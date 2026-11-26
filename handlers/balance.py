from decimal import Decimal

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from services.balance import calculate_balance
from keyboards.menus import main_menu

router = Router()


def money(amount):
    return f"{Decimal(amount) / 100:.2f} грн"


@router.message(F.text == "💰 Мій баланс")
async def show_balance(message: Message, state: FSMContext):
    await state.clear()

    balance = calculate_balance(message.from_user.id)

    await message.answer(
        "💰 Твій фінансовий баланс\n\n"
        f"💵 Доступні кошти: "
        f"{money(balance['available'])}\n\n"
        f"🎯 Накопичення: "
        f"{money(balance['savings'])}\n\n"
        f"🏦 Загальна сума коштів: "
        f"{money(balance['total'])}",
        reply_markup=main_menu
    )
