from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
DATABASES_FOLDER = PROJECT_DIR / "databases"
TEMPLATE_SQL = PROJECT_DIR / "template.sql"
DB_PATH = PROJECT_DIR / "data.db"

DATABASES_FOLDER.mkdir(exist_ok=True)
