#!/usr/bin/env python3
"""
Task 0: Custom Class-Based Context Manager for Database Connection
"""

import sqlite3


class DatabaseConnection:
    """Custom context manager for handling SQLite database connections"""

    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None

    def __enter__(self):
        """Open database connection when entering context"""
        self.conn = sqlite3.connect(self.db_name)
        return self.conn

    def __exit__(self, exc_type, exc_value, traceback):
        """Close database connection when exiting context"""
        if self.conn:
            self.conn.close()


if __name__ == "__main__":
    # Example usage of the context manager
    with DatabaseConnection("my_database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        results = cursor.fetchall()
        print(results)
