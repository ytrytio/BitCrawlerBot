from aiogram.types import Message
from bitcrawler.utils.utils import bq

async def ping(message: Message):
    user_date = message.date
    ping_msg = await message.reply(
        bq("Пинг..."),
        parse_mode="HTML"
    )
    bot_date = ping_msg.date
    delta_ms = (bot_date - user_date).total_seconds() * 1000

    await ping_msg.edit_text(
        bq("Пинг... ") + bq("Понг!") + "\n" +
        bq("Задержка:", f"{delta_ms:.1f}ms"),
        parse_mode="HTML"
    )
