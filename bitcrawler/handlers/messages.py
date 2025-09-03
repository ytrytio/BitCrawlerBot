from bitcrawler.commands import *
from bitcrawler.callbacks import EnterPassword, enter_pass

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.filters.state import StateFilter

router = Router(name=__name__)

router.message.register(start, Command("start"))
router.message.register(on_archive, F.document)
router.message.register(enter_pass, StateFilter(EnterPassword.password), F.text)
