import logging
import os

from env.default_chat_settings import *
import asyncio
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.permissions import has_permission, permission_denied_message

from env.env import LOG_PATH, LOGGING_LEVEL

from bot.create_bot import bot, dp

from chats.models import Chat, ChatAdministrator, ChatSettings

logging.basicConfig(level=LOGGING_LEVEL, filename=LOG_PATH, filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s", encoding='utf-8')

admin_commands = ["add_bot_admin", "remove_bot_admin", "get_bot_admins"]


class AddAdmin(StatesGroup):
    username = State()


@dp.message_handler(commands=admin_commands)
async def admin_router(message: types.Message):
    funcs = {"get_bot_admins": get_bot_admins,  # TODO отформатировать вывод
             "add_bot_admin": add_bot_admin,  # TODO добавить ограничения, добавить ограничения на функцию второго шага
             # (там где непосредственно добавляется админ нет проверки на то, чтобы
             # переслал искомое сообщение именно тот кто запустил команду
             "remove_bot_admin": remove_bot_admin}  # TODO добавить ограничения

    command = message.get_command(pure=True)
    await funcs[command](message=message)


async def get_bot_admins(message: types.Message):
    admins = ChatAdministrator.objects.filter(chat__chat_id=message.chat.id)
    await bot.send_message(chat_id=message.chat.id, text=f'{[admin.user_id for admin in admins]}')


async def add_bot_admin(message: types.Message):
    if not await has_permission(chat_id=message.chat.id, message=message): return

    await AddAdmin.username.set()
    await bot.send_message(chat_id=message.chat.id,
                           text=f'<b>Ответьте</b> на сообщение человека, которого вы хотите назначить админом (потянуть влево)')


#
@dp.message_handler(state=AddAdmin.username)
async def add_bot_admin_1(message: types.Message, state: FSMContext):
    replied_message = message.reply_to_message
    if replied_message is None:
        await bot.send_message(chat_id=message.chat.id,
                               text=f'<b>Ответьте</b> на сообщение человека, которого вы хотите назначить админом (потянуть влево)\n'
                                    f'Да, это костыльно, но как сделать иначе я так и не придумал\n'
                                    f'Чтобы отменить нажмите /cancel')
        return

    new_admin_id = replied_message["from"]["id"]

    current_bot_admins = [bot_admin.user_id for bot_admin in ChatAdministrator.objects.filter(chat=message.chat.id)]

    if new_admin_id in current_bot_admins:
        await bot.send_message(chat_id=message.chat.id,
                               text=f'Этот пользователь итак является админом для бота в этом чате\n'
                                    f'Можете переслать сообщение от другого юзера или отменить процесс назначения админа /cancel')
        return

    elif replied_message["from"]["is_bot"]:
        await bot.send_message(chat_id=message.chat.id,
                               text=f'Нельзя назначить другого бота админом для этого бота\n'
                                    f'Можете переслать сообщение от другого юзера или отменить процесс назначения админа /cancel')
        return

    else:
        ChatAdministrator.objects.create(chat=Chat.objects.get(chat_id=message.chat.id), user_id=new_admin_id)
        await bot.send_message(chat_id=message.chat.id,
                               text=f'Пользователь {replied_message["from"]["username"]} назначен админом для бота в этом чате')
        await state.finish()
        return


async def remove_bot_admin(message: types.Message):
    if not await has_permission(chat_id=message.chat.id, message=message): return
    remover_id = message["from"].id
    current_bot_admins = [await bot.get_chat_member(chat_id=message.chat.id, user_id=bot_admin.user_id)
                          for bot_admin in ChatAdministrator.objects.filter(chat__chat_id=message.chat.id)]

    # print(current_bot_admins)
    # print(current_bot_admins[0]['telegram_user_id'])
    # print(await my_bot.get_chat_member(
    #     chat_id=message.chat.id, user_id=current_bot_admins[0]['telegram_user_id']))

    remove_admin_inline_keyboard = InlineKeyboardMarkup(row_width=2)
    # print(current_bot_admins)
    for ba in current_bot_admins:  # ba - bot admin
        remove_admin_inline_keyboard.add(InlineKeyboardButton(f"{ba.user.username}",
                                                              callback_data=f'remove_bot_admin_{ba.user.id}_by_{remover_id}'))

    remove_admin_inline_keyboard.insert(InlineKeyboardButton(f"Отмена",
                                                             callback_data=f'cancel_removing_bot_admin_{remover_id}'))

    await message.reply("Выберите, кого удалить из админов бота", reply_markup=remove_admin_inline_keyboard)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("remove_bot_admin_"))
async def remove_bot_admin_1(callback_query: types.CallbackQuery):
    # print(callback_query)
    admin_id, remover_id = callback_query.data.replace('remove_bot_admin_', '').split('_by_')
    admin_id, remover_id = int(admin_id), int(remover_id)

    member_username = (await bot.get_chat_member(chat_id=callback_query["message"].chat.id,
                                                 user_id=admin_id))["user"]["username"]

    user_clicked_button_id = callback_query["from"]["id"]
    if user_clicked_button_id != remover_id:
        m = await bot.send_message(chat_id=callback_query["message"].chat.id,
                                   text="Выбирать юзера для удаления должен тот же пользователь, "
                                        "который запустил процесс удаления")
        await asyncio.sleep(2)
        await m.delete()
        return
    else:
        ChatAdministrator.objects.get(chat__chat_id=callback_query["message"].chat.id, user_id=admin_id).delete()
        await bot.send_message(chat_id=callback_query["message"].chat.id,
                               text=f'Пользователь {callback_query["message"].reply_to_message["from"]["username"]} '
                                    f'разжаловал из админов пользователя {member_username}')
        await callback_query["message"].delete()
        return

    # if
    # user_id = int(callback_query.data.replace('rm_b_a_', ''))
    # await my_db.remove_admin()
    #
    #     await bot.answer_callback_query(callback_query.id)
    # await bot.send_message(callback_query.from_user.id, f'Нажата инлайн кнопка! code={code}')


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("cancel_removing_bot_admin_"))
async def remove_bot_admin_cancel(callback_query: types.CallbackQuery):
    canceler_id = int(callback_query.data.replace("cancel_removing_bot_admin_", ''))

    user_clicked_button_id = callback_query["from"]["id"]

    if user_clicked_button_id != canceler_id:
        m = await bot.send_message(chat_id=callback_query["message"].chat.id,
                                   text="Отменять процесс удаления админа должен тот же пользователь, "
                                        "который запустил процесс удаления")
        await m.delete()
        return
    else:
        await bot.send_message(chat_id=callback_query["message"].chat.id,
                               text=f'Отмена удаления админа')
        await callback_query["message"].delete()
        return
