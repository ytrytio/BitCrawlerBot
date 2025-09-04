import asyncio
import os
from bitcrawler.config import PROJECT_DIR

restart_event = asyncio.Event()


async def restart_process():
    await asyncio.sleep(2)
    os.chdir(PROJECT_DIR)
    os.execvpe(
        "uv",
        ["uv", "run", "python", "-m", "bitcrawler"],
        os.environ
    )
