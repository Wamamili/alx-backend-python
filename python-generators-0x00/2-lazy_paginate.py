#!/usr/bin/python3
"""
Lazy loading paginated data using Python generators.
"""

import seed


def paginate_users(page_size, offset):
    """
    Fetch a page of users from the user_data table.

    Args:
        page_size (int): Number of rows per page.
        offset (int): Starting offset.

    Returns:
        list[dict]: A list of user rows as dictionaries.
    """
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return rows


def lazy_pagination(page_size):
    """
    Generator that lazily fetches paginated user data.

    Args:
        page_size (int): Number of rows per page.

    Yields:
        list[dict]: A page of user rows.
    """
    offset = 0
    while True:  # ✅ only one loop
        page = paginate_users(page_size, offset)
        if not page:
            break
        yield page
        offset += page_size
