from dotenv import dotenv_values
from typing import Any, Dict
from bitcrawler.handlers import routers
from bitcrawler.utils import init_db, setup_logger

from aiogram import Bot, Dispatcher

secrets: Dict[str, str | None] = dotenv_values('.env')
BOT_TOKEN: str = secrets["BOT_TOKEN"] or ""

logger = setup_logger()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.include_routers(*routers)

async def main() -> Any:
    await init_db()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot) # type: ignore
