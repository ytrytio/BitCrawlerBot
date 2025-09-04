from typing import Tuple
from bitcrawler.handlers import get_routers
from bitcrawler.storage import SQLiteStorage
from bitcrawler.utils import setup_logger
from bitcrawler.config import SESSION, BOT_TOKEN
from aiogram import Bot, Dispatcher


logger = setup_logger()

async def create_main_bot(storage: SQLiteStorage) -> Tuple[Bot, Dispatcher]:
    bot = Bot(token=BOT_TOKEN, session=SESSION)
    dp = Dispatcher(name="Main", storage=storage)
    dp.include_routers(*get_routers("main"))
    await bot.delete_webhook(drop_pending_updates=True)
    return bot, dp
