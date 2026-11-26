from decimal import Decimal, InvalidOperation

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.goals import (
    add_goal,
    get_goals,
    get_goal,
    deposit_goal,
    withdraw_goal,
    get_total_savings,
    get_goal_history
)

from keyboards.goals import goals_menu, goal_types_keyboard

router = Router()


class Goal(StatesGroup):
    goal_type = State()
    name = State()
    target = State()
    select_goal = State()
    amount = State()


GOAL_TYPES = (
    "🛡️ Фінансова подушка",
    "🚗 Автомобіль",
    "🏠 Житло",
    "📈 Інвестиції",
    "✈️ Подорож",
    "🎯 Інша ціль"
)


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


@router.message(StateFilter(None), F.text == "🎯 Накопичення")
async def open_goals(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        "🎯 Управління накопиченнями\n\n"
        f"💰 Загалом накопичено: "
        f"{money(get_total_savings(message.from_user.id))}\n\n"
        "Обери необхідну дію:",
        reply_markup=goals_menu
    )


@router.message(
    StateFilter(
        Goal.goal_type,
        Goal.name,
        Goal.target,
        Goal.select_goal,
        Goal.amount
    ),
    F.text == "❌ Скасувати"
)
@router.message(
    StateFilter(
        Goal.goal_type,
        Goal.name,
        Goal.target,
        Goal.select_goal,
        Goal.amount
    ),
    Command("cancel")
)
async def cancel_goal(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        "❌ Операцію скасовано.",
        reply_markup=goals_menu
    )


@router.message(F.text == "➕ Створити ціль")
async def create_goal(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(Goal.goal_type)

    await message.answer(
        "🎯 Обери тип фінансової цілі:",
        reply_markup=goal_types_keyboard
    )


@router.message(Goal.goal_type)
async def select_type(message: Message, state: FSMContext):
    if message.text not in GOAL_TYPES:
        await message.answer("Обери тип цілі кнопкою.")
        return

    await state.update_data(goal_type=message.text)
    await state.set_state(Goal.name)

    await message.answer(
        "✏️ Введи назву своєї цілі:"
    )


@router.message(Goal.name)
async def goal_name(message: Message, state: FSMContext):
    name = (message.text or "").strip()

    if not name or len(name) > 100:
        await message.answer(
            "Введи назву від 1 до 100 символів."
        )
        return

    await state.update_data(name=name)
    await state.set_state(Goal.target)

    await message.answer(
        "💰 Яку суму хочеш накопичити в гривнях?"
    )


@router.message(Goal.target)
async def goal_target(message: Message, state: FSMContext):
    amount = parse_amount(message.text)

    if amount is None:
        await message.answer("⚠️ Введи коректну суму.")
        return

    data = await state.get_data()

    add_goal(
        message.from_user.id,
        data["name"],
        data["goal_type"],
        amount
    )

    await state.clear()

    await message.answer(
        "✅ Фінансову ціль створено!\n\n"
        f"🎯 Назва: {data['name']}\n"
        f"💰 Ціль: {money(amount)}\n"
        "💵 Накопичено: 0 грн",
        reply_markup=goals_menu
    )


@router.message(F.text == "📋 Мої накопичення")
async def list_goals(message: Message, state: FSMContext):
    await state.clear()

    goals = get_goals(message.from_user.id)

    if not goals:
        await message.answer(
            "📭 У тебе поки немає фінансових цілей.",
            reply_markup=goals_menu
        )
        return

    for goal_id, name, goal_type, target, saved in goals:

        percent = saved * 100 // target
        filled = min(10, saved * 10 // target)

        bar = "█" * filled + "░" * (10 - filled)

        remaining = max(0, target - saved)

        status = (
            "🎉 Ціль досягнуто!"
            if saved >= target
            else "⏳ У процесі"
        )

        await message.answer(
            f"🎯 #{goal_id} — {name}\n"
            f"Тип: {goal_type}\n"
            f"Ціль: {money(target)}\n"
            f"Накопичено: {money(saved)}\n"
            f"Залишилось: {money(remaining)}\n\n"
            f"{bar} {percent}%\n"
            f"{status}"
        )

    await message.answer(
        "💰 Загалом накопичено: "
        f"{money(get_total_savings(message.from_user.id))}",
        reply_markup=goals_menu
    )


@router.message(F.text == "💵 Поповнити ціль")
async def start_deposit(message: Message, state: FSMContext):
    await start_operation(message, state, "deposit")


@router.message(F.text == "💸 Зняти кошти")
async def start_withdraw(message: Message, state: FSMContext):
    await start_operation(message, state, "withdraw")


async def start_operation(message, state, operation):
    await state.clear()

    goals = get_goals(message.from_user.id)

    if operation == "withdraw":
        goals = [goal for goal in goals if goal[4] > 0]

    if not goals:
        await message.answer(
            "📭 Немає доступних цілей для цієї операції.",
            reply_markup=goals_menu
        )
        return

    for goal_id, name, goal_type, target, saved in goals:
        await message.answer(
            f"#{goal_id} — {name}\n"
            f"Накопичено: {money(saved)}\n"
            f"Ціль: {money(target)}"
        )

    await state.update_data(operation=operation)
    await state.set_state(Goal.select_goal)

    await message.answer(
        "Введи номер фінансової цілі:"
    )


@router.message(Goal.select_goal)
async def select_goal(message: Message, state: FSMContext):
    try:
        goal_id = int(message.text or "")
    except ValueError:
        await message.answer("Введи номер цілі цифрами.")
        return

    goal = get_goal(message.from_user.id, goal_id)

    if not goal:
        await message.answer("⚠️ Ціль не знайдено.")
        return

    await state.update_data(goal_id=goal_id)
    await state.set_state(Goal.amount)

    await message.answer(
        f"🎯 {goal[1]}\n\n"
        "💵 Введи суму операції в гривнях:"
    )


@router.message(Goal.amount)
async def process_amount(message: Message, state: FSMContext):
    amount = parse_amount(message.text)

    if amount is None:
        await message.answer("⚠️ Введи коректну суму.")
        return

    data = await state.get_data()

    user_id = message.from_user.id
    goal_id = data["goal_id"]

    if data["operation"] == "deposit":
        success = deposit_goal(user_id, goal_id, amount)
        action = "Поповнено"
    else:
        success = withdraw_goal(user_id, goal_id, amount)
        action = "Знято"

    if not success:
        await message.answer(
            "⚠️ Недостатньо коштів або ціль недоступна."
        )
        return

    goal = get_goal(user_id, goal_id)

    await state.clear()

    text = (
        "✅ Операцію виконано!\n\n"
        f"🎯 Ціль: {goal[1]}\n"
        f"💵 {action}: {money(amount)}\n"
        f"💰 Накопичено: {money(goal[4])}\n"
        f"Залишилось: {money(max(0, goal[3] - goal[4]))}"
    )

    if goal[4] >= goal[3]:
        text += "\n\n🎉 Фінансову ціль досягнуто!"

    await message.answer(
        text,
        reply_markup=goals_menu
    )


@router.message(F.text == "📜 Історія накопичень")
async def goals_history(message: Message, state: FSMContext):
    await state.clear()

    history = get_goal_history(message.from_user.id)

    if not history:
        await message.answer(
            "📭 Історія поки порожня.",
            reply_markup=goals_menu
        )
        return

    text = "📜 Історія накопичень:\n\n"

    for name, operation, amount, date in history:

        action = (
            "➕ Поповнення"
            if operation == "deposit"
            else "➖ Зняття"
        )

        text += (
            f"🎯 {name}\n"
            f"{action}: {money(amount)}\n"
            f"📅 {date[:10]}\n\n"
        )

    await message.answer(
        text,
        reply_markup=goals_menu
    )
