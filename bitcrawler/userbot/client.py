# pyright: reportMissingTypeStubs=false
# pyright: reportUnknownMemberType=false
# pyright: reportGeneralTypeIssues=false

from telethon import TelegramClient
from pathlib import Path
from telethon.tl.types import Message
from bitcrawler.config import DATABASES_FOLDER, API_ID, API_HASH, UB_SESSION

client = None
if API_ID and API_HASH:
    client = TelegramClient(str(UB_SESSION), API_ID, API_HASH)

async def download(chat_id: int, message_id: int, file_name: str) -> Path | None:
    if not client: return
    async with client:
        chat = await client.get_entity(chat_id)
        messages = await client.get_messages(entity=chat, ids=message_id)

        if not messages or (isinstance(messages, list) and not messages):
            raise ValueError("Сообщение не найдено")

        msg: Message = messages[0] if isinstance(messages, list) else messages # type: ignore

        if not msg.media:
            raise ValueError("Документ не найден в указанном сообщении")

        file_path: Path = DATABASES_FOLDER / file_name
        await client.download_media(message=msg, file=str(file_path))  # type: ignore

        return file_path
