from aiogram.types import Message
from bitcrawler.utils import bq
from bitcrawler.config import DATABASES_FOLDER
from bitcrawler.utils import setup_logger
from logging import Logger
from collections import defaultdict
from typing import List, Tuple, Dict, Set
import re
import csv

logger: Logger = setup_logger()

NORMALIZED_HEADERS = {
    r"(?i)^(name|имя)$": "Имя",
    r"(?i)^(surname|фамилия)$": "Фамилия",
    r"(?i)^(email|почта|e-mail)$": "Email",
    r"(?i)^(phone|телефон|номер)$": "Телефон",
    r"(?i)^(address|адрес)$": "Адрес",
    r"(?i)^(city|город)$": "Город",
    r"(?i)^(username|логин)$": "Юзернейм",
    r"(?i)^(id|telegram id)$": "Telegram ID"
}

def normalize_header(header: str) -> str:
    for pattern, normalized in NORMALIZED_HEADERS.items():
        if re.match(pattern, header.strip(), re.IGNORECASE):
            return normalized
    return header.strip()

def extract_row_dict(headers: List[str], row: List[str]) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for i, cell in enumerate(row):
        if i < len(headers):
            name = normalize_header(headers[i])
            value = cell.strip()
            if value:
                result[name] = value
    return result

async def search(message: Message):
    if not message.chat or not message.from_user or not message.text:
        logger.warning(f"Invalid message: chat={message.chat}, from_user={message.from_user}, text={message.text}")
        return
    if message.chat.type != "private":
        logger.info(f"Ignoring search command in non-private chat: {message.chat.type}")
        return

    try:
        query = " ".join(message.text.split(" ")[1:]).strip()
        if not query:
            await message.reply(
                bq("ПОИСК BitCrawler") + "\n" +
                bq("Введите запрос после команды.") + "\n\n" +
                bq("Использование:", "<code>/search {запрос}</code>") + "\n\n" +
                bq("Разрешённые форматы запроса:",
                   "\nНомер телефона (<code>+70123456789</code>)"
                   "\nTelegram ID (<code>@123456789</code>)"
                   "\nЮзернейм (<code>@username</code>)"),
                parse_mode="HTML"
            )
            return

        column_patterns = {
            "phone": r"(?i)\b(Телефон|phone|номер)\b",
            "telegram_id": r"(?i)\b(Telegram ID|id)\b",
            "username": r"(?i)\b(Юзернейм|username|логин)\b"
        }

        query_type = None
        search_query = None

        if re.match(r'^\+\d{10,12}$', query):
            query_type = "phone"
            search_query = query[1:]
        elif re.match(r'^@(\d{6,12})$', query):
            query_type = "telegram_id"
            search_query = query[1:]
        elif re.match(r'^@[a-zA-Z_][\w]{4,31}$', query):
            query_type = "username"
            search_query = query[1:]
        else:
            await message.reply(
                bq("ПОИСК BitCrawler") + "\n" +
                bq("Неверный формат запроса.") + "\n\n" +
                bq("Разрешённые форматы запроса:",
                   "\nНомер телефона (<code>+70123456789</code>)"
                   "\nTelegram ID (<code>@123456789</code>)"
                   "\nЮзернейм (<code>@username</code>)"),
                parse_mode="HTML"
            )
            return

        escaped_query = re.escape(search_query)
        pattern = rf'\b{escaped_query}\b'

        matches: List[Tuple[str, Dict[str, str]]] = []

        if not DATABASES_FOLDER.exists() or not DATABASES_FOLDER.is_dir():
            await message.reply(
                bq("ПОИСК BitCrawler") + "\n" +
                bq("Ошибка:", "Папка с данными недоступна."),
                parse_mode="HTML"
            )
            return

        files = [f for f in DATABASES_FOLDER.rglob("*")
                 if f.is_file() and f.suffix.lower() in (".csv", ".txt")]

        if not files:
            await message.reply(
                bq("ПОИСК BitCrawler") + "\n" +
                bq("Данные не найдены.") + "\n" +
                bq("Запрос:", f"<code>{query}</code>"),
                parse_mode="HTML"
            )
            return

        for file_path in files:
            try:
                if file_path.suffix.lower() == ".csv":
                    try:
                        with open(file_path, "r", encoding="utf-8-sig") as f:
                            reader = csv.reader(f)
                            headers: List[str] = next(reader, []) # type: ignore
                            target_columns = [
                                i for i, header in enumerate(headers)
                                if re.search(column_patterns[query_type], header.strip())
                            ]
                            if not target_columns:
                                continue

                            for row in reader:
                                for col_idx in target_columns:
                                    if col_idx < len(row):
                                        cell_value = row[col_idx].strip()
                                        if re.search(pattern, cell_value, re.IGNORECASE):
                                            matches.append((file_path.name, extract_row_dict(headers, row)))
                                            break
                    except UnicodeDecodeError:
                        with open(file_path, "r", encoding="latin-1") as f:
                            reader = csv.reader(f)
                            headers: List[str] = next(reader, []) # type: ignore
                            target_columns = [
                                i for i, header in enumerate(headers)
                                if re.search(column_patterns[query_type], header.strip())
                            ]
                            if not target_columns:
                                continue

                            for row in reader:
                                for col_idx in target_columns:
                                    if col_idx < len(row):
                                        cell_value = row[col_idx].strip()
                                        if re.search(pattern, cell_value, re.IGNORECASE):
                                            matches.append((file_path.name, extract_row_dict(headers, row)))
                                            break

                else:
                    continue

            except Exception as e:
                logger.error(f"Error reading file {file_path.name}: {e}")
                continue

        if not matches:
            await message.reply(
                bq("ПОИСК BitCrawler") + "\n" +
                bq("Данные не найдены.") + "\n" +
                bq("Запрос:", f"<code>{query}</code>"),
                parse_mode="HTML"
            )
            return

        aggregated_data: Dict[str, Set[str]] = defaultdict(set)
        for _, row_dict in matches:
            for column, value in row_dict.items():
                aggregated_data[column].add(value)

        def pluralize_sootvet(amount: int) -> str:
            last_two = amount % 100
            last = amount % 10
            if 11 <= last_two <= 14:
                return "совпадений"
            elif last == 1:
                return "совпадение"
            elif 2 <= last <= 4:
                return "совпадения"
            return "совпадений"

        amount = len(matches)
        word = pluralize_sootvet(amount)
        response = (
            bq("ПОИСК BitCrawler") + "\n" +
            bq(f"Найдено {amount} {word} по запросу:", f"<code>{query}</code>") + "\n\n"
        )

        for column, values in aggregated_data.items():
            response += bq(f"{column}:", ", ".join(sorted(values))) + "\n"

        await message.reply(response, parse_mode="HTML")

    except Exception as e:
        logger.error(f"Error processing search query: {e}")
        await message.reply(
            bq("ПОИСК BitCrawler") + "\n" +
            bq("Ошибка:", str(e)),
            parse_mode="HTML"
        )
