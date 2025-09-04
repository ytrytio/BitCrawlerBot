from dotenv import dotenv_values
from typing import Dict, Tuple
from bitcrawler.handlers import get_routers
from bitcrawler.storage import SQLiteStorage
from bitcrawler.utils import setup_logger
from bitcrawler.config import SESSION
from aiogram import Bot, Dispatcher

secrets: Dict[str, str | None] = dotenv_values('.env')
BOT_TOKEN: str = secrets["BOT_TOKEN"] or ""

logger = setup_logger()

async def create_main_bot(storage: SQLiteStorage) -> Tuple[Bot, Dispatcher]:
    bot = Bot(token=BOT_TOKEN, session=SESSION)
    dp = Dispatcher(name="Main", storage=storage)
    dp.include_routers(*get_routers("main"))
    await bot.delete_webhook(drop_pending_updates=True)
    return bot, dp
