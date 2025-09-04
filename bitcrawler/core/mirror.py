from aiogram import Bot
from typing import List, Dict, Any
from bitcrawler.utils import database, aiosqlite, setup_logger
from bitcrawler.config import SESSION

logger = setup_logger()

class Mirror:
    table_name = "mirrors"

    def __init__(self, id: int, token: str, owner_id: int, is_active: bool, name: str = "Mirror"):
        self.id = id
        self.token = token
        self.owner_id = owner_id
        self.is_active = is_active
        self.name = name
        self.bot: Bot | None = None

    async def get_bot(self) -> Bot:
        if not self.bot:
            self.bot = Bot(token=self.token, session=SESSION)
            await self.bot.delete_webhook(drop_pending_updates=True)
            logger.info(f"Mirror #{self.id} bot prepared (owner: {self.owner_id})")
        return self.bot

    async def close(self) -> None:
        if self.bot and self.bot.session:
            try:
                await self.bot.session.close()
            except Exception as e:
                logger.error(f"Error closing bot session for Mirror #{self.id}: {e}")
            self.bot = None

    async def _refresh_name_or_delete(self, db: aiosqlite.Connection) -> bool:
        try:
            bot = Bot(token=self.token)
            me = await bot.get_me()
            new_name = me.username or me.first_name or self.name
            await bot.session.close()
        except Exception:
            await db.execute(f"DELETE FROM {self.table_name} WHERE id = ?", (self.id,))
            await db.commit()
            logger.warning(f"Mirror #{self.id} с токеном не найден. Запись удалена.")
            return False

        if new_name != self.name:
            await db.execute(
                f"UPDATE {self.table_name} SET name = ? WHERE id = ?",
                (new_name, self.id)
            )
            await db.commit()
            self.name = new_name
            logger.info(f"Mirror #{self.id} имя обновлено на {self.name}")
        return True

    @classmethod
    @database
    async def create(cls, db: aiosqlite.Connection, owner_id: int, token: str, name: str = "Mirror") -> "Mirror":
        cursor = await db.execute(
            f"INSERT INTO {cls.table_name} (name, token, owner_id) VALUES (?, ?, ?) RETURNING id",
            (name, token, owner_id)
        )
        row = await cursor.fetchone()
        if row is None:
            raise RuntimeError("Не удалось создать зеркало")
        await db.commit()

        return cls(id=row[0], token=token, owner_id=owner_id, is_active=True, name=name)

    @classmethod
    @database
    async def get_all_active(cls, db: aiosqlite.Connection) -> List["Mirror"]:
        cursor = await db.execute(
            f"SELECT id, token, owner_id, is_active, name FROM {cls.table_name} WHERE is_active = 1"
        )
        rows = await cursor.fetchall()
        mirrors: List[Mirror] = []
        for row in rows:
            mirror = cls(
                id=row["id"],
                token=row["token"],
                owner_id=row["owner_id"],
                is_active=bool(row["is_active"]),
                name=row["name"] if row["name"] else f"Mirror#{row['id']}"
            )
            if await mirror._refresh_name_or_delete(db):
                mirrors.append(mirror)
        return mirrors

    @classmethod
    @database
    async def get_by_owner(cls, db: aiosqlite.Connection, owner_id: int) -> List["Mirror"]:
        cursor = await db.execute(
            f"SELECT id, token, name, is_active FROM {cls.table_name} WHERE owner_id = ?",
            (owner_id,)
        )
        rows = await cursor.fetchall()
        mirrors: List[Mirror] = []
        for row in rows:
            mirror = cls(
                id=row["id"],
                token=row["token"],
                owner_id=owner_id,
                is_active=bool(row["is_active"]),
                name=row["name"] if row["name"] else f"Mirror#{row['id']}"
            )
            if await mirror._refresh_name_or_delete(db):
                mirrors.append(mirror)
        return mirrors

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "token": self.token,
            "owner_id": self.owner_id,
            "is_active": self.is_active,
            "name": self.name
        }
