
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

# Налаштування журналу
logging.basicConfig(level=logging.INFO)

# Токен буде доданий через секрети GitHub або змінні середовища
import os

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "👋 Привіт! Я FinTrack — твій особистий "
        "фінансовий помічник.\n\n"
        "💰 Тут ти зможеш вести облік доходів "
        "та витрат.\n\n"
        "Незабаром почнемо!"
    )


async def main():
    if not TOKEN:
        raise ValueError("Не знайдено BOT_TOKEN!")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
