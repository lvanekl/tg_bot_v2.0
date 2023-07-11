import logging

from aiogram import types
from aiogram.utils.exceptions import Unauthorized

from chats.models import Chat
from env.env import LOG_PATH, LOGGING_LEVEL

logging.basicConfig(level=LOGGING_LEVEL, filename=LOG_PATH, filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s", encoding='utf-8')

from bot.create_bot import bot, dp


async def send_poll(chat_id: int, poll: dict):
    print(f'Отправка голосования в чат {chat_id}')
    print(poll)
    print()
    try:
        await bot.send_poll(chat_id=chat_id, **poll, is_anonymous=False)
    except Unauthorized:
        Chat.objects.get(chat_id=chat_id).delete()
        print(chat_id, 'был удален в телеграмме, больше нет к нему доступа, стираю его из базы')
    except Exception as e:
        logging.error(e)
