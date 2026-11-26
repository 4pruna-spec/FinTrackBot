import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards.menus import main_menu

from database.db import init_db
from database.goals import init_goals_db
from database.protection import init_protection

from handlers.transactions import router as transactions_router
from handlers.history import router as history_router
from handlers.statistics import router as statistics_router
from handlers.budgets import router as budgets_router
from handlers.debts import router as debts_router
from handlers.goals import router as goals_router
from handlers.balance import router as balance_router
from handlers.errors import handle_error


logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")

dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(
    message: Message,
    state: FSMContext
):
    await state.clear()

    await message.answer(
        "👋 Вітаю у FinTrack!\n\n"
        "💰 Твій особистий фінансовий помічник.\n\n"
        "📊 Бюджет 65/15/20\n"
        "💳 Контроль боргів\n"
        "🎯 Фінансові цілі\n"
        "🛡️ Захист накопичень\n\n"
        "Обери необхідну дію 👇",
        reply_markup=main_menu
    )


@dp.errors()
async def global_error_handler(
    event,
    state: FSMContext = None
):
    if state is not None:
        await state.clear()

    return await handle_error(event)


async def main():

    if not TOKEN:
        raise ValueError("Не знайдено BOT_TOKEN!")

    init_db()
    init_goals_db()
    init_protection()

    dp.include_router(history_router)
    dp.include_router(statistics_router)
    dp.include_router(budgets_router)
    dp.include_router(balance_router)
    dp.include_router(debts_router)
    dp.include_router(goals_router)
    dp.include_router(transactions_router)

    bot = Bot(token=TOKEN)

    logging.info("FinTrackBot успішно запущено!")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
