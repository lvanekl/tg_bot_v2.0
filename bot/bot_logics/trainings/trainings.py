import asyncio
import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.bot_logics.gyms.gyms import get_gyms
from bot.create_bot import dp, bot
from bot.permissions import has_permission, permission_denied_message
from chats.models import Chat
from env.env import LOGGING_LEVEL, LOG_PATH
from trainings.models import Training, Gym

from datetime import datetime as Datetime

logging.basicConfig(level=LOGGING_LEVEL, filename=LOG_PATH, filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s", encoding='utf-8')

logging.info('importing gyms logics')

trainings_commands = ["get_trainings", "add_training", "remove_training",
                      "edit_training", ]

day_names = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
day_short_names = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']
day_short_names_to_day_names = dict(zip(day_short_names, day_names))


class AddOrEditTraining(StatesGroup):
    weekday = State()
    time = State()
    gym = State()
    sport = State()


@dp.message_handler(commands=trainings_commands)
async def trainings_logics_router(message: types.Message):
    funcs = {"get_trainings": get_trainings,  # TODO отформатировать вывод, доступы
             "add_training": add_training,  # TODO добавить ограничения, доступы
             "remove_training": remove_training,  # TODO доступы
             "edit_training": edit_training}  # TODO доступы

    command = message.get_command(pure=True)
    await funcs[command](message)
    # await self.my_bot.send_poll(chat_id=telegram_chat_id, **poll, is_anonymous=False)
    # await self.my_bot.send_poll(chat_id=telegram_chat_id, **poll, is_anonymous=False)


async def get_trainings(message: types.Message):
    trainings = Training.objects.filter(chat__chat_id=message.chat.id).order_by('weekday', 'time')

    text = 'Сохраненные тренировки:\n'
    c = 1
    for tr in trainings:
        text += str(c) + ') '
        text += day_names[tr.weekday] + ' - ' + tr.time.strftime('%H:%M') \
                + '  ' + tr.gym.name + f' ({tr.sport})' * bool(tr.sport)
        c += 1
        text += '\n'

    await bot.send_message(chat_id=message.chat.id, text=text)


async def add_training(message: types.Message):
    if not await has_permission(chat_id=message.chat.id, message=message):
        return
    if not Gym.objects.filter(chat__chat_id=message.chat.id):
        await bot.send_message(chat_id=message.chat.id,
                               text=f'Вы не сможете добавить тренирвоку, потому что у вас еще не добавлен ни один зал. '
                                    f'Воспользуйтесь командой /add_gym')
    else:
        await bot.send_message(chat_id=message.chat.id,
                               text=f'Введите день недели \n(цифра 0-6 ИЛИ полное название ИЛИ сокращенное'
                                    f' название из двух букв, регист не важен)\n'
                                    f'Примеры: "0", "ПонеДелЬнИК", "пН"\n'
                                    f'Для отмены нажмите /cancel')

        await AddOrEditTraining.weekday.set()


@dp.message_handler(state=AddOrEditTraining.weekday)
async def add_training_1(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text.isdigit() and 0 <= int(message.text) <= 6:
            data["weekday"] = int(message.text)
        elif message.text.capitalize() in day_names:
            data["weekday"] = day_names.index(message.text.capitalize())
        elif message.text.lower() in day_short_names:
            data["weekday"] = day_short_names.index(message.text)
        else:
            await bot.send_message(chat_id=message.chat.id, text=f'Некорректный формат ввода, попробуйте еще раз')
            return

    await bot.send_message(chat_id=message.chat.id, text=f'Введите время тренировки в формате "HH:MM"\n'
                                                         f'Пример 19:30\n'
                                                         f'Для отмены нажмите /cancel')
    await AddOrEditTraining.next()


@dp.message_handler(state=AddOrEditTraining.time)
async def add_training_2(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        # ниже - проверка на то что введенная строка - время
        if len(message.text) == 5 and message.text[2] == ':' \
                and message.text.replace(':', '').isdigit() \
                and 0 <= int(message.text.split(':')[0]) <= 23 \
                and 0 <= int(message.text.split(':')[1]) <= 59:
            data["time"] = Datetime.strptime(message.text, "%H:%M").time()
        else:
            await bot.send_message(chat_id=message.chat.id, text=f'Некорректный формат ввода, попробуйте еще раз')
            return
    # TODO сделать выбор спортзала Inline клавиатурой
    await bot.send_message(chat_id=message.chat.id, text=f'Выберите спортзал. Для этого '
                                                         f'введите его номер в списке ниже')
    await get_gyms(message)
    await AddOrEditTraining.next()


@dp.message_handler(state=AddOrEditTraining.gym)
async def add_training_3(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        gyms = list(Gym.objects.filter(chat__chat_id=message.chat.id))
        # print(message.text.isdigit(), int(message), len(gyms))
        if message.text.isdigit() and int(message.text) <= len(gyms):
            data["gym"] = gyms[int(message.text) - 1]
        else:
            await bot.send_message(chat_id=message.chat.id, text=f'Некорректный формат ввода, попробуйте еще раз')
            return

    await bot.send_message(chat_id=message.chat.id, text=f'Введите вид спорта')
    await AddOrEditTraining.next()


@dp.message_handler(state=AddOrEditTraining.sport)
async def add_training_4(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["sport"] = message.text

    Training.objects.create(chat=Chat.objects.get(chat_id=message.chat.id),
                            weekday=data["weekday"], time=data["time"],
                            gym=data["gym"], sport=data["sport"])

    await bot.send_message(chat_id=message.chat.id, text=f'Тренировка сохранена')
    await state.finish()


# @dp.message_handler()
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


async def remove_training(message: types.Message):
    if not await has_permission(chat_id=message.chat.id, message=message):
        return
    remover_id = message["from"].id

    trainings = Training.objects.filter(chat__chat_id=message.chat.id).order_by('weekday')

    remove_training_inline_keyboard = InlineKeyboardMarkup(row_width=2)

    for tr in trainings:  # ba - bot admin
        remove_training_inline_keyboard.insert(
            InlineKeyboardButton(f"{day_short_names[tr.weekday]} {tr.time} ({tr.gym.name})",
                                 callback_data=f'remove_training_{tr.id}_by_{remover_id}'))

    remove_training_inline_keyboard.insert(InlineKeyboardButton(f"Отмена",
                                                                callback_data=f'cancel_removing_training_by_{remover_id}'))

    await message.reply("Выберите, какую тренировку удалить", reply_markup=remove_training_inline_keyboard)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("remove_training_"))
async def remove_training_1(callback_query: types.CallbackQuery):
    training_id, remover_id = callback_query.data.replace('remove_training_', '').split('_by_')
    training_id, remover_id = int(training_id), int(remover_id)

    user_clicked_button_id = callback_query["from"]["id"]
    if user_clicked_button_id != remover_id:
        m = await bot.send_message(chat_id=callback_query["message"].chat.id,
                                   text="Выбирать тренировку для удаления должен тот же пользователь, "
                                        "который запустил процесс удаления")
        await asyncio.sleep(2)
        await m.delete()
        return
    else:
        tr = Training.objects.get(id=training_id)
        await bot.send_message(chat_id=callback_query["message"].chat.id,
                               text=f'Пользователь {callback_query["message"].reply_to_message["from"]["username"]} '
                                    f'удалил тренировку "{tr.gym.name} {day_names[tr.weekday]} {tr.time}" из сохраненных')
        tr.delete()
        await callback_query["message"].delete()
        return


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("cancel_removing_training_by_"))
async def remove_training_cancel(callback_query: types.CallbackQuery):
    canceler_id = int(callback_query.data.replace("cancel_removing_training_by_", ''))

    user_clicked_button_id = callback_query["from"]["id"]

    if user_clicked_button_id != canceler_id:
        m = await bot.send_message(chat_id=callback_query["message"].chat.id,
                                   text="Отменять процесс удаления тренировки должен тот же пользователь, "
                                        "который запустил процесс удаления")
        await asyncio.sleep(2)
        await m.delete()
        return
    else:
        await bot.send_message(chat_id=callback_query["message"].chat.id,
                               text=f'Отмена удаления тренировки')
        await callback_query["message"].delete()
        return


async def edit_training(message: types.Message):
    # TODO
    await bot.send_message(chat_id=message.chat.id,
                           text=f'Функция пока не готова, удалите тренировку и создайте новую')
