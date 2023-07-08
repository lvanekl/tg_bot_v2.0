import asyncio
import logging
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from chats.models import Chat
from env.env import LOG_PATH, BOT_USERNAME, LOGGING_LEVEL

from bot.permissions import has_permission, permission_denied_message
from bot.create_bot import bot, dp
from trainings.models import Gym

logging.basicConfig(level=LOGGING_LEVEL, filename=LOG_PATH, filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s", encoding='utf-8')

logging.info('importing gyms logics')

gym_commands = ["get_gyms", "add_gym", "remove_gym", "edit_gym"]


class AddOrEditGym(StatesGroup):
    name = State()
    address = State()


@dp.message_handler(commands=gym_commands)
async def gyms_logics_router(message: types.Message):
    funcs = {"get_gyms": get_gyms,  # TODO отформатировать вывод, доступы
             "add_gym": add_gym,  # TODO добавить ограничения, доступы
             "remove_gym": remove_gym,  # TODO доступы
             "edit_gym": edit_gym}  # TODO доступы

    command = message.get_command(pure=True)
    await funcs[command](message)


async def get_gyms(message: types.Message):
    gyms = Gym.objects.filter(chat__chat_id=message.chat.id)

    text = 'Сохраненные спортзалы:\n'
    c = 1
    for gym in gyms:
        text += str(c) + ') '
        text += gym.name + ' - ' + gym.address
        c += 1
        text += '\n'

    await bot.send_message(chat_id=message.chat.id, text=text)


async def add_gym(message: types.Message):
    if not await has_permission(chat_id=message.chat.id, message=message):
        return
    await bot.send_message(chat_id=message.chat.id, text=f'Введите имя зала')
    await AddOrEditGym.name.set()


@dp.message_handler(state=AddOrEditGym.name)
async def add_gym_1(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["name"] = message.text
    await bot.send_message(chat_id=message.chat.id, text=f'Введите адрес зала')
    await AddOrEditGym.next()


@dp.message_handler(state=AddOrEditGym.address)
async def add_gym_2(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["address"] = message.text
        Gym.objects.create(chat=Chat.objects.get(chat_id=message.chat.id), name=data["name"], address=data["address"])
    await bot.send_message(chat_id=message.chat.id, text=f'Новый зал добавлен')
    await state.finish()


async def remove_gym(message: types.Message):
    if not await has_permission(chat_id=message.chat.id, message=message):
        return
    remover_id = message["from"].id

    gyms = Gym.objects.filter(chat__chat_id=message.chat.id)

    remove_gym_inline_keyboard = InlineKeyboardMarkup(row_width=2)

    for gym in gyms:  # ba - bot admin
        remove_gym_inline_keyboard.add(InlineKeyboardButton(f"{gym.name}",
                                                            callback_data=f'remove_gym_{gym.id}_by_{remover_id}'))

    remove_gym_inline_keyboard.insert(InlineKeyboardButton(f"Отмена",
                                                           callback_data=f'cancel_removing_gym_by_{remover_id}'))

    await message.reply("Выберите, какой спортзал удалить", reply_markup=remove_gym_inline_keyboard)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("remove_gym_"))
async def remove_gym_1(callback_query: types.CallbackQuery):
    gym_id, remover_id = callback_query.data.replace('remove_gym_', '').split('_by_')
    gym_id, remover_id = int(gym_id), int(remover_id)

    user_clicked_button_id = callback_query["from"]["id"]
    if user_clicked_button_id != remover_id:
        m = await bot.send_message(chat_id=callback_query["message"].chat.id,
                                   text="Выбирать зал для удаления должен тот же пользователь, "
                                        "который запустил процесс удаления")
        await asyncio.sleep(2)
        await m.delete()
        return
    else:
        gym = Gym.objects.get(id=gym_id)
        await bot.send_message(chat_id=callback_query["message"].chat.id,
                               text=f'Пользователь {callback_query["message"].reply_to_message["from"]["username"]} '
                                    f'удалил спортзал {gym.name} из сохраненных')
        gym.delete()
        await callback_query["message"].delete()
        return


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("cancel_removing_gym_by_"))
async def remove_gym_cancel(callback_query: types.CallbackQuery):
    canceler_id = int(callback_query.data.replace("cancel_removing_gym_by_", ''))

    user_clicked_button_id = callback_query["from"]["id"]

    if user_clicked_button_id != canceler_id:
        m = await bot.send_message(chat_id=callback_query["message"].chat.id,
                                   text="Отменять процесс удаления зала должен тот же пользователь, "
                                        "который запустил процесс удаления")
        await asyncio.sleep(2)
        await m.delete()
        return
    else:
        await bot.send_message(chat_id=callback_query["message"].chat.id,
                               text=f'Отмена удаления зала')
        await callback_query["message"].delete()
        return


async def edit_gym(message: types.Message):
    # TODO
    await bot.send_message(chat_id=message.chat.id,
                           text=f'Функция пока не готова, удалите зал и создайте новый')
