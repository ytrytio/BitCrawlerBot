from aiogram.types import Message
from bitcrawler.utils.utils import bq


async def start(message: Message):
    await message.reply(
        bq("Добро пожаловать в BitCrawler!"),
        parse_mode="HTML"
    )
