from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bitcrawler.utils import add_database
from pathlib import Path
from typing import Dict
from dotenv import dotenv_values

secrets: Dict[str, str | None] = dotenv_values('.env')
SOURCE_CHAT_ID = secrets["SOURCE_CHAT_ID"]
SOURCE_TOPIC_ID = secrets["SOURCE_TOPIC_ID"]

async def on_archive(message: Message):
    if not message.document: return

    file_name = message.document.file_name or " "
    file_ext = Path(file_name).suffix.lower()

    archive_type = {
        ".zip": "ZIP",
        ".rar": "RAR",
        ".7z": "7-ZIP",
        ".tar": "TAR",
        ".gz": "GZIP",
    }.get(file_ext, "Unknown")

    db_id = await add_database(
        name=message.document.file_name,
        format=archive_type
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📥 Скачать",
                    callback_data=f"add_{db_id}"
                )
            ]
        ]
    )

    await message.reply(
        f"🗃 <b>Обнаружен новый архив!</b>\n<b>Формат</b>: <i>{archive_type}</i>\n\n<i>Может потребоваться пароль.</i>",
        parse_mode="HTML",
        reply_markup=keyboard
    )
