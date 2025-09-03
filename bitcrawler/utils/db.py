from typing import Callable, Any, Awaitable
from typing_extensions import Callable
import aiosqlite
import aiofiles
from bitcrawler.config import DB_PATH, TEMPLATE_SQL

def database(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
    async def wrapper(*args: tuple[Any, ...], **kwargs: dict[str, Any]) -> Any:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            return await func(*args, db=db, **kwargs)
    return wrapper


@database
async def init_db(db: aiosqlite.Connection):
    if not TEMPLATE_SQL.exists(): raise FileNotFoundError(f"{TEMPLATE_SQL} not found.")
    async with aiofiles.open(TEMPLATE_SQL, "r", encoding="utf-8") as f: sql_script = await f.read()
    await db.executescript(sql_script)
    await db.commit()


@database
async def add_database(db: aiosqlite.Connection, name: str, format: str, password: str | None = None) -> str:
    cursor = await db.execute(
        "INSERT INTO databases (name, format) VALUES (?, ?) RETURNING id",
        (name, format)
    )
    row = await cursor.fetchone()
    if row is None: raise RuntimeError("Unable to get variable 'id'")
    return row[0]
