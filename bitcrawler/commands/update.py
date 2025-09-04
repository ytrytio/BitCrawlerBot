import subprocess
from aiogram.types import Message
from asyncio import create_task
from typing import List
from bitcrawler.signals import restart_process
from bitcrawler.config import SOURCE_CHAT_ID, PROJECT_DIR, CURRENT_BRANCH
from bitcrawler.utils import setup_logger, bq

logger = setup_logger()

async def update(message: Message):
    if message.chat.id != SOURCE_CHAT_ID: return

    output_lines: List[str] = []
    restart = False

    local_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=PROJECT_DIR,
        capture_output=True, text=True, check=True
    ).stdout.strip()
    output_lines.append(bq("Local SHA:", f"{local_sha}"))

    subprocess.run(["git", "fetch"], cwd=PROJECT_DIR, check=True)
    output_lines.append(bq("Git fetch выполнен."))

    remote_sha = subprocess.run(
        ["git", "rev-parse", f"origin/{CURRENT_BRANCH}"],
        cwd=PROJECT_DIR,
        capture_output=True, text=True, check=True
    ).stdout.strip()
    output_lines.append(bq("Remote SHA:", f"{remote_sha}"))

    pull_result = subprocess.run(
        ["git", "pull"],
        cwd=PROJECT_DIR,
        capture_output=True, text=True, check=True
    )
    pull_stdout = pull_result.stdout.strip()
    output_lines.append(bq(f"git pull: {pull_stdout}"))

    if "Already up to date." not in pull_stdout:
        restart = True
        output_lines.append(bq("Обновление завершено."))
        output_lines.append(bq("Запрошен перезапуск."))
        logger.info(f"Update done, restart event triggered. Pull output: {pull_stdout}")
    else:
        output_lines.append(bq("Используется актуальная версия."))
        logger.info("Already up to date, nothing to do.")

    reply_text = "\n".join(output_lines)

    await message.reply(
        bq("Обновление") + "\n" + reply_text,
        parse_mode="HTML"
    )

    if restart: create_task(restart_process())
