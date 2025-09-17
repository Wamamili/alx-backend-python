#!/usr/bin/env python3
import sqlite3
import functools


# Decorator to automatically handle DB connection
def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            result = func(conn, *args, **kwargs)  # pass connection
        finally:
            conn.close()  # ensure connection is always closed
        return result
    return wrapper


# Decorator to manage transactions (commit/rollback)
def transactional(func):
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            result = func(conn, *args, **kwargs)
            conn.commit()  # commit if no error
            return result
        except Exception as e:
            conn.rollback()  # rollback on error
            print(f"[ERROR] Transaction failed: {e}")
            raise
    return wrapper


@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))


if __name__ == "__main__":
    # Update user's email with automatic transaction handling
    update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')
    print(" User email updated successfully")
