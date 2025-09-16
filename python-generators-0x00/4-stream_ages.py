#!/usr/bin/python3
"""
Memory-efficient aggregation with generators.
Compute the average age of users without loading all data into memory.
"""

import seed


def stream_user_ages():
    """
    Generator that streams user ages one by one.

    Yields:
        int: Age of a user from the database.
    """
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT age FROM user_data")
    for row in cursor:  # ✅ loop #1
        yield row["age"]
    cursor.close()
    connection.close()


def calculate_average_age():
    """
    Calculate the average age using the stream_user_ages generator.

    Prints:
        str: Average age of users.
    """
    total, count = 0, 0
    for age in stream_user_ages():  # ✅ loop #2
        total += age
        count += 1

    average = total / count if count > 0 else 0
    print(f"Average age of users: {average:.2f}")


if __name__ == "__main__":
    calculate_average_age()
