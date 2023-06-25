import logging
from aiogram import types

from env.env import LOG_PATH, LOGGING_LEVEL

logging.basicConfig(level=LOGGING_LEVEL, filename=LOG_PATH, filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s", encoding='utf-8')

from bot.create_bot import bot, dp


async def send_poll(chat_id: int, poll: dict):
    print(f'Отправка голосования в чат {chat_id}')
    print(poll)
    print()
    # await self.my_bot.send_message(chat_id=telegram_chat_id, text='aaaaaaa')
    await bot.send_poll(chat_id=chat_id, **poll, is_anonymous=False)
