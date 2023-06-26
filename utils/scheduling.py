import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bot.bot_logics.basic.polls import send_poll
from utils.poll_generation import generate_poll
from utils.training_analyzer import analyze_schedule_today, clear_expired_trainings_corrections

from env.default_chat_settings import DEFAULT_POLL_SEND_TIME
from env.env import LOG_PATH, TRAININGS_CHECK_RUN_TIME, LOGGING_LEVEL

from chats.models import Chat, ChatSettings
from trainings.models import Training, Gym

from datetime import time as Time, datetime as Datetime, date as Date

logging.basicConfig(level=LOGGING_LEVEL, filename=LOG_PATH, filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s", encoding='utf-8')

loop = asyncio.get_event_loop()
scheduler = AsyncIOScheduler(timezone="Europe/Moscow")


def start_scheduling():
    scheduler.add_job(everyday_schedule_analyzer, trigger='cron',
                      hour=TRAININGS_CHECK_RUN_TIME.hour,
                      minute=TRAININGS_CHECK_RUN_TIME.minute,
                      second=TRAININGS_CHECK_RUN_TIME.second)


async def everyday_schedule_analyzer():
    all_chats = Chat.objects.all()

    generate_poll_tasks = []
    print(all_chats)
    for chat in all_chats:
        chat_settings = ChatSettings.objects.get(chat=chat.id)
        if chat_settings.auto_poll:
            #     await single_chat_analyze_and_send_poll(chat=chat, chat_settings=chat_settings,
            #                                             # send_time=chat_settings['poll_send_time'],
            #                                             send_time=DEFAULT_POLL_SEND_TIME, )
            task = asyncio.create_task(single_chat_analyze_and_send_poll(chat=chat,
                                                                         send_time=chat_settings['poll_send_time'],))
            generate_poll_tasks.append(task)
    await asyncio.gather(*generate_poll_tasks)

    await clear_expired_trainings_corrections()


async def single_chat_analyze_and_send_poll(chat: Chat, send_time: Time):
    today_trainings = await analyze_schedule_today(chat=chat)
    # тестовая тренировка
    date = Date.today()
    time = Time(hour=19, minute=34)
    gym = Gym(chat=chat, name="Акроритм")
    sport = "Спортивная гимнастика"

    training = Training(chat=chat, weekday=date.weekday(), sport=sport, gym=gym, time=time)

    # today_trainings = [training] + list(today_trainings)

    if today_trainings:
        for tr in today_trainings:
            await schedule_a_poll_once(chat=chat,
                                       training=tr,
                                       send_datetime=Datetime.combine(Datetime.today(), send_time))


async def schedule_a_poll_once(chat: Chat, training: Training,
                               send_datetime: Datetime):
    # параметр send_datetime нужен на случай,
    # если отключена автоотправка голосования и люди в чате хотят отправлять ее через /poll

    poll = await generate_poll(chat=chat, training=training)

    # TODO
    scheduler.add_job(send_poll, trigger='date', run_date=send_datetime,
                      kwargs={"chat_id": chat.chat_id,
                              "poll": poll})
