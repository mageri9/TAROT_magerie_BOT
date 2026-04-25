import asyncio
import hashlib

from loguru import logger
from openai import AsyncOpenAI

from core.config import settings

client = AsyncOpenAI(
    base_url="https://api.aitunnel.ru/v1/",
    api_key=settings.AITUNNEL_API_KEY,
    default_headers={
        "HTTP-Referer": "https://t.me/tarot_magerie_test_bot",
        "X-Title": "Tarot Magerie Bot",
    },
    max_retries=0,
    timeout=settings.AI_TIMEOUT,
)


# services/ai_service.py — модифицируем функцию ask_oracle


async def ask_oracle(
    card_name: str,
    is_reversed: bool = False,
    context: str = "",
    db_meaning: str = "",
    redis_client=None,
) -> str:
    """
    Спросить у AI-таролога о значении карты.

    - Проверяет кэш в Redis (если включен)
    - При промахе идёт в AI через Circuit Breaker + Fallback
    - Сохраняет успешный ответ в кэш
    """

    # ========== Проверяем кэш ==========
    if redis_client and settings.AI_CACHE_ENABLED:
        cached = await redis_client.get_cached_oracle_response(card_name, is_reversed, context)
        if cached:
            return cached  # Мгновенный ответ

    # ========== Формируем промпт ==========
    if is_reversed:
        position_text = "в перевёрнутом положении"
        tone = "Толкование должно быть более мрачным, предупреждающим или указывать на препятствия и внутренние блоки."
        question_type = "о сложностях, страхах или о том, что человек пытается игнорировать."
    else:
        position_text = "в прямом положении"
        tone = "Толкование должно быть светлым, вдохновляющим и давать ощущение поддержки."
        question_type = "о возможностях, росте или о том, к чему стоит стремиться."

    if len(context) > 200:
        context = context[:200] + "..."

    prompt = (
        f"Ты — таролог. Пользователю выпала карта «{card_name}» {position_text}. "
        f"{tone} "
        f"Официальное толкование карты: {db_meaning}. "
        f"Контекст от пользователя: {context}. "
        f"Дай краткое (1-2 предложения) и полезное толкование на сегодня. "
        f"Пиши простым, человеческим языком, c небольшой долей поэзии и метафор. "
        f"В конце задай ОДИН короткий, но глубокий вопрос {question_type} "
        f"Вопрос должен быть уникальным для этой карты и её положения. Не используй markdown."
    )

    # ==========  Определяем модели с учётом Circuit Breaker ==========
    models_to_try = []

    primary_open = False
    if redis_client:
        primary_open = await redis_client.is_circuit_open(settings.AI_PRIMARY_MODEL)

    if not primary_open:
        models_to_try.append(settings.AI_PRIMARY_MODEL)
    else:
        logger.warning(f"⚠️ Circuit breaker open for {settings.AI_PRIMARY_MODEL}, skipping")

    if settings.AI_FALLBACK_MODEL:
        fallback_open = False
        if redis_client:
            fallback_open = await redis_client.is_circuit_open(settings.AI_FALLBACK_MODEL)
        if not fallback_open:
            models_to_try.append(settings.AI_FALLBACK_MODEL)
        else:
            logger.warning(f"⚠️ Circuit breaker open for {settings.AI_FALLBACK_MODEL}, skipping")

    if not models_to_try:
        logger.error("❌ All models are disabled by circuit breaker")
        return "🔮 Звёзды просят немного терпения. Попробуй позже."

    # ========== Пробуем модели по очереди ==========
    last_error = None
    answer = None

    for attempt, model in enumerate(models_to_try):
        try:
            logger.info(f"🤖 Attempt {attempt + 1}/{len(models_to_try)}: using {model}")

            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=settings.AI_TEMPERATURE,
                max_tokens=settings.AI_MAX_TOKENS,
                timeout=settings.AI_TIMEOUT,
            )

            answer = response.choices[0].message.content

            # Логируем использование токенов
            if hasattr(response, "usage") and response.usage:
                logger.info(
                    f"📊 Tokens: prompt={response.usage.prompt_tokens}, "
                    f"completion={response.usage.completion_tokens}, "
                    f"total={response.usage.total_tokens}"
                )

            if not answer:
                raise ValueError("Empty response from model")

            answer = answer.strip()

            # ========== УСПЕХ ==========
            if attempt == 0 and model == settings.AI_PRIMARY_MODEL:
                logger.info(f"✅ Primary model {model} succeeded")
                if redis_client:
                    await redis_client.reset_circuit(model)
            elif attempt > 0:
                logger.warning(f"⚠️ Used fallback model: {model}")

            break

        except asyncio.TimeoutError:
            last_error = f"timeout after {settings.AI_TIMEOUT}s"
            logger.warning(f"⏱️ Model {model} {last_error}")

        except Exception as e:
            last_error = str(e)
            logger.error(f"❌ Model {model} failed: {type(e).__name__}: {e}")

            if "401" in str(e) or "403" in str(e):
                logger.error(f"🔐 Auth error for {model}, aborting fallback chain")
                break

        # ========== Записываем ошибку в Circuit Breaker ==========
        if redis_client:
            failures = await redis_client.record_failure(model)
            logger.warning(
                f"📊 Model {model} failures: {failures}/{settings.AI_CIRCUIT_BREAKER_THRESHOLD}"
            )

            if failures >= settings.AI_CIRCUIT_BREAKER_THRESHOLD:
                await redis_client.open_circuit(model)

    # ========== Если все попытки провалились ==========
    if answer is None:
        logger.error(f"❌ All models failed. Last error: {last_error}")
        return "🔮 Оракул сегодня немногословен... Попробуй позже."

    # ========== Сохраняем в кэш (только успешные ответы от AI) ==========
    if redis_client and settings.AI_CACHE_ENABLED:
        await redis_client.cache_oracle_response(card_name, is_reversed, context, answer)

    return answer


def _get_cache_key(card_name: str, is_reversed: bool, context: str) -> str:
    """Генерирует ключ для кэширования ответа AI."""
    data = f"{card_name},{is_reversed},{context}"
    hash_val = hashlib.md5(data.encode()).hexdigest()[:12]
    return f"oracle:cache:{hash_val}"
