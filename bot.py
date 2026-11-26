import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards.menus import main_menu
from database.db import init_db

from handlers.transactions import router as transactions_router
from handlers.history import router as history_router
from handlers.statistics import router as statistics_router

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")

dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        "👋 Вітаю у FinTrack!\n\n"
        "💰 Твій особистий фінансовий помічник.\n\n"
        "Обери необхідну дію в меню нижче 👇",
        reply_markup=main_menu
    )


async def main():
    if not TOKEN:
        raise ValueError("Не знайдено BOT_TOKEN!")

    init_db()

    dp.include_router(history_router)
    dp.include_router(statistics_router)
    dp.include_router(transactions_router)

    bot = Bot(token=TOKEN)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
