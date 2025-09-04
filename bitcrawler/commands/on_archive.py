from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bitcrawler.utils import add_database, bq
from bitcrawler.config import SOURCE_CHAT_ID, SOURCE_TOPIC_ID
from pathlib import Path


async def on_archive(message: Message):
    if not message.document or not message.chat: return
    if message.message_thread_id != SOURCE_TOPIC_ID: return
    if message.chat.id != SOURCE_CHAT_ID: return

    file_name = message.document.file_name or " "
    file_ext = Path(file_name).suffix.lower()

    archive_type = {
        ".zip": "ZIP",
        ".rar": "RAR",
        ".7z": "7-ZIP",
        ".tar": "TAR",
        ".gz": "GZIP",
    }.get(file_ext, "Unknown")

    if archive_type == "Unknown": return

    db_id = await add_database(
        name=message.document.file_name,
        format=archive_type
    )
    print(db_id)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Скачать",
                    callback_data=f"add_{db_id}"
                )
            ]
        ]
    )

    await message.reply(
        bq(f"Обнаружен новый архив!") + "\n" +
        bq("Формат:", f"{archive_type}") + "\n" +
        bq("Может потребоваться пароль."),
        parse_mode="HTML",
        reply_markup=keyboard
    )
