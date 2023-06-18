from aiogram import types, Bot

from env.env import DEVELOPER_TELEGRAM_ID, LOGGING_LEVEL, LOG_PATH

import logging

logging.basicConfig(level=LOGGING_LEVEL, filename=LOG_PATH, filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s", encoding='utf-8')

permission_denied_message = f'''Похоже у вас нет доступа к этой функции. Доступ может появиться, если
1) Вас назначат админом чата (через настрйоки чата)
2) Вас назначат админом бота (через настройки бота)
3) Кто-то из админов в настройках включит пункт everyone_is_admin

Доступ может не появиться, если разраб накосячил'''


async def has_permission(chat_id: int, message: types.Message, my_bot: Bot) -> bool:
    # TODO
    # chat_admins = []
    # if message.chat.type == "private":
    #     return True
    # if message.chat.type == "group":
    #     chat_admins = await my_bot.get_chat_administrators(message.chat.id)
    # chat_settings = (await my_db.get_chat_settings(telegram_chat_id=chat_id))[0]
    # bot_admins = await my_db.get_admins(telegram_chat_id=chat_id)
    #
    # everyone_is_admin = chat_settings['everyone_is_admin']
    #
    # user_id = message["from"]["id"]
    # # print(chat_admins, chat_settings, bot_admins)
    # return everyone_is_admin or (user_id in chat_admins+bot_admins) or user_id == DEVELOPER_TELEGRAM_ID
    return True

