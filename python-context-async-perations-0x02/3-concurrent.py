#!/usr/bin/env python3
"""
Concurrent Asynchronous Database Queries
"""

import asyncio
import aiosqlite


async def async_fetch_users(db_name="my_database.db"):
    """Fetch all users asynchronously"""
    async with aiosqlite.connect(db_name) as db:
        cursor = await db.execute("SELECT * FROM users")
        results = await cursor.fetchall()
        await cursor.close()
        return results


async def async_fetch_older_users(db_name="my_database.db"):
    """Fetch users older than 40 asynchronously"""
    async with aiosqlite.connect(db_name) as db:
        cursor = await db.execute("SELECT * FROM users WHERE age > ?", (40,))
        results = await cursor.fetchall()
        await cursor.close()
        return results


async def fetch_concurrently():
    """Run multiple queries concurrently"""
    all_users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )

    print("All Users:", all_users)
    print("Users older than 40:", older_users)


if __name__ == "__main__":
    asyncio.run(fetch_concurrently())
