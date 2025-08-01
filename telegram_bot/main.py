from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
import logging
import asyncio


import os
import sys
import django
from pathlib import Path



def init_django():
    BASE_DIR = Path(__file__).resolve().parent.parent
    sys.path.append(str(BASE_DIR))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()

init_django()

from telegram_bot.settings import BOT_TOKEN
from .bot.routers import (zaek_routers)

BOT_TOKEN = BOT_TOKEN

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

dp = Dispatcher()
logging.basicConfig(level=logging.INFO)



@dp.message(Command("start","menu"))
async def cmd_start(message: types.Message):
    await message.answer("Меню бота ", reply_markup=main_menu_kb())


def main_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text='Пользователь', callback_data='user')
    builder.button(text='Вопрос', callback_data='question')
    builder.adjust(1)
    return builder.as_markup()

dp.include_routers(zaek_routers)

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
