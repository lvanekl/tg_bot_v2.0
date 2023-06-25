from aiogram.types import InputFile
import os

from bot.create_bot import dp, bot
from chats.models import ChatSettings


@dp.message_handler(content_types=["new_chat_members"])
async def new_member(message):
    chat_settings = ChatSettings.objects.get(chat__chat_id=message.chat.id)
    photo = InputFile(str(chat_settings.welcome_meme))
    await bot.send_photo(chat_id=message.chat.id, photo=photo)


@dp.message_handler(commands=['new_member'])
async def new_member(message):
    chat_settings = ChatSettings.objects.get(chat__chat_id=message.chat.id)
    photo = InputFile(str(chat_settings.welcome_meme))
    await bot.send_photo(chat_id=message.chat.id, photo=photo)
