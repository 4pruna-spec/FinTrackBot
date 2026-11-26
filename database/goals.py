import sqlite3

from database.db import DB_NAME


def init_goals_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                goal_type TEXT NOT NULL,
                target_amount INTEGER NOT NULL
                    CHECK(target_amount > 0),
                saved_amount INTEGER NOT NULL DEFAULT 0
                    CHECK(saved_amount >= 0),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS goal_operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                goal_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                amount INTEGER NOT NULL CHECK(amount > 0),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (goal_id) REFERENCES goals(id)
            )
        """)


def add_goal(user_id, name, goal_type, target_amount):
    if target_amount <= 0:
        raise ValueError("Некоректна сума цілі")

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute("""
            INSERT INTO goals
            (user_id, name, goal_type, target_amount)
            VALUES (?, ?, ?, ?)
        """, (
            user_id,
            name,
            goal_type,
            target_amount
        ))

        return cursor.lastrowid


def get_goals(user_id):
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute("""
            SELECT id, name, goal_type,
                   target_amount, saved_amount
            FROM goals
            WHERE user_id = ?
            ORDER BY id DESC
        """, (user_id,)).fetchall()


def get_goal(user_id, goal_id):
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute("""
            SELECT id, name, goal_type,
                   target_amount, saved_amount
            FROM goals
            WHERE user_id = ? AND id = ?
        """, (user_id, goal_id)).fetchone()


def deposit_goal(user_id, goal_id, amount):
    if amount <= 0:
        return False

    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("BEGIN IMMEDIATE")

        goal = conn.execute("""
            SELECT id
            FROM goals
            WHERE id = ? AND user_id = ?
        """, (goal_id, user_id)).fetchone()

        if not goal:
            return False

        balance = conn.execute("""
            SELECT COALESCE(SUM(
                CASE
                    WHEN type = 'income' THEN amount
                    WHEN type = 'expense' THEN -amount
                    ELSE 0
                END
            ), 0)
            FROM transactions
            WHERE user_id = ?
        """, (user_id,)).fetchone()[0]

        saved = conn.execute("""
            SELECT COALESCE(SUM(saved_amount), 0)
            FROM goals
            WHERE user_id = ?
        """, (user_id,)).fetchone()[0]

        if amount > balance - saved:
            return False

        conn.execute("""
            UPDATE goals
            SET saved_amount = saved_amount + ?
            WHERE id = ? AND user_id = ?
        """, (amount, goal_id, user_id))

        conn.execute("""
            INSERT INTO goal_operations
            (user_id, goal_id, type, amount)
            VALUES (?, ?, 'deposit', ?)
        """, (user_id, goal_id, amount))

    return True


def withdraw_goal(user_id, goal_id, amount):
    if amount <= 0:
        return False

    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("BEGIN IMMEDIATE")

        goal = conn.execute("""
            SELECT saved_amount
            FROM goals
            WHERE id = ? AND user_id = ?
        """, (goal_id, user_id)).fetchone()

        if not goal or amount > goal[0]:
            return False

        conn.execute("""
            UPDATE goals
            SET saved_amount = saved_amount - ?
            WHERE id = ? AND user_id = ?
        """, (amount, goal_id, user_id))

        conn.execute("""
            INSERT INTO goal_operations
            (user_id, goal_id, type, amount)
            VALUES (?, ?, 'withdraw', ?)
        """, (user_id, goal_id, amount))

    return True


def get_total_savings(user_id):
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute("""
            SELECT COALESCE(SUM(saved_amount), 0)
            FROM goals
            WHERE user_id = ?
        """, (user_id,)).fetchone()[0]


def get_goal_history(user_id, limit=10):
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute("""
            SELECT goals.name,
                   goal_operations.type,
                   goal_operations.amount,
                   goal_operations.created_at
            FROM goal_operations
            JOIN goals
                ON goals.id = goal_operations.goal_id
            WHERE goal_operations.user_id = ?
                AND goals.user_id = ?
            ORDER BY goal_operations.id DESC
            LIMIT ?
        """, (user_id, user_id, limit)).fetchall()


def get_monthly_savings(user_id):
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute("""
            SELECT COALESCE(SUM(
                CASE
                    WHEN type = 'deposit' THEN amount
                    WHEN type = 'withdraw' THEN -amount
                    ELSE 0
                END
            ), 0)
            FROM goal_operations
            WHERE user_id = ?
            AND strftime('%Y-%m', created_at)
                = strftime('%Y-%m', 'now')
        """, (user_id,)).fetchone()[0]
