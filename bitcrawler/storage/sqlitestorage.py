import aiosqlite
from typing import Optional, Dict, Any, Mapping, Union
from aiogram.fsm.storage.base import BaseStorage, StorageKey
from aiogram.fsm.state import State
import json
from bitcrawler.config import DB_PATH

class SQLiteStorage(BaseStorage):
    def __init__(self):
        self.db: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        self.db = await aiosqlite.connect(DB_PATH)
        self.db.row_factory = aiosqlite.Row

    async def close(self) -> None:
        if self.db:
            await self.db.close()
            self.db = None

    async def set_state(
        self,
        key: StorageKey,
        state: Optional[Union[str, State]] = None
    ) -> None:
        assert self.db, "DB not connected"
        state_str = state.state if isinstance(state, State) else state
        await self.db.execute(
            """
            INSERT INTO fsm_states (chat_id, user_id, state)
            VALUES (?, ?, ?)
            ON CONFLICT(chat_id, user_id) DO UPDATE SET state=excluded.state
            """,
            (key.chat_id, key.user_id, state_str)
        )
        await self.db.commit()

    async def get_state(self, key: StorageKey) -> Optional[str]:
        assert self.db, "DB not connected"
        cursor = await self.db.execute(
            "SELECT state FROM fsm_states WHERE chat_id = ? AND user_id = ?",
            (key.chat_id, key.user_id)
        )
        row = await cursor.fetchone()
        return row["state"] if row else None

    async def set_data(self, key: StorageKey, data: Mapping[str, Any]) -> None:
        assert self.db, "DB not connected"
        data_json = json.dumps(dict(data))
        await self.db.execute(
            """
            INSERT INTO fsm_data (chat_id, user_id, data)
            VALUES (?, ?, ?)
            ON CONFLICT(chat_id, user_id) DO UPDATE SET data=excluded.data
            """,
            (key.chat_id, key.user_id, data_json)
        )
        await self.db.commit()

    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
        assert self.db, "DB not connected"
        cursor = await self.db.execute(
            "SELECT data FROM fsm_data WHERE chat_id = ? AND user_id = ?",
            (key.chat_id, key.user_id)
        )
        row = await cursor.fetchone()
        if row and row["data"]:
            return json.loads(row["data"])
        return {}

    async def update_data(self, key: StorageKey, data: Mapping[str, Any]) -> Dict[str, Any]:
        current_data = await self.get_data(key)
        current_data.update(data)
        await self.set_data(key, current_data)
        return current_data
