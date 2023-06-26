from django.core.management.base import BaseCommand
import asyncio
from bot.create_bot import dp
import bot.bot_logics

import logging
from env.env import LOG_PATH, LOGGING_LEVEL
from utils.scheduling import scheduler, start_scheduling

logging.basicConfig(level=LOGGING_LEVEL, filename=LOG_PATH, filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s", encoding='utf-8')


class Command(BaseCommand):
    help = '... running bot and schedule...'

    def handle(self, *args, **options):
        asyncio.run(self.main())

    async def main(self):
        try:
            scheduler.start()
            start_scheduling()
            await dp.start_polling()

        except Exception as e:
            raise e
