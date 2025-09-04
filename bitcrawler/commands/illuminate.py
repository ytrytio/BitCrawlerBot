from aiogram.types import Message
from typing import Any
from bitcrawler.utils import bq, database
import aiosqlite

@database
async def illuminate(message: Message, db: aiosqlite.Connection, **kwargs: Any):
    if not message.chat or not message.from_user: return

    if not message.reply_to_message:
        await message.reply(bq("Команда пишется в ответ на сообщение."), parse_mode="HTML")
        return

    user_id = message.reply_to_message.from_user.id # type: ignore
    first_name = message.reply_to_message.from_user.first_name # type: ignore
    username = message.reply_to_message.from_user.username or "" # type: ignore

    cursor = await db.execute(
        "INSERT OR IGNORE INTO whitelist (id, username) VALUES (?, ?)",
        (user_id, username)
    )
    await db.commit()

    text = None

    if cursor.rowcount == 0:
        text = bq("Whitelist") + "\n" + bq("Запись уже существует:", first_name)
    else:
        text = bq("Whitelist") + "\n" + bq("Запись добавлена:", first_name)

    await message.reply(text, parse_mode="HTML")
