import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards.menus import main_menu

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")

dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "👋 Вітаю у FinTrack!\n\n"
        "💰 Твій особистий фінансовий помічник.\n\n"
        "Обери необхідну дію в меню нижче 👇",
        reply_markup=main_menu
    )


async def main():
    if not TOKEN:
        raise ValueError("Не знайдено BOT_TOKEN!")

    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
