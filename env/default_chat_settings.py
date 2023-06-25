import os.path
from datetime import time as Time, datetime as Datetime, timedelta

# TODO настроить задание имени файла хэшом
DEFAULT_WELCOME_MEME_PATH = os.path.join('media', 'welcome_memes', 'default.jpg')
DEFAULT_AUTO_POLL_FLAG = 1
DEFAULT_GPT_QUESTION = 1
DEFAULT_GPT_YES = 1
DEFAULT_GPT_MAYBE = 1
DEFAULT_GPT_NO = 1
DEFAULT_CHAT_EMOJI_FLAG = 1
DEFAULT_EVERYONE_IS_ADMIN = 0
DEFAULT_LANGUAGE = 'Русский'

DEFAULT_POLL_SEND_TIME = Time(hour=7, minute=30)
# DEFAULT_POLL_SEND_TIME = (Datetime.now() + timedelta(minutes=1)).time()
print(f"DEFAULT_POLL_SEND_TIME = {DEFAULT_POLL_SEND_TIME}")
