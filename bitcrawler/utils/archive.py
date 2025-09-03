import zipfile
import rarfile  # type: ignore
import py7zr
from .logger import setup_logger
from pathlib import Path
from typing import Tuple, Optional
from bitcrawler.config import DATABASES_FOLDER

logger = setup_logger()


class Archive:
    def __init__(self, file_path: Path, dest_folder: Path = DATABASES_FOLDER, password: str | None = None):
        self.file_path = file_path
        self.dest_folder = dest_folder / file_path.stem
        self.dest_folder.mkdir(parents=True, exist_ok=True)
        self.password = password
        logger.info(f"Archive initialized: {self.file_path} -> {self.dest_folder}")

    def _get_largest_file_ext(self) -> Optional[str]:
        largest_file = None
        largest_size = -1
        for f in self.dest_folder.rglob("*"):
            if f.is_file():
                size = f.stat().st_size
                if size > largest_size:
                    largest_size = size
                    largest_file = f
        return largest_file.suffix.lower() if largest_file else None

    async def unzip(self) -> Tuple[bool, Optional[str]]:
        try:
            with zipfile.ZipFile(self.file_path, 'r') as zip_ref:
                if self.password:
                    zip_ref.extractall(self.dest_folder, pwd=self.password.encode())
                else:
                    zip_ref.extractall(self.dest_folder)
            largest_ext = self._get_largest_file_ext()
            logger.info(f"ZIP extracted in {self.dest_folder}")
            return True, largest_ext
        except (RuntimeError, zipfile.BadZipFile) as e:
            logger.error(f"Failed to extract ZIP: {e}")
            return False, "PR"

    async def unrar(self) -> Tuple[bool, Optional[str]]:
        try:
            with rarfile.RarFile(self.file_path, 'r') as rar_ref:
                if self.password:
                    rar_ref.extractall(self.dest_folder, pwd=self.password)  # type: ignore
                else:
                    rar_ref.extractall(self.dest_folder)  # type: ignore
            largest_ext = self._get_largest_file_ext()
            logger.info(f"RAR extracted in {self.dest_folder}")
            return True, largest_ext
        except rarfile.BadRarFile as e:
            logger.error(f"Failed to extract RAR: {e}")
            return False, "PR"
        except rarfile.PasswordRequired:
            logger.error("RAR archive needs password")
            return False, "IP"
        except rarfile.Error as e:
            logger.error(f"RAR extraction error: {e}")
            return False, None

    async def un7zip(self) -> Tuple[bool, Optional[str]]:
        try:
            with py7zr.SevenZipFile(self.file_path, mode='r', password=self.password) as archive:
                if archive.needs_password() and not self.password:
                    logger.error("Password required for 7z archive")
                    return False, "PR"
                archive.extractall(path=self.dest_folder)
            largest_ext = self._get_largest_file_ext()
            logger.info(f"7z extracted in {self.dest_folder}")
            return True, largest_ext
        except py7zr.exceptions.Bad7zFile as e: # type: ignore
            logger.error(f"Bad 7z file or invalid password: {e}")
            return False, "IP"
        except Exception as e:
            logger.error(f"Failed to extract 7z: {e}")
            return False, None

    async def extract(self) -> Tuple[bool, Optional[str]]:
        ext = self.file_path.suffix.lower()
        if ext == '.zip':
            return await self.unzip()
        elif ext == '.rar':
            return await self.unrar()
        elif ext == '.7z':
            return await self.un7zip()
        else:
            logger.error(f"Unknown archive format: {ext}")
            return False, None

    async def delete(self):
        if self.file_path.exists():
            self.file_path.unlink()
            logger.info(f"Archive deleted: {self.file_path}")
        else:
            logger.warning(f"Archive not found for deletion: {self.file_path}")
