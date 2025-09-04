import asyncio
from typing import List, Any
from logging import Logger
from aiogram import Bot
from bitcrawler.core.bot import create_main_bot
from bitcrawler.core.mirror import Mirror
from bitcrawler.utils import init_db, setup_logger
from bitcrawler.config import SESSION
from bitcrawler.signals import restart_event
from bitcrawler.storage.sqlitestorage import SQLiteStorage

logger: Logger = setup_logger()


async def collect_bots() -> tuple[List[Bot], Any, SQLiteStorage]:
    storage = SQLiteStorage()
    await storage.connect()

    bots: List[Bot] = []

    main_bot, main_dp = await create_main_bot(storage=storage)
    bots.append(main_bot)

    mirrors = await Mirror.get_all_active()
    for mirror in mirrors:
        bot = await mirror.get_bot()
        bots.append(bot)
        logger.info(f"Mirror #{mirror.id} prepared.")

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
    await init_db()
    await polling_loop()

    if SESSION:
        try:
            await SESSION.close()
        except Exception as e:
            logger.error(f"Error closing global SESSION: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("KeyboardInterrupt received, shutting down")
