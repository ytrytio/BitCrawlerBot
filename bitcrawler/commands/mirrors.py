from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from bitcrawler.core.mirror import Mirror
from bitcrawler.utils import bq
from typing import List

async def mirrors(message: Message):
    if not message.chat or not message.from_user:
        return

    user_id = message.from_user.id
    mirrors_list = await Mirror.get_by_owner(owner_id=user_id)

    if not mirrors_list:
        await message.reply(
            bq("У вас отсутствуют зеркала."),
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="Создать зеркало", callback_data="new_mirror")]]
            )
        )
        return

    text_lines: List[str] = []
    for mirror in mirrors_list:
        status = "Активно" if mirror.is_active else "Неактивно"
        text_lines.append(bq(f"{mirror.name or 'Mirror #' + str(mirror.id)}: ", f"{status}"))

    text = "\n".join(text_lines)

    await message.reply(
        bq("Список ваших зеркал:") + f"\n\n{text}",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Создать зеркало", callback_data="new_mirror")]]
        )
    )
