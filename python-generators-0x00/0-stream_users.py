#!/usr/bin/python3
"""
Stream users one by one from the user_data table using a generator.
"""

import mysql.connector


def stream_users():
    """
    Generator that streams rows from the user_data table one by one.

    Yields:
        dict: A row from the user_data table with keys:
              user_id, name, email, age
    """
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",        # adjust if needed
            password="root",    # adjust if needed
            database="ALX_prodev"
        )
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT user_id, name, email, age FROM user_data")

        # one loop only → generator handles streaming
        for row in cursor:
            yield row

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
