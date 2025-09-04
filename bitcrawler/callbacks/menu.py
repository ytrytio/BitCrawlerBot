from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from bitcrawler.utils.utils import bq


async def menu(callback: CallbackQuery):
    if not callback.message or not callback.message.chat or not callback.from_user: return
    if not isinstance(callback.message, Message): return
    if callback.message.chat.type != "private":
        await callback.answer("Доступно только в личных сообщениях.")
        return

    await callback.message.edit_text(
        bq("Главное меню"),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Мои зеркала", callback_data="my_mirrors")],
            ]
        )
    )
