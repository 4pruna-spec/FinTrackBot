import sqlite3

from database.db import DB_NAME


def init_protection():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TRIGGER IF NOT EXISTS protect_savings
            BEFORE INSERT ON transactions
            WHEN NEW.type = 'expense'
            BEGIN

                SELECT CASE
                    WHEN NEW.amount > (
                        SELECT COALESCE(SUM(
                            CASE
                                WHEN type = 'income'
                                    THEN amount
                                WHEN type = 'expense'
                                    THEN -amount
                                ELSE 0
                            END
                        ), 0)
                        FROM transactions
                        WHERE user_id = NEW.user_id
                    ) - (
                        SELECT COALESCE(SUM(saved_amount), 0)
                        FROM goals
                        WHERE user_id = NEW.user_id
                    )
                    THEN RAISE(
                        ABORT,
                        'INSUFFICIENT_AVAILABLE_FUNDS'
                    )
                END;

            END
        """)
