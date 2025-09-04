from aiogram.types import Message
from typing import Any
from bitcrawler.utils import bq, database
from bitcrawler.config import SOURCE_CHAT_ID
import aiosqlite

@database
async def darken(message: Message, db: aiosqlite.Connection, **kwargs: Any):
    if not message.chat or not message.from_user: return
    if message.chat.id != SOURCE_CHAT_ID: return

    if not message.reply_to_message:
        await message.reply(bq("Команда пишется в ответ на сообщение."), parse_mode="HTML")
        return

    user_id = message.reply_to_message.from_user.id # type: ignore
    first_name = message.reply_to_message.from_user.first_name # type: ignore

    cursor = await db.execute(
        "DELETE FROM whitelist WHERE id = ?",
        (user_id,)
    )
    await db.commit()

    text = None

    if cursor.rowcount == 0:
        text = bq("Whitelist") + "\n" + bq("Запись не существует:", first_name)
    else:
        text = bq("Whitelist") + "\n" + bq("Запись удалена:", first_name)

    await message.reply(text, parse_mode="HTML")
