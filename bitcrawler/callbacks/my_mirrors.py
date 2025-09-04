from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from bitcrawler.core.mirror import Mirror
from bitcrawler.utils import bq
from typing import List

async def my_mirrors(callback: CallbackQuery):
    if not callback.message or not callback.message.chat or not callback.from_user: return
    if not isinstance(callback.message, Message): return

    user_id = callback.from_user.id
    mirrors_list = await Mirror.get_by_owner(owner_id=user_id)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Создать зеркало", callback_data="new_mirror")],
            [InlineKeyboardButton(text="Назад", callback_data="menu")],
        ]
    )

    if not mirrors_list:
        await callback.message.edit_text(
            bq("У вас отсутствуют зеркала."),
            parse_mode="HTML",
            reply_markup=keyboard
        )
        return

    text_lines: List[str] = []
    for mirror in mirrors_list:
        status = "Активно" if mirror.is_active else "Неактивно"
        text_lines.append(bq(f"{mirror.name or 'Mirror #' + str(mirror.id)}: ", f"{status}"))

    text = "\n".join(text_lines)

    await callback.message.edit_text(
        bq("Список ваших зеркал:") + f"\n\n{text}",
        parse_mode="HTML",
        reply_markup=keyboard
    )
