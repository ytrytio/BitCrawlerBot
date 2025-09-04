from aiogram import Router, F
from bitcrawler.callbacks import *
import re

def setup_callbacks_router(name: str):
    router = Router(name=f"callbacks_{name}")
    router.callback_query.register(add, F.data.regexp(re.compile(r"^add_")))
    router.callback_query.register(add, F.data == "new_mirror")
    return router
