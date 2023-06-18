# from bot.bot_main_file import my_bot, dp
#
# from aiogram import Bot, types, executor, Dispatcher
#
#
#
# @dp.message_handler(commands=["get_schedule", "add_schedule", "remove_schedule",
#                               "edit_schedule", "get_schedule_corrections",
#                               "add_schedule_correction", "remove_schedule_correction",
#                               "edit_schedule_correction", ])
# async def schedule_messages_handler(message: types.Message):
#     funcs = {"/get_schedule": ...,
#              "/add_schedule": ...,
#              "/remove_schedule": ...,
#              "/edit_schedule": ...,
#              "/get_schedule_corrections": ...,
#              "/add_schedule_correction": ...,
#              "/remove_schedule_correction": ...,
#              "/edit_schedule_correction": ...}
#     # TODO
#
#
#
#
# @dp.message_handler(commands=["suggest_a_feature", "report_a_bug"])
# async def feedback_messages_handler(message: types.Message):
#     funcs = {"/suggest_a_feature": ...,
#              "/report_a_bug": ..., }
#     # TODO
#
#
# def send_poll(telegramm_chat_id: int, poll: dict):
#     Bot.send_poll(chat_id=telegramm_chat_id, **poll)
#
