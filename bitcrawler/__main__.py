import asyncio
from typing import List, Any
from logging import Logger
from aiogram import Bot
from aiogram.exceptions import TelegramUnauthorizedError
from telethon.tl.types import User # type: ignore
from telethon.errors import SessionPasswordNeededError # type: ignore
from bitcrawler.core.bot import create_main_bot
from bitcrawler.core.mirror import Mirror
from bitcrawler.utils import init_db, setup_logger, LogColors
from bitcrawler.config import SESSION, PHONE, API_ID, API_HASH
from bitcrawler.signals import restart_event
from bitcrawler.storage.sqlitestorage import SQLiteStorage
from bitcrawler.userbot.client import client

logger: Logger = setup_logger()

async def collect_bots() -> tuple[List[Bot], Any, SQLiteStorage]:
    storage = SQLiteStorage()
    await storage.connect()

    bots: List[Bot] = []

    main_bot, main_dp = await create_main_bot(storage=storage)
    bots.append(main_bot)

    mirrors = await Mirror.get_all_active()
    for mirror in mirrors:
        try:
            bot = await mirror.get_bot()
            await bot.get_me()
            bots.append(bot)
            logger.info(f"Mirror #{mirror.id} prepared.")
        except TelegramUnauthorizedError:
            logger.error(f"Mirror #{mirror.id} token invalid, deleting...")
            await mirror.delete()

    return bots, main_dp, storage



async def polling_loop() -> None:
    while True:
        bots, dp, storage = await collect_bots()
        logger.info(f"Starting polling for {len(bots)} bots...")

        polling_task = asyncio.create_task(dp.start_polling(*bots))  # type: ignore
        restart_task = asyncio.create_task(restart_event.wait())

        done, _ = await asyncio.wait(
            [polling_task, restart_task],
            return_when=asyncio.FIRST_COMPLETED
        )

        if polling_task in done:
            logger.info("Polling finished normally.")
            restart_task.cancel()
            await storage.close()
            break

        if restart_task in done:
            logger.warning("Restart requested. Stopping polling...")
            await dp.stop_polling()
            restart_event.clear()
            await asyncio.gather(polling_task, return_exceptions=True)
            restart_task.cancel()
            await storage.close()
            logger.info("Restarting polling...")


async def main() -> None:
    try:
        if API_ID and API_HASH and PHONE:
            if not client.is_connected():
                await client.connect()
            info = await client.get_me()
            if info:
                logger.info(f"User is already authorized: {info.id if isinstance(info, User) else info.user_id}")
            else:
                logger.info(f"User is not authorized, starting login process...")
                await client.send_code_request(PHONE)
                code = input(f"{LogColors.CYAN}[INPUT] Введите код, отправленный на ваш номер телефона: {LogColors.RESET}")

                try:
                    await client.sign_in(PHONE, code=code)
                except SessionPasswordNeededError:
                    logger.info(f"Two-factor authentication password required.")
                    password = input(f"{LogColors.CYAN}[INPUT] Введите пароль для двухфакторной аутентификации: {LogColors.RESET}")
                    await client.sign_in(password=password)

                info = await client.get_me()
                if not info:
                    logger.error("Unable to retrieve user data after login.")
                    raise RuntimeError("Unable to retrieve user data after login.")

            if isinstance(info, User):
                user_id = info.id
            else:
                user_id = getattr(info, "user_id", None)

            if user_id is None:
                logger.error(f"Unable to determine user_id.")
                raise RuntimeError("Unable to determine user_id.")

            logger.info(f"Successfully connected to user account {user_id}.")

            if isinstance(info, User):
                user_id = info.id
            else:
                user_id = getattr(info, "user_id", None)

            if user_id is None:
                raise RuntimeError("Unable to get user_id.")

            logger.info(f"Connected to user account {user_id}.")
        else:
            logger.info(f"Userbot login was skipped.")

        await init_db()
        await polling_loop()

        if SESSION:
            try:
                await SESSION.close()
            except Exception as e:
                logger.error(f"Error closing global SESSION: {e}")

    except Exception as e:
        logger.error(f"{LogColors.RED}Ошибка авторизации: {e}{LogColors.RESET}")
        raise
    finally:
        if client.is_connected():
            await client.disconnect() # type: ignore
            logger.info(f"{LogColors.YELLOW}Соединение с Telegram закрыто{LogColors.RESET}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("KeyboardInterrupt received, shutting down")
