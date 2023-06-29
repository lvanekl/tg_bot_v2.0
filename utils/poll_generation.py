import datetime
import json
import random

import asyncio
import logging

import aiohttp
# import openai

from env.env import openai_token, LOG_PATH, LOGGING_LEVEL, PROXY_URL
from datetime import date as Date, time as Time
from chats.models import ChatSettings, Chat
from trainings.models import Training, Gym

# openai.api_key = openai_token

logging.basicConfig(level=LOGGING_LEVEL, filename=LOG_PATH, filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s", encoding='utf-8')

default_prompt = '''Я занимаюсь в спортсекции и я провожу голосование о сегодняшней тренировке, 
чтобы люди могли отметить планируют ли они сегодня прийти. По смыслу варианты ответа следующие: да, нет, не знаю. 
Твоя задача придумать вопрос и замены этим вариантам ответов, чтобы опросы не были однообразными. Атмосфера дружеская и в чате приветствуются подколы вплоть до самых жестких. 
Нужны варианты ответов в максимально шутливой форме - выдавай самые абсурдные и абстрактные варианты. Как можно меньше пафоса. Я хочу получить ответ в формате json:
{"question": ["", "", ""], "yes": ["", "", ""], "maybe": ["", "", ""], "no": ["", "", ""], ]}. 
Вот тебе примеры хороших вариантов,  {
  "question": [
    "Собираешься засиять на тренировке сегодня?",
    "Какие планы на вечер?",
    "Как насчет тренировочки сегодня?"
  ],
  "yes": [
    "Я приду и покажу всем, как сделать отжимание на одной руке, держа бутерброд в другой",
    "Да, сегодня я буду участвовать в спортивной эпопее!",
    "Да, я настроен так серьезно, что мои мышцы уже начали набирать массу, только думая об этой тренировке!",
  ],
  "no": [
    "Не сегодня, я решил(а) превратиться в картофельное чипсовое лежебоко",
    "Нет, я официально объявляю себя чемпионом по совмещению диванной и телевизионной гимнастики",
    "Я собираюсь сидеть и вынашивать новые спортивные идеи в покое.",
    "Нет, моя энергия будет направлена на увеличение попкорна в своем организме.",
    "Сегодня я не приду, потому что меня похитили пришельцы и они требуют, чтобы я им показал, как пропускать тренировки.",
    "Нет, сегодня я занят чем-то ненужным и бессмысленным".
  ],
  "maybe": [
    "Я на грани решения между тренировкой и занятием мастерством подушечного боя",
    "Моя предвыборная кампания между тренировкой и отдыхом зависит от победы апатии или энтузиазма."
  ]
}

НО ИХ ТЕБЕ КОПИРОВАТЬ НЕЛЬЗЯ. Придумай сам, мне нужны именно новые варианты ответов
Обязательно сделай перепроверку на грамматические, фактические и речевые ошибки. 
Также проверь, чтобы в ответе не было пустых строк ('')
Также ни один из вариантов ответа не должен быть длиннее 95 символов, это очень важно'''


async def generate_poll(chat: Chat, training: Training) -> dict:
    print('started_generating_poll')

    date, time, gym, sport = Date.today(), training.time, training.gym, training.sport

    chat_settings = ChatSettings.objects.get(chat=chat.id)
    GPT_question, GPT_yes, GPT_maybe, GPT_no, emoji = chat_settings.GPT_question, chat_settings.GPT_yes, \
        chat_settings.GPT_maybe, chat_settings.GPT_no, chat_settings.emoji

    # GPT_question, GPT_yes, GPT_maybe, GPT_no, emoji = False, False, False, False, True

    if any([GPT_question, GPT_yes, GPT_maybe, GPT_no]):
        poll_variants = await generate_poll_variants_using_chat_GPT(date=date, time=time, gym=gym, sport=sport)
    else:
        poll_variants = {}

    # print(datetime.datetime.now(), poll_variants)
    poll = choose_poll_variant(poll_variants)

    # print(datetime.datetime.now(), poll)
    if emoji:
        poll = add_emoji(poll)

    if any([GPT_question, GPT_yes, GPT_maybe, GPT_no]):
        if GPT_question:
            poll["question"] += f" \n({date}, {time}, {gym.name})"
        else:
            poll["question"] = generate_default_question(date=date, time=time, gym=gym.name)

        if not GPT_yes:
            poll["options"][0] = generate_default_yes_option(date=date, time=time, gym=gym.name)
        if not GPT_maybe:
            poll["options"][1] = generate_default_maybe_option(date=date, time=time, gym=gym.name)
        if not GPT_no:
            poll["options"][2] = generate_default_no_option(date=date, time=time, gym=gym.name)

    print(poll)
    return poll


async def generate_poll_variants_using_chat_GPT(date: Date, time: Time, gym: Gym, sport: str = "любой",
                                                language: str = 'Русский') -> str:
    prompt = default_prompt
    if sport is not None:
        prompt += f". ВАЖНО: вид спорта - {sport}, поэтому не используй другие виды спорта в генерации. "

    if date or time or gym:
        prompt += f"Кстати тренировка будет {date} в {time} в зале {gym.name} - если захочешь, " \
                  f"можешь использовать эти параметры в ответах. "
    prompt += f"Язык на котором должны быть сгенерированы ответы - {language}"

    headers = {'Content-Type': 'application/json',
               'Authorization': f'Bearer {openai_token}'}
    data = {'model': "gpt-3.5-turbo",
            'messages': [{"role": "user", "content": prompt}],
            'temperature': 1,
            "max_tokens": 2700}
    async with aiohttp.ClientSession() as session:
        while True:
            async with session.post('https://api.openai.com/v1/chat/completions',
                                    headers=headers, json=data, proxy=PROXY_URL) as response:
                answer = json.loads(await response.text())
                if 'error' in answer:
                    print(f'an error occured {gym}: ', answer['error'])
                    await asyncio.sleep(30)
                    continue
                else:
                    try:
                        answer = answer["choices"][0]["message"]["content"]
                        answer = eval(answer)

                        # варианты длиннее чем 99 символов нужно удалить, тг не разрешает их в опросы ставить
                        for key in answer:
                            answer[key] = list(filter(lambda x: len(x) <= 99, answer[key]))

                        if [] in answer.values():
                            # один из варинатов вообще пустой, так нельзя
                            raise ZeroDivisionError

                        break
                    except ZeroDivisionError:
                        print('Перегенерация ответа чата гпт изза слишком длинных вариантов ответа', answer)
                    except Exception as e:
                        logging.error(e)
                        print('Перегенерация ответа чата гпт изза ошибки декодирования')
    return answer


def choose_poll_variant(poll_variants: dict) -> dict:
    # конструкция poll_variants.get("ключ", ["..."]) нужна,
    # чтобы даже если этого ключа нет в словаре, опрос не поломался
    question = random.choice(poll_variants.get("question", ["Идете сегодня на тренировку"]))
    yes_option = random.choice(poll_variants.get("yes", ["Планирую"]))
    maybe_option = random.choice(poll_variants.get("maybe", ["Возможно"]))
    no_option = random.choice(poll_variants.get("no", ["Нет("]))

    return {"question": question, "options": [yes_option, maybe_option, no_option]}


def add_emoji(poll_variants: dict) -> dict:
    emoji_variants = ["✅🌀💤",
                      "🥳🧐🫡",
                      "👍✌️👋",
                      "😎😐🫥",
                      "❤️❓💔",
                      "💯❓⁉️", ]
    em = random.choice(emoji_variants)

    poll_variants["options"][0] = em[0] + poll_variants["options"][0]
    poll_variants["options"][1] = em[1] + poll_variants["options"][1]
    poll_variants["options"][2] = em[2] + poll_variants["options"][2]

    return poll_variants


def generate_default_question(date: Date, time: Time, gym: str) -> str:
    templates = [f"Прийдете {date} в {time} на тренировку в {gym}?",
                 f"Как насчет тренировки в {gym} ({date} в {time})?",
                 f"Перекличка на тренировку в {gym} ({date} в {time})?",
                 f"Какие планы на вечер {date}? Есть опция собраться в {gym} в {time}"]

    return random.choice(templates)


def generate_default_yes_option(date: Date, time: Time, gym: str) -> str:
    templates = [f"Тренируюсь в {gym}",
                 f"Прийду",
                 f"+1",
                 f"Поддержу тренировку своим присутствием"]

    return random.choice(templates)


def generate_default_no_option(date: Date, time: Time, gym: str) -> str:
    templates = [f"Не прийду",
                 f"Занят чем-то бессмысленным и бесполезным",
                 f"Я ужасный человек и не иду сегодня на тренировку",
                 f"Неправильный вариант ответа",
                 "Нашел причину не идти сегодня (долго искал - пришлось придумать)"]

    return random.choice(templates)


def generate_default_maybe_option(date: Date, time: Time, gym: str) -> str:
    templates = [f"Пока в раздумьях",
                 f"Еще не решил",
                 f"хз",
                 f"Мой выбор между тренировкой и отдыхом зависит от победы апатии или энтузиазма"]

    return random.choice(templates)


async def main():
    # функция для тестирования генерируемых ответов
    db_path = ...
    my_db = DB(db_path)

    telegram_chat_id = 1111
    chat_settings = {"chat_GPT": True, "funny_question": True, "funny_yes": True, "funny_maybe": True,
                     "funny_no": True, "emoji": True}
    date = Date.today()
    time = Time(hour=19, minute=34)
    gym = "Акроритм"
    sport = "Спортивная гимнастика"

    training = {"date": date, "time": time, "gym": gym, "sport": sport}

    my_db.clear_all_tables()
    await my_db.new_chat(telegram_chat_id)
    await my_db.add_answer_alternative(telegram_chat_id=telegram_chat_id, answer_type="question",
                                       answer_value="Придете?")
    await my_db.add_answer_alternative(telegram_chat_id=telegram_chat_id, answer_type="yes", answer_value="Да")
    await my_db.add_answer_alternative(telegram_chat_id=telegram_chat_id, answer_type="maybe", answer_value="Мб")
    await my_db.add_answer_alternative(telegram_chat_id=telegram_chat_id, answer_type="no", answer_value="Нет")

    print(await generate_poll(telegram_chat_id,
                              chat_settings=chat_settings, training=training, db_path=db_path))
    my_db.clear_all_tables()


if __name__ == "__main__":
    main()
