import time
from aiogram.types import Message
from bitcrawler.utils.utils import bq

async def ping(message: Message):
    start = time.perf_counter()
    sent_msg = await message.reply(
        bq("Пинг..."),
        parse_mode="HTML"
    )
    end = time.perf_counter()

    delta_ms = (end - start) * 1000

    await sent_msg.edit_text(
        bq("Пинг... Понг!") + "\n" +
        bq("Задержка:", f"{delta_ms:.1f}ms"),
        parse_mode="HTML"
    )
