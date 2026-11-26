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
