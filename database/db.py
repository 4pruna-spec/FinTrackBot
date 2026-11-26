import sqlite3

DB_NAME = "fintrack.db"


def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                amount INTEGER NOT NULL CHECK(amount > 0),
                category TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS debts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                currency TEXT NOT NULL,
                total_amount INTEGER NOT NULL CHECK(total_amount > 0),
                paid_amount INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS debt_payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                debt_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                amount INTEGER NOT NULL CHECK(amount > 0),
                amount_uah INTEGER NOT NULL CHECK(amount_uah > 0),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (debt_id) REFERENCES debts(id)
            )
        """)


def add_transaction(user_id, type, amount,
                    category=None, description=None):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            INSERT INTO transactions
            (user_id, type, amount, category, description)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, type, amount,
              category, description))


def get_balance(user_id):
    with sqlite3.connect(DB_NAME) as conn:
        result = conn.execute("""
            SELECT COALESCE(SUM(
                CASE
                    WHEN type = 'income' THEN amount
                    WHEN type = 'expense' THEN -amount
                    ELSE 0
                END
            ), 0)
            FROM transactions
            WHERE user_id = ?
        """, (user_id,)).fetchone()

    return result[0]


def get_transactions(user_id, limit=10):
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute("""
            SELECT type, amount, category,
                   description, created_at
            FROM transactions
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
        """, (user_id, limit)).fetchall()


def get_monthly_statistics(user_id):
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute("""
            SELECT
                COALESCE(SUM(
                    CASE WHEN type = 'income'
                    THEN amount ELSE 0 END
                ), 0),
                COALESCE(SUM(
                    CASE WHEN type = 'expense'
                    THEN amount ELSE 0 END
                ), 0)
            FROM transactions
            WHERE user_id = ?
            AND strftime('%Y-%m', created_at)
                = strftime('%Y-%m', 'now')
        """, (user_id,)).fetchone()


def get_monthly_expenses(user_id):
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute("""
            SELECT category, SUM(amount)
            FROM transactions
            WHERE user_id = ?
            AND type = 'expense'
            AND strftime('%Y-%m', created_at)
                = strftime('%Y-%m', 'now')
            GROUP BY category
        """, (user_id,)).fetchall()


def add_debt(user_id, name, currency, amount):
    if currency not in ("UAH", "USD", "EUR"):
        raise ValueError("Непідтримувана валюта")

    if amount <= 0:
        raise ValueError("Некоректна сума боргу")

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute("""
            INSERT INTO debts
            (user_id, name, currency, total_amount)
            VALUES (?, ?, ?, ?)
        """, (user_id, name, currency, amount))

        return cursor.lastrowid


def get_debts(user_id):
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute("""
            SELECT id, name, currency,
                   total_amount, paid_amount
            FROM debts
            WHERE user_id = ?
            ORDER BY id DESC
        """, (user_id,)).fetchall()


def get_debt(user_id, debt_id):
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute("""
            SELECT id, name, currency,
                   total_amount, paid_amount
            FROM debts
            WHERE user_id = ? AND id = ?
        """, (user_id, debt_id)).fetchone()


def pay_debt(user_id, debt_id, amount, amount_uah):
    if amount <= 0 or amount_uah <= 0:
        return False

    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("BEGIN IMMEDIATE")

        debt = conn.execute("""
            SELECT name, currency,
                   total_amount, paid_amount
            FROM debts
            WHERE id = ? AND user_id = ?
        """, (debt_id, user_id)).fetchone()

        if not debt:
            return False

        name, currency, total, paid = debt

        if amount > total - paid:
            return False

        if currency == "UAH" and amount != amount_uah:
            return False

        conn.execute("""
            UPDATE debts
            SET paid_amount = paid_amount + ?
            WHERE id = ? AND user_id = ?
        """, (amount, debt_id, user_id))

        conn.execute("""
            INSERT INTO debt_payments
            (debt_id, user_id, amount, amount_uah)
            VALUES (?, ?, ?, ?)
        """, (debt_id, user_id, amount, amount_uah))

        conn.execute("""
            INSERT INTO transactions
            (user_id, type, amount, category, description)
            VALUES (?, ?, ?, ?, ?)
        """, (
            user_id,
            "expense",
            amount_uah,
            "💳 Погашення боргів",
            name
        ))

    return True


def get_debt_payments(user_id, limit=10):
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute("""
            SELECT debts.name, debts.currency,
                   debt_payments.amount,
                   debt_payments.amount_uah,
                   debt_payments.created_at
            FROM debt_payments
            JOIN debts ON debts.id = debt_payments.debt_id
            WHERE debt_payments.user_id = ?
            AND debts.user_id = ?
            ORDER BY debt_payments.id DESC
            LIMIT ?
        """, (user_id, user_id, limit)).fetchall()
