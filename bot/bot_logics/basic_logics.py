from aiogram.types import Message, InputFile, ReplyKeyboardRemove

from aiogram.dispatcher import FSMContext
from bot.create_bot import my_bot, dp
from env.env import LOG_PATH, NEW_CHAT_MEME_PATH, LOGGING_LEVEL
from bot.messages import *

import logging

logging.basicConfig(level=LOGGING_LEVEL, filename=LOG_PATH, filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s", encoding='utf-8')

logging.info('importing basic logics')


@dp.message_handler(commands=["start"])
async def start(message: Message):
    chat_id = message.chat.id

    all_chats = await my_db.get_chats()
    for chat in all_chats:
        if chat['telegram_chat_id'] == chat_id:
            await message.answer("Ваш чат уже был добавлен в базу данных ранее и сейчас все должно работать корректно. \
                                \n\nЕсли чето сломалось напишите плз разработчику /feedback_help \
                                \n\nЕсли вы запутались в работе бота можете попробовать кликнуть /help")
            return

    await my_db.new_chat(telegram_chat_id=chat_id)

    photo = InputFile(NEW_CHAT_MEME_PATH)
    await my_bot.send_photo(chat_id=message.chat.id, photo=photo)
    await message.answer('''he-he lessgoooo... Тоесть... всем привет!) Чтобы узнать что я умею кликните /help''')


@dp.message_handler(commands=["help", "conception_explanation", "gyms_help", "schedule_help",
                              "chat_settings_help", "feedback_help", "about", "schedule_note"])
async def help_function(message: Message):
    help_messages = {'help': base_help_message,
                     'conception_explanation': conception_explanation_message,
                     'gyms_help': gyms_help_message,
                     'schedule_help': schedule_help_message,
                     'chat_settings_help': chat_settings_help_message,
                     'feedback_help': feedback_help_message,
                     'about': about_message,
                     "schedule_note": schedule_note_message}
    command = message.get_command(pure=True)  # pure убирает упоминание бота из команды: /command@botname -> command
    await message.answer(help_messages[command])


@dp.message_handler(commands=['cancel'], state="*")
async def cancel(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Окей, отменяю)', reply_markup=ReplyKeyboardRemove())
