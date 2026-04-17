import asyncio
from openai import AsyncOpenAI
from loguru import logger

from core.config import settings


client = AsyncOpenAI(
    base_url="https://api.aitunnel.ru/v1/",
    api_key=settings.AITUNNEL_API_KEY,
    default_headers={
        "HTTP-Referer": "https://t.me/tarot_magerie_test_bot",
        "X-Title": "Tarot Magerie Bot"
    }
)

DEFAULT_MODEL = "gemma-4-26b-a4b-it"

async def ask_oracle(card_name: str, is_reversed: bool = False, model: str = DEFAULT_MODEL) -> str:
    """
    Спросить у AI-таролога о значении карты.
"""

    if is_reversed:
        position_text = "в перевёрнутом положении"
        tone = "Толкование должно быть более мрачным, предупреждающим или указывать на препятствия и внутренние блоки."
        question_type = "о сложностях, страхах или о том, что человек пытается игнорировать."
    else:
        position_text = "в прямом положении"
        tone = "Толкование должно быть светлым, вдохновляющим и давать ощущение поддержки."
        question_type = "о возможностях, росте или о том, к чему стоит стремиться."

        # 2. Улучшенный промпт, который учит модель разнообразию
    prompt = (
        f"Ты — таролог. Пользователю выпала карта «{card_name}» {position_text}. "
        f"{tone} "
        f"Дай краткое (1-2 предложения) и полезное толкование на сегодня, строго соответствующее положению карты. "
        f"Пиши простым, человеческим языком, без излишней поэзии и метафор. "
        f"В конце задай ОДИН короткий, но глубокий вопрос {question_type} "
        f"Вопрос должен быть уникальным для этой карты и её положения. Не используй markdown."
    )

    try:
        logger.info(f"🤖 Asking Oracle about: {card_name} ({position_text})")

        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            max_tokens=400,
            timeout=15.0
        )


        answer = response.choices[0].message.content

        if not answer:
            logger.warning(f"Empty response from {model}")
            return "🔮 Оракул сегодня немногословен. Попробуй другую карту."

        logger.info(f"✨ Oracle answered: {answer[:50]}...")
        return answer.strip()

    except asyncio.TimeoutError:
        logger.error("⏱️ Oracle timeout")
        return "✨ Сегодня звезды медлят с ответом... Попробуй позже. ✨"


    except Exception as e:
        logger.error(f"❌ Oracle error: {e}")

        if "429" in str(e):
            return "🔮 Сегодня было много вопросов к звёздам. Дай отдохнуть и спроси снова."

        elif "401" in str(e):
            return "🔮 Оракул временно не может связаться с высшими силами. Мы работаем над этим."

        else:
            return "🔮 Оракул временно недоступен. Карты говорят, что всё наладится. 😉"