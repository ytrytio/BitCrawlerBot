from aiogram import Router, F
from bitcrawler.callbacks import *
import re

router = Router(name=__name__)

router.callback_query.register(add, F.data.regexp(re.compile(r"^add_")))
