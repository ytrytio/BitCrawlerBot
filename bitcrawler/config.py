from pathlib import Path
from aiogram.client.session.aiohttp import AiohttpSession
from dotenv import dotenv_values
from typing import Dict

secrets: Dict[str, str | None] = dotenv_values('.env')
PROXY: str | None = secrets["PROXY"]
SESSION = AiohttpSession(proxy=PROXY) if PROXY else None

CURRENT_BRANCH = "master"

PROJECT_DIR = Path(__file__).parent.parent
DATABASES_FOLDER = PROJECT_DIR / "databases"
TEMPLATE_SQL = PROJECT_DIR / "template.sql"
DB_PATH = PROJECT_DIR / "data.db"

DATABASES_FOLDER.mkdir(exist_ok=True)
