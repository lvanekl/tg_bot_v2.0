from aiogram import types
from aiogram.utils import exceptions

from bot.create_bot import bot, dp
from env.env import LOG_PATH, LOGGING_LEVEL

import logging

logging.basicConfig(level=LOGGING_LEVEL, filename=LOG_PATH, filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s", encoding='utf-8')

logging.info('importing basic logics')


@dp.errors_handler(exception=exceptions.RetryAfter)
async def exception_handler(update: types.Update, exception: exceptions.RetryAfter):
    # Do something
    # print(locals())
    # print(update.__dict__)
    # print()
    print(1)
    print(exception)
    print(2)
    print(update.callback_query.message.chat.id, type(update.callback_query.message.chat.id))
    await bot.send_message(chat_id=int(update.callback_query.message.chat.id), text=exception)
    return True
