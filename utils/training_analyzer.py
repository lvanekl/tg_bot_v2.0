from datetime import time as Time, date as Date
from chats.models import Chat
from trainings.models import TrainingCorrection, Training


async def analyze_schedule_today(chat: Chat):
    today = Date.today()
    current_weekday = today.weekday()

    today_planned_trainings = Training.objects.filter(chat=chat, weekday=current_weekday)
    all_corrections = TrainingCorrection.objects.filter(chat=chat).order_by('created_at')

    for cor in all_corrections:
        if cor.correction_type == 'move':
            if cor.old_date == today and cor.new_date == today:
                for tr in today_planned_trainings:
                    # если день остается тот же (и это сегодня), то проверяем, что старые время и место те же самые
                    if tr.time == cor.old_time and tr.gym == cor.old_gym:
                        tr.time = cor.new_time
                        tr.gym = cor.new_gym
            elif cor.new_date == today:
                for tr in today_planned_trainings:
                    if tr.time == cor.old_time \
                            and tr.gym == cor.old_gym \
                            and tr.weekday == cor.old_date.weekday():
                        # если тренировка, которую переносят на сегодня вообще была
                        # (старые дата [день недели], место, время указаны правильно)
                        today_planned_trainings.append(Training(chat=chat, weekday=today.weekday(),
                                                                sport=tr.sport,
                                                                gym=cor.new_gym, time=cor.new_time))
            elif cor.old_date == today:
                for tr in today_planned_trainings:
                    if tr.time == cor.old_time and tr.gym == cor.old_gym:
                        del tr

        elif cor.correction_type == 'remove':
            if cor.old_date == today:
                for tr in today_planned_trainings:
                    if tr.time == cor.old_time and tr.gym == cor.old_gym:
                        del tr
        elif cor.correction_type == 'add':
            if cor.new_date == today:
                today_planned_trainings.append(Training(chat=chat, weekday=today.weekday(),
                                                        sport='любой',
                                                        gym=cor.new_gym, time=cor.new_time))

    # today_planned_trainings = [{**dict(s), 'date': today} for s in
    #                            set(frozenset(d.items()) for d in today_planned_trainings)]

    return today_planned_trainings


async def clear_expired_trainings_corrections():
    chats = Chat.objects.all()
    today = Date.today()

    counter = 0
    for chat in chats:
        trainings_corrections = TrainingCorrection.objects.filter(chat_id=chat.chat_id)
        for sch_c in trainings_corrections:
            if sch_c.old_date < today and sch_c.new_date < today:
                sch_c.delete()
                counter += 1

    return f"Удалено {counter} устаревших поправок в расписание"

# if __name__ == "__main__":
#     analyze_schedule_today(telegram_chat_id=1111111)
