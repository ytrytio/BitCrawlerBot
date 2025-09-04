import asyncio
import sys
import os

restart_event = asyncio.Event()

async def restart_process():
    await asyncio.sleep(2)
    os.execvpe("uv", ["uv", "run", "python", "-m", "bitcrawler"], os.environ)
