from pathlib import Path
from aiogram.client.session.aiohttp import AiohttpSession
from dotenv import dotenv_values
from typing import Dict

secrets: Dict[str, str | None] = dotenv_values('.env')
BOT_TOKEN: str = secrets["BOT_TOKEN"] or ""
PROXY: str | None = secrets["PROXY"]
SESSION = AiohttpSession(proxy=PROXY) if PROXY else None

SOURCE_CHAT_ID: int = int(secrets["SOURCE_CHAT_ID"]) # type: ignore
SOURCE_TOPIC_ID: int = int(secrets["SOURCE_TOPIC_ID"]) # type: ignore

API_ID: int | None = int(secrets["API_ID"]) if secrets["API_ID"] else None
API_HASH: str | None = secrets["API_HASH"]
PHONE: str | None = secrets["PHONE"]

CURRENT_BRANCH = "master"

PROJECT_DIR = Path(__file__).parent.parent
DATABASES_FOLDER = PROJECT_DIR / "databases"
TEMPLATE_SQL = PROJECT_DIR / "template.sql"
DB_PATH = PROJECT_DIR / "data.db"

UB_SESSION = PROJECT_DIR / "userbot.session"

DATABASES_FOLDER.mkdir(exist_ok=True)
