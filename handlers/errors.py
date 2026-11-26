import logging
import sqlite3

from aiogram import Router
from aiogram.types import ErrorEvent

from keyboards.menus import main_menu

router = Router()

logger = logging.getLogger(__name__)


@router.errors()
async def handle_error(event: ErrorEvent):
    error = event.exception

    if (
        isinstance(error, sqlite3.IntegrityError)
        and "INSUFFICIENT_AVAILABLE_FUNDS" in str(error)
    ):
        message = event.update.message

        if message:
            await message.answer(
                "⚠️ Недостатньо доступних коштів!\n\n"
                "🔒 Твої накопичення захищені.\n\n"
                "Зменш суму операції або зніми "
                "необхідні кошти з накопичень.\n\n"
                "Операцію не збережено.",
                reply_markup=main_menu
            )

        return True

    logger.error(
        "Помилка FinTrackBot",
        exc_info=(
            type(error),
            error,
            error.__traceback__
        )
    )

    return False
