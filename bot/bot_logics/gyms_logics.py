import logging
from aiogram import types

from env.env import LOG_PATH, BOT_USERNAME, LOGGING_LEVEL

from bot.permissions import has_permission
from bot.create_bot import my_bot, dp

logging.basicConfig(level=LOGGING_LEVEL, filename=LOG_PATH, filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s", encoding='utf-8')

logging.info('importing gyms logics')

gym_commands = ["get_gyms", "add_gym", "remove_gym", "edit_gym"]


@dp.message_handler(commands=gym_commands)
async def gyms_logics_router(message: types.Message):
    funcs = {"get_gyms": get_gyms,  # TODO отформатировать вывод
             "add_gym": add_gym,  # TODO добавить ограничения
             "remove_gym": remove_gym,  # TODO
             "edit_gym": edit_gym}  # TODO

    command = message.get_command(pure=True)
    await funcs[command](message)
    # await self.my_bot.send_poll(chat_id=telegram_chat_id, **poll, is_anonymous=False)
    # await self.my_bot.send_poll(chat_id=telegram_chat_id, **poll, is_anonymous=False)


async def get_gyms(message: types.Message):
    gyms = await my_db.get_gyms(telegram_chat_id=message.chat.id)
    await my_bot.send_message(chat_id=message.chat.id, text=f'{gyms}')


async def add_gym(message: types.Message):
    pass


async def remove_gym(message: types.Message):
    pass


async def edit_gym(message: types.Message):
    pass
