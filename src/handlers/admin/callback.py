import asyncio
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, FSInputFile

import time
import psutil

from pathlib import Path
from loguru import logger
from datetime import date

from core.config import settings
from core.db import db
from core.redis import get_redis

from crud import get_total_users, get_new_users_today, get_all_card_backs, delete_card_back, reset_daily_card_limit, get_active_users_today
from filters.check_admin import IsAdmin
from keyboards.admin import get_admin_keyboard, get_cancel_keyboard, get_delete_back_keyboard

router = Router()

# ==================== FSM состояния ====================

class AdminStates(StatesGroup):
    """Состояния для админ-действий"""
    waiting_for_photo = State()
    waiting_for_save_back = State()

# ==================== Callback handlers ====================

@router.callback_query(F.data == "admin:get_file_id", IsAdmin())
async def get_photo_id_start(callback: CallbackQuery, state: FSMContext):
    """Начало получения file_id"""
    await state.set_state(AdminStates.waiting_for_photo)
    await callback.message.answer(
        "📸 Отправьте фото, чтобы получить его file_id\n\n"
        "После отправки фото вы получите его file_id",
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "admin:save_card_back", IsAdmin())
async def save_card_back_start(callback: CallbackQuery, state: FSMContext):
    """Начало сохранения рубашки"""
    await state.set_state(AdminStates.waiting_for_save_back)
    await callback.message.answer(
        "🃏 Отправьте фото для новой рубашки карт\n\n"
        "После отправки фото рубашка будет сохранена",
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "admin:view_card_back", IsAdmin())
async def view_card_backs(callback: CallbackQuery):
    """Показать все рубашки"""
    backs = await get_all_card_backs()

    if not backs:
        await callback.message.answer("❌ Рубашек пока нет")
        await callback.answer()
        return

    for back in backs:
        await callback.message.answer_photo(
            back[1],
            caption=f"🃏 Рубашка ID: {back[0]}",
            reply_markup=get_delete_back_keyboard(back[0])
        )
    await callback.answer()

@router.callback_query(F.data.startswith("admin:del_back:"), IsAdmin())
async def del_back(callback: CallbackQuery):
    """Удалить рубашку"""
    back_id = int(callback.data.split(":")[2])
    await delete_card_back(back_id)
    await callback.message.edit_caption(caption="✅ Рубашка удалена")
    await callback.answer()

@router.callback_query(F.data == "admin:cancel", IsAdmin())
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    """Отмена текущего действия"""
    await state.clear()
    await callback.message.edit_text(
        "❌ Действие отменено",
        reply_markup=get_admin_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "admin:exit", IsAdmin())
async def exit_admin_panel(callback: CallbackQuery, state: FSMContext):
    """Выход из админ-панели"""
    await state.clear()
    await callback.message.delete()
    await callback.message.answer(
        "👋 Вы вышли из админ-панели\n"
        "Для входа используйте /admin"
    )
    await callback.answer()

@router.callback_query(F.data == "admin:backup", IsAdmin())
async def admin_backup(callback: CallbackQuery):
    """Асинхронный бэкап базы данных с защитой от повторного запуска."""
    redis = get_redis()

    # ========== Проверяем блокировку ==========
    lock_key = "backup:lock"
    if await redis.get(lock_key):
        await callback.answer("❌ Бэкап уже выполняется!", show_alert=True)
        return

    await redis.set(lock_key, "1", ttl=60)

    await callback.answer("⏳ Создаю бэкап...")
    msg = await callback.message.answer("🔄 Запускаю бэкап базы данных...")
    logger.info(f"Admin {callback.from_user.id} requested backup")

    backup_file = Path("/tmp/tarot_backup.sql.gz")

    # ========== Асинхронный вызов pg_dump ==========

    cmd = f"{settings.pg_dump_cmd} | gzip > /tmp/tarot_backup.sql.gz"

    try:
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            error_msg = stderr.decode() if stderr else "Unknown error"
            logger.error(f"Backup failed: {error_msg}")
            await msg.edit_text(f"❌ Ошибка создания бэкапа:\n{error_msg[:200]}")
            return

        if not backup_file.exists() or backup_file.stat().st_size == 0:
            logger.error("Backup file empty or missing")
            await msg.edit_text("❌ Файл бэкапа пуст")
            return

        # ========== Отправляем файл ==========

        await msg.edit_text("✅ Бэкап готов, отправляю файл...")

        await callback.message.answer_document(
            FSInputFile(backup_file),
            caption=f"✅ Бэкап готов\n📦 Размер: {backup_file.stat().st_size // 1024} КБ"
        )

        await msg.delete()
        logger.info(f"Backup completed successfully, size: {backup_file.stat().st_size} bytes")

    except Exception as e:
        logger.error(f"Backup failed: {e}")
        await msg.edit_text(f"❌ Ошибка: {str(e)[:200]}")

    finally:
        backup_file.unlink(missing_ok=True)
        await redis.delete(lock_key)

@router.callback_query(F.data == "admin:errors", IsAdmin())
async def admin_errors(callback: CallbackQuery):
    """Показать последние ошибки из лога"""
    await callback.answer()

    today = date.today().isoformat()
    logs_dir = Path(__file__).parent.parent.parent.parent / "logs"
    errors_file = logs_dir / f"errors_{today}.log"

    if not errors_file.exists():
        await callback.message.answer("✅ Ошибок сегодня нет")
        return

    with open(errors_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    if not lines:
        await callback.message.answer("✅ Ошибок сегодня нет")
        return

    last_error = lines[-10:]
    text = "🔴 **Последние ошибки:**\n\n" + "".join(last_error)

    if len(text) > 4000:
        text = text[:4000] + "\n\n..."

    await callback.message.answer(text[:4000])


@router.callback_query(F.data == "admin:status", IsAdmin())
async def admin_status(callback: CallbackQuery):
    await callback.answer()

    redis = get_redis()

    total_users = await get_total_users()
    new_today = await get_new_users_today()
    active_today = await get_active_users_today()

    memory = psutil.virtual_memory()
    mem_used_mb = memory.used // (1024 * 1024)
    mem_total_mb = memory.total // (1024 * 1024)

    bot_uptime = int(time.time() - psutil.Process().create_time())
    hours = bot_uptime // 3600
    minutes = (bot_uptime % 3600) // 60
    uptime_str = f"{hours}ч {minutes}м"

    try:
        redis_ping = await redis.ping()
        redis_status = "✅" if redis_ping else "❌"
    except:
        redis_status = "❌"

    try:
        await db.fetchone("SELECT 1")
        db_status = "✅"
    except:
        db_status = "❌"

    text = f"""
📊 СТАТУС БОТА

👥 Пользователи
• Всего: {total_users}
• Сегодня: {new_today}
• Активных: {active_today}

💾 Система
• ОЗУ: {mem_used_mb} / {mem_total_mb} МБ ({memory.percent}%)
• Аптайм: {uptime_str}

🔴 Redis: {redis_status}
🗄️ PostgreSQL: {db_status}
"""
    await callback.message.answer(text)

@router.callback_query(F.data == "admin:reset_daily_card", IsAdmin())
async def reset_daily_card(callback: CallbackQuery):
    """Сбросить лимит карты дня для админа."""
    await reset_daily_card_limit(callback.from_user.id)
    await callback.answer("✅ Лимит сброшен")

@router.callback_query(F.data == "admin:clear_ai_cache", IsAdmin())
async def clear_ai_cache(callback: CallbackQuery):
    redis_client = get_redis()
    if not redis_client:
        await callback.answer("❌ Redis недоступен", show_alert=True)
        return

    deleted = await redis_client.invalidate_oracle_cache()
    await callback.message.answer(f"✅ Кэш очищен. Удалено: {deleted}")
    await callback.answer()

def register_handlers():
    """Регистрируем обработчики колбэков админа"""
    pass
