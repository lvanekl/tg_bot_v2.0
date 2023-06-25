import os
from datetime import time as Time, datetime as Datetime, timedelta
import logging

telegram_token = ""
openai_token = ""

NEW_CHAT_MEME_PATH = "media/new_chat_meme.jpg"

TEST_DB_PATH = 'db/test.sqlite3'
DB_PATH = 'db/db.sqlite3'
LOG_PATH = os.path.join('logs', 'log.log')
LOGGING_LEVEL = logging.INFO

DEVELOPER_TELEGRAM_ID = 409733921
TRAININGS_CHECK_RUN_TIME = Time(hour=2, minute=3)
# TRAININGS_CHECK_RUN_TIME = (Datetime.now()+timedelta(seconds=5)).time()
print(f"TRAININGS_CHECK_RUN_TIME = {TRAININGS_CHECK_RUN_TIME}")
BOT_USERNAME = "@Igor2_bot"
