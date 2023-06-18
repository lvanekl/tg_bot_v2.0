import logging
from aiogram import types

from env.env import LOG_PATH, LOGGING_LEVEL

logging.basicConfig(level=LOGGING_LEVEL, filename=LOG_PATH, filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s", encoding='utf-8')

from bot.create_bot import my_bot, dp


async def send_poll(telegram_chat_id: int, poll: dict):
    print('aaaaaaaaaaaaaaaaaaaaaa')
    # await self.my_bot.send_message(chat_id=telegram_chat_id, text='aaaaaaa')
    await my_bot.send_poll(chat_id=telegram_chat_id, **poll, is_anonymous=False)
