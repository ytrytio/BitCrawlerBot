from aiogram import Bot
from aiogram.types import CallbackQuery, Message, InaccessibleMessage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bitcrawler.utils import database, aiosqlite, Archive, bq
from bitcrawler.config import DATABASES_FOLDER
from pathlib import Path
from typing import Any
from json import dumps, loads

class EnterPassword(StatesGroup):
    password = State()

@database
async def add(callback: CallbackQuery, db: aiosqlite.Connection, state: FSMContext, bot: Bot, **kwargs: Any):
    message = callback.message
    if not message or not isinstance(message, Message) or not message.reply_to_message or not callback.data: return

    document = message.reply_to_message.document

    if document:
        await message.edit_text(
            bq("Запрос принят.")+"\n"+
            bq("Загрузка архива...")+"\n",
            parse_mode="HTML"
        )
        file = await bot.get_file(document.file_id)
        file_path = file.file_path
        file_name = document.file_name or "archive"
        ARCHIVE_PATH = DATABASES_FOLDER / file_name
        if not file_path: return

        await bot.download_file(file_path, ARCHIVE_PATH)
        await message.edit_text(
            bq("Запрос принят.")+"\n"+
            bq("Архив загружен.")+"\n"+
            bq("Распаковка...")+"\n\n"+
            bq("Введите пароль к архиву в ответ на это сообщение.", "\n#empty - если пароль не нужен."),
            parse_mode="HTML"
        )
        await state.set_state(EnterPassword.password)
        await state.update_data(
            call_message=dumps(message.model_dump()),
            path=str(ARCHIVE_PATH),
            archive_id=str(callback.data.split("_")[1])
        )
    else:
        await callback.answer("Архив не найден.")


@database
async def enter_pass(message: Message, db: aiosqlite.Connection, state: FSMContext, bot: Bot, **kwargs: Any) -> Any:
    if not message or not message.from_user or not message.reply_to_message: return
    if isinstance(message, InaccessibleMessage): return

    data = await state.get_data()
    call_msg = Message.model_validate(loads(data["call_message"]))
    ARCHIVE_PATH = Path(data["path"])

    if message.reply_to_message.message_id != call_msg.message_id: return

    password = message.text if message.text != "#empty" else None

    await call_msg.edit_text(
        bq("Запрос принят.")+"\n"+
        bq("Архив загружен.")+"\n"+
        bq("Пароль принят.")+"\n"+
        bq("Распаковка..."),
        parse_mode="HTML"
    ).as_(bot)

    archive = Archive(
        file_path=ARCHIVE_PATH,
        password=password
    )

    unpacked, returned = await archive.extract()

    if not unpacked:
        error = {
            "PR": "Password required",
            "IP": "Incorrect password",
        }.get(returned, "Unknown error") if returned else "Unknown error"

        await call_msg.edit_text(
            bq("Запрос принят.")+"\n"+
            bq("Архив загружен.")+"\n"+
            bq("Пароль принят.")+"\n"+
            bq("Не удалось распаковать архив.")+"\n"+
            bq(f"Причина:", f"{error}"),
            parse_mode="HTML"
        ).as_(bot)
    else:
        await call_msg.edit_text(
            bq("Запрос принят.")+"\n"+
            bq("Архив загружен.")+"\n"+
            bq("Пароль принят.")+"\n"+
            bq("Архив распакован.")+"\n"+
            bq("Готово!")+"\n\n"+
            bq("Формат распакованного файл:", f"{returned}"),
            parse_mode="HTML"
        ).as_(bot)

    await db.execute(
        "UPDATE databases SET format=? WHERE id=?",
        (returned, data["archive_id"])
    )
    await state.clear()
    await archive.delete()
