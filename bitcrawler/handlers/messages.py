from aiogram import Router, F
from aiogram.filters import Command
from aiogram.filters.state import StateFilter
from bitcrawler.commands import *
from bitcrawler.callbacks import EnterPassword, EnterToken, enter_pass, enter_token

def setup_messages_router(name: str):
    router = Router(name=f"messages_{name}")

    router.message.register(start, Command("start"))
    router.message.register(mirrors, Command("mirrors"))
    router.message.register(on_archive, F.document)
    router.message.register(enter_pass, StateFilter(EnterPassword.password), F.text)
    router.message.register(enter_token, StateFilter(EnterToken.token), F.text)

    return router
