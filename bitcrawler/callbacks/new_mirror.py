from typing import Any
from json import dumps, loads
from aiogram import Bot
from aiogram.types import CallbackQuery, Message, InaccessibleMessage
from aiogram.exceptions import TelegramUnauthorizedError
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bitcrawler.utils import database, aiosqlite, bq
from bitcrawler.core import Mirror
from bitcrawler.utils import setup_logger, get_encrypt_name
from bitcrawler.signals import restart_event

logger = setup_logger()

class EnterToken(StatesGroup):
    token = State()

@database
async def new_mirror(callback: CallbackQuery, db: aiosqlite.Connection, state: FSMContext, bot: Bot, **kwargs: Any):
    message = callback.message
    if not message or not isinstance(message, Message) or not message.reply_to_message or not callback.data: return
    if message.chat.type != "private":
        await callback.answer("Доступно только в личных сообщениях.")
        return

    await message.edit_text(
        bq("Введитие токен, полученный от @BotFather, в ответ на это сообщение."),
        parse_mode="HTML"
    )
    await state.set_state(EnterToken.token)
    await state.update_data(
        call_message=dumps(message.model_dump()),
        attempt=1
    )

@database
async def enter_token(message: Message, db: aiosqlite.Connection, state: FSMContext, bot: Bot, **kwargs: Any) -> Any:
    if not message or not message.from_user or not message.reply_to_message: return
    if isinstance(message, InaccessibleMessage): return

    data = await state.get_data()
    call_msg = Message.model_validate(loads(data["call_message"]))
    attempt = data["attempt"] or 1
    if message.reply_to_message.message_id != call_msg.message_id: return

    token = message.text or ""

    try:
        test_bot = Bot(token=token)
        me = await test_bot.get_me()
        botname = me.username
        await test_bot.set_my_name(get_encrypt_name(me.id))
    except TelegramUnauthorizedError as e:
        await call_msg.edit_text(
            bq(f"Попытка {attempt}") + "\n" +
            bq("Неверный токен, попробуйте ещё раз."),
            parse_mode="HTML"
        ).as_(bot)
        logger.error(e)
        return
    except Exception as e:
        await call_msg.edit_text(
            bq("Попытка создать зеркало:", f"{attempt}") + "\n" +
            bq(f"Неизвестная ошибка, попробуйте ещё раз."),
            parse_mode="HTML"
        ).as_(bot)
        logger.error(e)
        return
    finally:
        await state.update_data(
            call_message=dumps(call_msg.model_dump()),
            attempt=attempt + 1
        )

    mirror = await Mirror.create(name=botname, owner_id=message.from_user.id, token=token)

    await call_msg.edit_text(
        bq("Токен принят.") + "\n" +
        bq(f"Новое зеркало @{mirror.name} успешно создано."),
        parse_mode="HTML"
    ).as_(bot)

    await state.clear()
    restart_event.set()
