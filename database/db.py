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
