from aiogram import Router, F
from aiogram.types import CallbackQuery, InputMediaPhoto

from keyboards.user import open_card_button

router = Router()

@router.callback_query(F.data == "open_card")
async def open_card(callback: CallbackQuery):
    """Открыть карту"""
    file_id = "AgACAgIAAxkBAAIBWGnC57oMd7h3yHrCBTQl6R9H9J_2AAIeF2sbOq8YSlmzmF12KUpRAQADAgADeQADOgQ"
    await callback.message.edit_media(
        InputMediaPhoto(
            media=file_id,
            caption="✨ Ваша карта! ✨",
            reply_markup=open_card_button()
        )
    )




@router.callback_query(F.data == "cancel")
async def cancel_handler(query: CallbackQuery):
    await query.message.edit_text('Operation canceled')


def register_handlers():
    pass
