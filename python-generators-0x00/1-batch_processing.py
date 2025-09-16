#!/usr/bin/python3
"""
Batch processing of users using Python generators.
"""

import mysql.connector


def stream_users_in_batches(batch_size):
    """
    Generator that fetches rows from user_data in batches.

    Args:
        batch_size (int): Number of rows per batch.

    Yields:
        list[dict]: A batch of rows as dictionaries.
    """
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",       # adjust if needed
            password="root",   # adjust if needed
            database="ALX_prodev"
        )
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT user_id, name, email, age FROM user_data")

        batch = []
        for row in cursor:  # loop #1
            batch.append(row)
            if len(batch) == batch_size:
                yield batch
                batch = []
        if batch:  # leftover rows
            yield batch

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def batch_processing(batch_size):
    """
    Processes users in batches and filters users over the age of 25.

    Args:
        batch_size (int): Number of rows per batch.
    """
    for batch in stream_users_in_batches(batch_size):  # loop #2
        for user in batch:  # loop #3
            if user["age"] > 25:
                print(user)
