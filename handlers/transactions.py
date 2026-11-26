from decimal import Decimal, InvalidOperation

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import add_transaction

from services.balance import calculate_balance
from services.validation import check_available_funds

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


def money(amount):
    return f"{Decimal(amount) / 100:.2f} грн"


def parse_amount(text):
    try:
        amount = Decimal(
            (text or "").strip().replace(",", ".")
        )

        if not amount.is_finite():
            return None

        if amount <= 0 or amount > 1000000000:
            return None

        cents = amount * 100

        if cents != cents.to_integral_value():
            return None

        return int(cents)

    except (InvalidOperation, ValueError):
        return None


@router.message(Command("cancel"))
@router.message(F.text == "❌ Скасувати")
async def cancel(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        "❌ Операцію скасовано.",
        reply_markup=main_menu
    )


@router.message(F.text == "➕ Додати дохід")
async def add_income(message: Message, state: FSMContext):
    await state.clear()
    await state.update_data(kind="income")
    await state.set_state(Transaction.amount)

    await message.answer(
        "💵 Введи суму доходу в гривнях:"
    )


@router.message(F.text == "➖ Додати витрату")
async def add_expense(message: Message, state: FSMContext):
    await state.clear()
    await state.update_data(kind="expense")
    await state.set_state(Transaction.amount)

    balance = calculate_balance(message.from_user.id)

    await message.answer(
        f"💰 Доступно: {money(balance['available'])}\n\n"
        "💸 Введи суму витрати в гривнях:"
    )


@router.message(Transaction.amount)
async def process_amount(message: Message, state: FSMContext):
    amount = parse_amount(message.text)

    if amount is None:
        await message.answer(
            "⚠️ Введи коректну суму."
        )
        return

    data = await state.get_data()
    kind = data["kind"]

    if kind == "expense":
        allowed, error = check_available_funds(
            message.from_user.id,
            amount
        )

        if not allowed:
            await message.answer(error)
            return

    await state.update_data(amount=amount)
    await state.set_state(Transaction.category)

    keyboard = (
        income_keyboard
        if kind == "income"
        else expense_keyboard
    )

    await message.answer(
        "📂 Обери категорію:",
        reply_markup=keyboard
    )


@router.message(Transaction.category)
async def process_category(message: Message, state: FSMContext):
    data = await state.get_data()

    kind = data["kind"]
    amount = data["amount"]
    category = message.text
    user_id = message.from_user.id

    categories = (
        INCOME_CATEGORIES
        if kind == "income"
        else EXPENSE_CATEGORIES
    )

    if category not in categories:
        await message.answer(
            "⚠️ Обери категорію кнопкою."
        )
        return

    if kind == "expense":

        if category in (
            "💳 Погашення боргів",
            "🛡️ Фінансова подушка",
            "🎯 Накопичення"
        ):
            await state.clear()

            await message.answer(
                "⚠️ Для цієї операції використовуй "
                "розділ «Борги» або «Накопичення».\n\n"
                "Це допоможе уникнути подвійного обліку.",
                reply_markup=main_menu
            )
            return

        allowed, error = check_available_funds(
            user_id,
            amount
        )

        if not allowed:
            await state.set_state(Transaction.amount)

            await message.answer(
                error + "\n\nВведи нову суму."
            )
            return

    add_transaction(
        user_id,
        kind,
        amount,
        category
    )

    await state.clear()

    balance = calculate_balance(user_id)

    action = (
        "➕ Дохід додано"
        if kind == "income"
        else "➖ Витрату додано"
    )

    text = (
        f"✅ {action}!\n\n"
        f"💵 Сума: {money(amount)}\n"
        f"📂 Категорія: {category}\n"
    )

    if kind == "expense":
        group = EXPENSE_CATEGORIES.get(category)

        groups = {
            "needs": "🏠 Основні витрати — 65%",
            "personal": "🛍️ Особисті витрати — 15%",
            "goals": "🎯 Фінансові цілі — 20%"
        }

        text += (
            f"📊 Бюджет: "
            f"{groups.get(group, 'Без групи')}\n"
        )

    text += (
        "\n━━━━━━━━━━━━━━\n\n"
        f"💰 Доступно: {money(balance['available'])}\n"
        f"🎯 Накопичення: {money(balance['savings'])}\n"
        f"🏦 Загалом: {money(balance['total'])}"
    )

    await message.answer(
        text,
        reply_markup=main_menu
    )
