from django.core.management.base import BaseCommand
import asyncio
from aiogram import Bot, Dispatcher

import telegram_bot.settings
from telegram_bot.bot.routers import zaek_routers
from django.conf import settings


class Command(BaseCommand):
    help = 'Run Telegram bot'

    def handle(self, *args, **options):
        bot = Bot(token=telegram_bot.settings.BOT_TOKEN)
        dp = Dispatcher()
        dp.include_router(zaek_routers)

        async def start():
            await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(bot)

        asyncio.run(start())