from decimal import Decimal, InvalidOperation

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import add_transaction, get_balance
from keyboards.menus import main_menu
from keyboards.categories import (
    INCOME_CATEGORIES,
    EXPENSE_CATEGORIES,
    income_keyboard,
    expense_keyboard
)

router = Router()


class Transaction(StatesGroup):
    amount = State()
    category = State()


@router.message(F.text == "💰 Мій баланс")
async def balance(message: Message, state: FSMContext):
    await state.clear()

    amount = Decimal(
        get_balance(message.from_user.id)
    ) / 100

    await message.answer(
        f"💰 Твій баланс: {amount:.2f} грн",
        reply_markup=main_menu
    )


@router.message(F.text == "➕ Додати дохід")
async def income(message: Message, state: FSMContext):
    await state.clear()
    await state.update_data(kind="income")
    await state.set_state(Transaction.amount)

    await message.answer(
        "💵 Введи суму доходу в гривнях:"
    )


@router.message(F.text == "➖ Додати витрату")
async def expense(message: Message, state: FSMContext):
    await state.clear()
    await state.update_data(kind="expense")
    await state.set_state(Transaction.amount)

    await message.answer(
        "💸 Введи суму витрати в гривнях:"
    )


@router.message(Command("cancel"))
@router.message(F.text == "❌ Скасувати")
async def cancel(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        "❌ Операцію скасовано.",
        reply_markup=main_menu
    )


@router.message(Transaction.amount)
async def enter_amount(message: Message, state: FSMContext):
    try:
        amount = Decimal(
            (message.text or "").strip().replace(",", ".")
        )

        if not amount.is_finite():
            raise ValueError

        if amount <= 0 or amount > 1000000000:
            raise ValueError

        if amount * 100 != (amount * 100).to_integral_value():
            raise ValueError

        amount_kopecks = int(amount * 100)

    except (InvalidOperation, ValueError):
        await message.answer(
            "⚠️ Введи коректну суму. Наприклад: 150.50"
        )
        return

    await state.update_data(amount=amount_kopecks)

    data = await state.get_data()

    keyboard = (
        income_keyboard
        if data["kind"] == "income"
        else expense_keyboard
    )

    await state.set_state(Transaction.category)

    await message.answer(
        "📂 Обери категорію:",
        reply_markup=keyboard
    )


@router.message(Transaction.category)
async def save_transaction(
    message: Message,
    state: FSMContext
):
    data = await state.get_data()

    kind = data["kind"]
    amount = data["amount"]
    category = message.text

    categories = (
        INCOME_CATEGORIES
        if kind == "income"
        else EXPENSE_CATEGORIES
    )

    if category not in categories:
        await message.answer(
            "⚠️ Обери категорію за допомогою кнопок."
        )
        return

    add_transaction(
        message.from_user.id,
        kind,
        amount,
        category
    )

    await state.clear()

    balance = Decimal(
        get_balance(message.from_user.id)
    ) / 100

    text = (
        "✅ Операцію збережено!\n\n"
        f"💵 Сума: {Decimal(amount) / 100:.2f} грн\n"
        f"📂 Категорія: {category}\n"
    )

    if kind == "expense":
        groups = {
            "needs": "Основні витрати (65%)",
            "personal": "Особисті витрати (15%)",
            "goals": "Фінансові цілі (20%)"
        }

        group = groups[EXPENSE_CATEGORIES[category]]

        text += f"📊 Група бюджету: {group}\n"

    text += f"\n💰 Баланс: {balance:.2f} грн"

    await message.answer(
        text,
        reply_markup=main_menu
    )
