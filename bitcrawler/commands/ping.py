from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from bitcrawler.utils.utils import bq

async def ping(message: Message):
    user_date = message.date
    ping_msg = await message.reply(
        bq("Пинг..."),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Главное меню", callback_data="menu")]
            ]
        )
    )
    bot_date = ping_msg.date
    delta_seconds = (bot_date - user_date).total_seconds()
    delta_ms = int(delta_seconds * 1000)

    await ping_msg.edit_text(
        bq("Пинг... ") + bq("Понг!") + "\n" +
        bq("Задержка:", f"{delta_ms}ms"),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Главное меню", callback_data="menu")]
            ]
        )
    )
