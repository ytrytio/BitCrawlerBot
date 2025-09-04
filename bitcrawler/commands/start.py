from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from bitcrawler.utils.utils import bq


async def start(message: Message):
    await message.reply(
        bq("Добро пожаловать в BitCrawler!"),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Главное меню", callback_data="menu")]
            ]
        )
    )
