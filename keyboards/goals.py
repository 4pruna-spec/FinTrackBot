from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


goals_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📋 Мої накопичення")
        ],
        [
            KeyboardButton(text="➕ Створити ціль")
        ],
        [
            KeyboardButton(text="💵 Поповнити ціль"),
            KeyboardButton(text="💸 Зняти кошти")
        ],
        [
            KeyboardButton(text="📜 Історія накопичень")
        ],
        [
            KeyboardButton(text="🔙 Головне меню")
        ]
    ],
    resize_keyboard=True
)


goal_types_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🛡️ Фінансова подушка")
        ],
        [
            KeyboardButton(text="🚗 Автомобіль"),
            KeyboardButton(text="🏠 Житло")
        ],
        [
            KeyboardButton(text="📈 Інвестиції"),
            KeyboardButton(text="✈️ Подорож")
        ],
        [
            KeyboardButton(text="🎯 Інша ціль")
        ],
        [
            KeyboardButton(text="❌ Скасувати")
        ]
    ],
    resize_keyboard=True
)
