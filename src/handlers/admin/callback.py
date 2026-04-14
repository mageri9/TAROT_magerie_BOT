from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, FSInputFile

import time
import psutil
import subprocess
from pathlib import Path
from loguru import logger
from datetime import date

from core.db import db
from core import redis

from crud import get_total_users, get_new_users_today, get_all_card_backs, delete_card_back
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
    """Ручной бэкап базы данных."""
    await callback.answer("⏳ Создаю бэкап...")
    logger.info(f"Admin {callback.from_user.id} requested backup")

    backup_file = Path("/tmp/tarot_backup.sql.gz")

    cmd = (
        f"docker exec tarot_magerie_bot-postgres-1 "
        f"pg_dump -U bot_user tarot_bot | gzip > {backup_file}"
    )
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        logger.error(f"Backup failed: {result.stderr}")
        await callback.message.answer("❌ Ошибка создания бэкапа")
        return

    if not backup_file.exists() or backup_file.stat().st_size == 0:
        logger.error("Backup file empty or missing")
        await callback.message.answer("❌ Файл бэкапа пуст")
        return

    await callback.message.answer_document(
        FSInputFile(backup_file),
        caption="✅ Бэкап готов"
    )
    backup_file.unlink(missing_ok=True)

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
    """Показать статус бота и системы."""
    await callback.answer()

# 1. Пользователи
    total_users = await get_total_users()
    total_users = total_users[0] if total_users else 0

    new_today = await get_new_users_today()
    new_today = new_today[0] if new_today else 0

# 2. Система
    memory = psutil.virtual_memory()
    mem_used_mb = memory.used // (1024 * 1024)
    mem_total_mb = memory.total // (1024 * 1024)
    mem_percent = memory.percent

    bot_uptime = int(time.time() - psutil.Process().create_time())
    hours = bot_uptime // 3600
    minutes = (bot_uptime % 3600) // 60
    uptime_str = f"{hours}ч {minutes}м"

# 3. Статус сервисов
    redis_status = "✅" if await redis.redis_client.ping() else "❌"
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

💾 Система
• ОЗУ: {mem_used_mb} / {mem_total_mb} МБ ({mem_percent}%)
• Аптайм: {uptime_str}

🔴 Redis: {redis_status}
🗄️ PostgreSQL: {db_status}
"""

    await callback.message.answer(text)

def register_handlers():
    """Регистрируем обработчики колбэков админа"""
    pass
