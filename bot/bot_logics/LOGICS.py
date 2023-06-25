# # from bot.bot_main_file import my_bot, dp
# #
# # from aiogram import Bot, types, executor, Dispatcher
# #
# #
# #
# # ["get_schedule_corrections",
# #  "add_schedule_correction", "remove_schedule_correction",
# #  "edit_schedule_correction", ]
# #
# #
# #
# #
# # @dp.message_handler(commands=["suggest_a_feature", "report_a_bug"])
# # async def feedback_messages_handler(message: types.Message):
# #     funcs = {"/suggest_a_feature": ...,
# #              "/report_a_bug": ..., }
# #     # TODO
# #
# #
# # def send_poll(telegramm_chat_id: int, poll: dict):
# #     Bot.send_poll(chat_id=telegramm_chat_id, **poll)
# #
#
#
# @dp.callback_query_handler(text="edit_chat_settings_GPT_question")
# async def edit_GPT_question(callback_query: types.CallbackQuery):
#     # callback_query["message"].chat.id,
#     chat_settings = ChatSettings.objects.get(chat__chat_id=callback_query["message"].chat.id)
#     chat_settings.GPT_question = not chat_settings.GPT_question
#     chat_settings.save()
#
#     await bot.send_message(chat_id=callback_query["message"].chat.id,
#                            text=f'''Настройка GPT_question установлена в значение {chat_settings.GPT_question}''')
#
#
# @dp.callback_query_handler(text="edit_chat_settings_GPT_yes")
# async def edit_GPT_yes(callback_query: types.CallbackQuery):
#     # callback_query["message"].chat.id,
#     chat_settings = ChatSettings.objects.get(chat__chat_id=callback_query["message"].chat.id)
#     chat_settings.GPT_yes = not chat_settings.GPT_yes
#     chat_settings.save()
#
#     await bot.send_message(chat_id=callback_query["message"].chat.id,
#                            text=f'''Настройка GPT_yes установлена в значение {chat_settings.GPT_yes}''')
#
#
# @dp.callback_query_handler(text="edit_chat_settings_GPT_maybe")
# async def edit_GPT_maybe(callback_query: types.CallbackQuery):
#     # callback_query["message"].chat.id,
#     chat_settings = ChatSettings.objects.get(chat__chat_id=callback_query["message"].chat.id)
#     chat_settings.GPT_maybe = not chat_settings.GPT_maybe
#     chat_settings.save()
#
#     await bot.send_message(chat_id=callback_query["message"].chat.id,
#                            text=f'''Настройка GPT_maybe установлена в значение {chat_settings.GPT_maybe}''')
#
#
# @dp.callback_query_handler(text="edit_chat_settings_GPT_no")
# async def edit_GPT_no(callback_query: types.CallbackQuery):
#     # callback_query["message"].chat.id,
#     chat_settings = ChatSettings.objects.get(chat__chat_id=callback_query["message"].chat.id)
#     chat_settings.GPT_no = not chat_settings.GPT_no
#     chat_settings.save()
#
#     await bot.send_message(chat_id=callback_query["message"].chat.id,
#                            text=f'''Настройка GPT_no установлена в значение {chat_settings.GPT_no}''')
#
#
# @dp.callback_query_handler(text="edit_chat_settings_emoji")
# async def edit_emoji(callback_query: types.CallbackQuery):
#     # callback_query["message"].chat.id,
#     chat_settings = ChatSettings.objects.get(chat__chat_id=callback_query["message"].chat.id)
#     chat_settings.emoji = not chat_settings.emoji
#     chat_settings.save()
#
#     await bot.send_message(chat_id=callback_query["message"].chat.id,
#                            text=f'''Настройка emoji установлена в значение {chat_settings.emoji}''')
#
#
# @dp.callback_query_handler(text="edit_chat_settings_language")
# async def edit_language(callback_query: types.CallbackQuery):
#     # callback_query["message"].chat.id,
#     chat_settings = ChatSettings.objects.get(chat__chat_id=callback_query["message"].chat.id)
#     if chat_settings.language == 'Русский':
#         chat_settings.language = 'English'
#
#     # elif chat_settings.language == 'English':
#     #     chat_settings.language = 'Русский'
#     else:
#         chat_settings.language = 'Русский'
#     chat_settings.save()
#
#     await bot.send_message(chat_id=callback_query["message"].chat.id,
#                            text=f'''Настройка language установлена в значение {chat_settings.language}''')
#
#
# @dp.callback_query_handler(text="edit_chat_settings_everyone_is_administrator")
# async def edit_everyone_is_administrator(callback_query: types.CallbackQuery):
#     # callback_query["message"].chat.id,
#     chat_settings = ChatSettings.objects.get(chat__chat_id=callback_query["message"].chat.id)
#     chat_settings.everyone_is_administrator = not chat_settings.everyone_is_administrator
#     chat_settings.save()
#
#     await bot.send_message(chat_id=callback_query["message"].chat.id,
#                            text=f'''Настройка everyone_is_administrator установлена в \
#                            значение {chat_settings.everyone_is_administrator}''')
#
#
# @dp.callback_query_handler(text="edit_chat_settings_auto_poll")
# async def edit_auto_poll(callback_query: types.CallbackQuery):
#     # callback_query["message"].chat.id,
#     chat_settings = ChatSettings.objects.get(chat__chat_id=callback_query["message"].chat.id)
#     chat_settings.auto_poll = not chat_settings.auto_poll
#     chat_settings.save()
#
#     await bot.send_message(chat_id=callback_query["message"].chat.id,
#                            text=f'''Настройка auto_poll установлена в значение {chat_settings.auto_poll}''')
#
#

# async def edit_chat_settings(message: types.Message):
#     edit_chat_settings_inline_keyboard = InlineKeyboardMarkup(row_width=2)
#
#     # имя поля в модели
#     settings_fields = [('welcome_meme', 'Приветственный мем'),
#
#                        # ('poll', 'Настройки опроса'),
#                        ('GPT_question', 'Вопрос от GPT?'),
#                        ('GPT_yes', '"Да" от GPT?'),
#                        ('GPT_maybe', '"Мб" от GPT?'),
#                        ('GPT_no', '"Нет" от GPT?'),
#                        ('emoji', 'Эмодзи?'),
#                        ('language', 'Язык генерации'),
#
#                        ('everyone_is_administrator', 'Все админы?'),
#
#                        ('auto_poll', 'Автоотправка опроса'),
#                        ('poll_send_time', 'Время автоотправки'),  # TODO
#                        ]
#
#     for settings_field in settings_fields:
#         code, name = settings_field
#         edit_chat_settings_inline_keyboard.insert(InlineKeyboardButton(name,
#                                                                        callback_data=f'edit_chat_settings_{code}'))
#
#     await message.reply("Выберите какую настройку вы хотите изменить", reply_markup=edit_chat_settings_inline_keyboard)