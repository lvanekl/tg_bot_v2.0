import logging
import os

from datetime import datetime as Datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, Group
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog import Dialog
from bot.create_bot import dp, dr, bot

from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager, StartMode

from bot.permissions import permission_denied_message, has_permission
from chats.models import ChatSettings
from env.default_chat_settings import DEFAULT_WELCOME_MEME_PATH, DEFAULT_POLL_SEND_TIME
from env.env import LOGGING_LEVEL, LOG_PATH

logging.basicConfig(level=LOGGING_LEVEL, filename=LOG_PATH, filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s", encoding='utf-8')

windows_width = 1


async def toggle_boolean_field(c: CallbackQuery, button: Button, manager: DialogManager):
    chat_id = c["message"].chat.id
    chat_settings = ChatSettings.objects.get(chat__chat_id=chat_id)

    button_id = button.widget_id.replace('_btn', '', 1)

    chat_settings.__setattr__(button_id, not chat_settings.__getattribute__(button_id))

    # chat_settings[button_id] = not chat_settings[button_id]
    chat_settings.save()


async def toggle_language(c: CallbackQuery, button: Button, manager: DialogManager):
    chat_id = c["message"].chat.id
    chat_settings = ChatSettings.objects.get(chat__chat_id=chat_id)

    if chat_settings.language == 'Русский':
        chat_settings.language = "English"
    else:
        chat_settings.language = "Русский"
    chat_settings.save()


class EditWelcomeMeme(StatesGroup):
    picture = State()


async def edit_welcome_meme(c: CallbackQuery, button: Button, manager: DialogManager):
    # chat_id = c["message"].chat.id
    await c["message"].delete_reply_markup()
    await bot.send_message(chat_id=c["message"].chat.id,
                           text="Отправьте в чат новую картинку."
                                "Отправьте DEFAULT чтобы установить картинку по умолчанию "
                                "(она тоже очень неплоха). Чтобы отменить введите /cancel")
    await EditWelcomeMeme.picture.set()


@dp.message_handler(state=EditWelcomeMeme.picture, content_types=["photo", "text"])
async def edit_welcome_meme_1(message: types.Message, state: FSMContext):
    if message.text == 'DEFAULT':
        chat_settings = ChatSettings.objects.get(chat__chat_id=message.chat.id)
        chat_settings.welcome_meme = DEFAULT_WELCOME_MEME_PATH
        chat_settings.save()
        await bot.send_message(chat_id=message.chat.id,
                               text="Установлена приветственная картинка по умолчанию")
    else:
        chat_settings = ChatSettings.objects.get(chat__chat_id=message.chat.id)

        file_info = await bot.get_file(message.photo[-1].file_id)
        path = os.path.join('media', 'welcome_memes', file_info.file_path.split('photos/')[1])
        await message.photo[-1].download(destination_file=path)
        chat_settings.welcome_meme = path
        chat_settings.save()
        await bot.send_message(chat_id=message.chat.id,
                               text="Установлена новая приветственная картинка")

    await state.finish()


class EditPollSendTime(StatesGroup):
    time = State()


async def edit_poll_send_time(c: CallbackQuery, button: Button, manager: DialogManager):
    # chat_id = c["message"].chat.id
    await c["message"].delete_reply_markup()
    await bot.send_message(chat_id=c["message"].chat.id,
                           text=f"Отправьте в чат время, во сколько должен отправляться опрос в чат (формат: HH:MM)"
                                f"Отправьте DEFAULT чтобы установить значение по умолчанию ({DEFAULT_POLL_SEND_TIME}). Чтобы отменить введите /cancel")
    await EditPollSendTime.time.set()


@dp.message_handler(state=EditPollSendTime.time)
async def edit_poll_send_time_1(message: types.Message, state: FSMContext):
    if message.text == 'DEFAULT':
        chat_settings = ChatSettings.objects.get(chat__chat_id=message.chat.id)
        chat_settings.poll_send_time = DEFAULT_POLL_SEND_TIME
        chat_settings.save()
        await bot.send_message(chat_id=message.chat.id,
                               text=f"Установлено время отправки по умолчанию ({DEFAULT_POLL_SEND_TIME})")
    elif (len(message.text) == 5 and message.text[2] == ':'
          and message.text.replace(':', '').isdigit()
          and 0 <= int(message.text.split(':')[0]) <= 23
          and 0 <= int(message.text.split(':')[1]) <= 59):

        chat_settings = ChatSettings.objects.get(chat__chat_id=message.chat.id)
        chat_settings.poll_send_time = Datetime.strptime(message.text, "%H:%M").time()
        chat_settings.save()
        await bot.send_message(chat_id=message.chat.id,
                               text="Установлено новое время отправки опроса")

    else:
        await bot.send_message(chat_id=message.chat.id, text=f'Некорректный формат ввода, попробуйте еще раз')
        return

    await state.finish()


async def get_settings_values(**kwargs):
    event = kwargs["dialog_manager"].event
    if isinstance(event, Message):
        message = event
    elif isinstance(event, CallbackQuery):
        message = event.message
    else:
        message = event.message
        print(type(event), event)
    chat_id = message.chat.id
    chat_settings = ChatSettings.objects.get(chat__chat_id=chat_id)
    # print()
    # print('m', kwargs["dialog_manager"].__dict__)
    poll_generation = {"GPT_question": chat_settings.GPT_question,
                       "GPT_yes": chat_settings.GPT_yes,
                       "GPT_maybe": chat_settings.GPT_maybe,
                       "GPT_no": chat_settings.GPT_no,
                       "emoji": chat_settings.emoji,
                       "language": chat_settings.language}
    poll_send = {"poll_send_time": chat_settings.poll_send_time,
                 "auto_poll": chat_settings.auto_poll}
    admininstrate = {'everyone_is_administrator': chat_settings.everyone_is_administrator}
    return {**poll_generation, **poll_send, **admininstrate}


async def to_poll_variants(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(Settings.poll_variants)


async def to_poll_send(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(Settings.poll_send)


async def to_administrate(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(Settings.administrate)


async def to_other(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(Settings.other)


async def to_main(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().switch_to(Settings.main)


async def to_exit(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.done()


class Settings(StatesGroup):
    main = State()
    poll_send = State()  # настройки связанные с отправкой опросов
    poll_variants = State()  # настройки связанные с наполнением опросов
    administrate = State()  # настройки связанные с администрированием
    other = State()  # настройки связанные с приветственным мемом


settings_main_window = Window(
    Const("Настройки"),
    Group(Button(Const("Наполнение опросов"), id="poll_variants_btn", on_click=to_poll_variants),
          Button(Const("Отправка опросов"), id="poll_send_btn", on_click=to_poll_send),
          Button(Const("Администрирование"), id="administrate_btn", on_click=to_administrate),
          Button(Const("Другое"), id="other_btn", on_click=to_other),
          Button(Const("Выйти"), id="exit_btn", on_click=to_exit),
          width=windows_width, ),
    state=Settings.main
)

settings_poll_variants_window = Window(
    Const("Настройки наполнения опросов"),
    Group(Button(Format("Вопрос от GPT? - {GPT_question}"), id="GPT_question_btn", on_click=toggle_boolean_field),
          Button(Format('"Да" от GPT? - {GPT_yes}'), id="GPT_yes_btn", on_click=toggle_boolean_field),
          Button(Format('"Мб" от GPT? - {GPT_maybe}'), id="GPT_maybe_btn", on_click=toggle_boolean_field),
          Button(Format('"Нет" от GPT? - {GPT_no}'), id="GPT_no_btn", on_click=toggle_boolean_field),
          Button(Format('Эмодзи? - {emoji}'), id="emoji_btn", on_click=toggle_boolean_field),
          Button(Format('Язык генерации - {language}'), id="language_btn", on_click=toggle_language),
          Button(Const('Назад'), id="back_btn", on_click=to_main),
          width=windows_width, ),
    state=Settings.poll_variants,
    getter=get_settings_values,
)

settings_poll_send_window = Window(
    Const("Настройки отправки опросов"),
    Group(Button(Format("Время отправки - {poll_send_time}"), id="poll_send_time_btn", on_click=edit_poll_send_time),
          Button(Format('Автоотправка? - {auto_poll}'), id="auto_poll_btn", on_click=toggle_boolean_field),
          Button(Const('Назад'), id="back_btn", on_click=to_main),
          width=windows_width, ),
    state=Settings.poll_send,
    getter=get_settings_values,
)

settings_administrate_window = Window(
    Const("Настройки администрирования"),
    Group(Button(Format("Все админы? - {everyone_is_administrator}"), id="everyone_is_administrator_btn",
                 on_click=toggle_boolean_field),
          Button(Const('Назад'), id="back_btn", on_click=to_main),
          width=windows_width, ),
    state=Settings.administrate,
    getter=get_settings_values,
)

settings_other_window = Window(
    Const("Другие настройки (для вывода картинки-приветствия нажмите /new_member)"),
    Group(Button(Const("Поменять картинку-приветствие"), id="welcome_meme_btn",
                 on_click=edit_welcome_meme),
          Button(Const('Назад'), id="back_btn", on_click=to_main),
          width=windows_width, ),
    state=Settings.other,
)

dr.register(Dialog(settings_main_window,
                   settings_poll_variants_window,
                   settings_poll_send_window,
                   settings_administrate_window,
                   settings_other_window))


@dp.message_handler(commands=["chat_settings"])
async def chat_settings(message: Message, dialog_manager: DialogManager):
    if not await has_permission(chat_id=message.chat.id, message=message): return
    await dialog_manager.start(Settings.main, mode=StartMode.RESET_STACK)
