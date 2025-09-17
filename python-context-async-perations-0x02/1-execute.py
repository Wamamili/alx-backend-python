#!/usr/bin/env python3
"""
Task 1: Reusable Query Context Manager
"""

import sqlite3


class ExecuteQuery:
    """Custom context manager to execute a SQL query with parameters"""

    def __init__(self, db_name, query, params=None):
        self.db_name = db_name
        self.query = query
        self.params = params if params else ()
        self.conn = None
        self.cursor = None
        self.results = None

    def __enter__(self):
        """Open connection and execute the query"""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute(self.query, self.params)
        self.results = self.cursor.fetchall()
        return self.results

    def __exit__(self, exc_type, exc_value, traceback):
        """Close connection automatically"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()


if __name__ == "__main__":
    query = "SELECT * FROM users WHERE age > ?"
    params = (25,)

    with ExecuteQuery("my_database.db", query, params) as results:
        print(results)
