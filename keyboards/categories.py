from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

INCOME_CATEGORIES = [
    "💼 Зарплата",
    "💵 Аванс",
    "🏪 Бізнес",
    "💻 Підробіток",
    "🎁 Подарунок",
    "💰 Інший дохід"
]

EXPENSE_CATEGORIES = {
    "🛒 Продукти": "needs",
    "🏠 Комунальні послуги": "needs",
    "🚗 Транспорт": "needs",
    "📱 Зв'язок": "needs",
    "💊 Здоров'я": "needs",
    "🎓 Освіта": "needs",
    "🐈 Домашні тварини": "needs",
    "🏡 Побут": "needs",

    "🎮 Розваги": "personal",
    "☕ Кафе та ресторани": "personal",
    "👕 Одяг": "personal",
    "🎁 Подарунки": "personal",
    "💻 Техніка": "personal",
    "🛍️ Інше": "personal",

    "💳 Погашення боргів": "goals",
    "🛡️ Фінансова подушка": "goals",
    "🎯 Накопичення": "goals",
    "📈 Інвестиції": "goals"
}


def create_keyboard(categories):
    buttons = [
        KeyboardButton(text=category)
        for category in categories
    ]

    rows = [
        buttons[i:i + 2]
        for i in range(0, len(buttons), 2)
    ]

    rows.append([
        KeyboardButton(text="❌ Скасувати")
    ])

    return ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True
    )


income_keyboard = create_keyboard(INCOME_CATEGORIES)

expense_keyboard = create_keyboard(EXPENSE_CATEGORIES)
