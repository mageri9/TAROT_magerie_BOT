import asyncio
import html

from aiogram import F, Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

import services as srv
from core.config import settings
from core.redis import get_redis
from crud import get_user_stats
from keyboards.user import card_of_the_day, open_card_button


class CardContextState(StatesGroup):
    waiting_for_context = State()


router = Router()


@router.message(CommandStart())
async def start_handler(message: Message):
    """Обработчик команды старт"""
    await srv.register_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
    )
    await message.answer(
        f"<b>{html.escape(message.from_user.full_name)}</b>, добро пожаловать!\n"
        f"Я бот-предсказатель.\n"
        f"Вам доступна ✨ КАРТА ДНЯ ✨",
        reply_markup=card_of_the_day(),
    )


@router.message(F.text == "🔮 КАРТА ДНЯ 🔮")
async def card_of_day(message: types.Message, state: FSMContext):
    """Обработчик кнопки '🔮 КАРТА ДНЯ 🔮'"""
    user_id = message.from_user.id

    card_id, card_back = await srv.give_daily_card(user_id)

    if not card_back:
        await message.answer("Вы уже получали карту сегодня.\nПриходите завтра!")
        return

    await state.update_data(card_id=card_id)

    await message.answer_photo(
        card_back,
        caption="✨ Напиши в чат, что тебя волнует. Оракул увидит это.",
        reply_markup=open_card_button(card_id),
    )

    await state.set_state(CardContextState.waiting_for_context)


@router.message(F.text == "📜 ПРОФИЛЬ 📜")
async def profile(message: Message):
    """Статистика пользователя (кнопка)"""
    user_id = message.from_user.id
    stats = await get_user_stats(user_id)

    if not stats or stats[0] == 0:
        await message.answer("🔮 Откройте одну карту.")
        return

    total, upright, reversed_ = stats

    text = f"""

    📜 Всего: {total}/156

    🃏: {upright}
    🎴: {reversed_}

            """
    await message.answer(text)


@router.message(F.text == "❓ ПОМОЩЬ ❓")
async def help_command(message: Message):
    await message.answer(
        "🔮 Что я умею:\n"
        "• Открой карту, чтобы узнать значение.\n"
        "• Обратись к Оракулу.\n"
        "• У тебя есть шанс испытать удачу повторно.\n"
        "• Статистика — кнопка ПРОФИЛЬ.\n"
        "• Новая карта каждый день!\n\n"
        "📜 Если что-то сломалось — напиши @mageri9"
    )


@router.message(CardContextState.waiting_for_context)
async def process_context(message: types.Message, state: FSMContext):
    redis_client = get_redis()

    if not redis_client:
        await message.answer("❌ Redis недоступен, попробуй позже")
        return

    user_id = message.from_user.id
    context = message.text.strip()

    if not context:
        await message.answer("✨ Напиши мысль или вопрос, который тебя волнует.")
        return

    if len(context) > settings.CONTEXT_MAX_LENGTH:
        last_space = context.rfind(" ", 0, 200)
        if last_space > 0:
            context = context[:last_space] + "..."
        else:
            context = context[:200] + "..."

    await redis_client.set(f"context:{user_id}", context, ttl=settings.CONTEXT_TTL)

    try:
        await message.delete()
    except Exception:
        pass

    msg = await message.answer("✨ Оракул услышал. ✨")
    await asyncio.sleep(2)
    try:
        await msg.delete()
    except Exception:
        pass


def register_handlers():
    pass
