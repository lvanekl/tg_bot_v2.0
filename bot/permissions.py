from aiogram import types
from env.env import DEVELOPER_TELEGRAM_ID, LOGGING_LEVEL, LOG_PATH
from bot.create_bot import bot
import logging

logging.basicConfig(level=LOGGING_LEVEL, filename=LOG_PATH, filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s", encoding='utf-8')

from chats.models import ChatSettings, ChatAdministrator, Chat

permission_denied_message = f'''Похоже у вас нет доступа к этой функции. Доступ может появиться, если
1) Вас назначат админом чата (через настрйоки чата)
2) Вас назначат админом бота (через настройки бота)
3) Кто-то из админов в настройках включит пункт everyone_is_admin

Доступ может не появиться, если разраб накосячил'''


async def has_permission(chat_id: int, message: types.Message) -> bool:
    return True
    # TODO
    chat_admins = []

    if message.chat.type == "private":
        return True
    if message.chat.type == "group":
        chat_admins = await bot.get_chat_administrators(message.chat.id)

    chat_settings = Chat.objects.get(chat_id=chat_id).chat_settings
    everyone_is_admin = chat_settings.everyone_is_admin

    bot_admins = [bot_admin.user_id for bot_admin in Chat.objects.get(chat_id=chat_id).chat_administrators]

    # TODO убрать это сообщение, провести дебаг этой функции
    print('permissions file: ', chat_settings, chat_admins, bot_admins)

    user_id = message["from"]["id"]
    # print(chat_admins, chat_settings, bot_admins)
    return everyone_is_admin or (user_id in chat_admins+bot_admins) or user_id == DEVELOPER_TELEGRAM_ID

