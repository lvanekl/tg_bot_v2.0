from env.env import telegram_token, LOGGING_LEVEL, LOG_PATH
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import logging

logging.basicConfig(level=LOGGING_LEVEL, filename=LOG_PATH, filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s", encoding='utf-8')

storage = MemoryStorage()
my_bot = Bot(token=telegram_token, parse_mode='HTML')
dp = Dispatcher(my_bot, storage=storage)
