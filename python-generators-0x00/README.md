# Task: Seed Database with Python Generators

## About the Task
This task demonstrates how to use Python **generators** to efficiently seed a database with large amounts of sample data.  
Instead of loading everything into memory at once, generators allow us to **yield one record at a time**, making the process memory-efficient and scalable.

You will implement a script called `seed.py` that:
- Defines a generator function to produce fake user/property/booking data.
- Connects to a database (SQLite/MySQL).
- Inserts the generated records in batches.

---

## Learning Objectives
- Understand how generators can be applied to database seeding.
- Use `yield` to produce rows of data dynamically.
- Implement batch insertion to optimize database performance.
- Combine Python with SQL for efficient data population.

---

## Requirements
- Python 3.x installed on your machine.
- SQLite3 or MySQL database installed.
- Knowledge of Python generators (`yield`).
- Familiarity with SQL schema design and insertion queries.
- GitHub repository: **alx-python-generators**
- Directory: **0x00-python-generators**
- File: **seed.py**

---

## Instructions
1. Create a file named `seed.py` inside the `0x00-python-generators` directory.
2. Implement a generator function (e.g., `user_generator`, `property_generator`) to yield rows of data.
3. Use the generator to insert records into your database in **batches**.
4. Ensure that the database connection is properly closed after seeding.

---

## Example

### Code (seed.py)
```python
import sqlite3
import random
import string

# Generator function for fake users
def user_generator(n):
    for _ in range(n):
        name = ''.join(random.choices(string.ascii_letters, k=6))
        email = f"{name.lower()}@example.com"
        yield (name, email)

# Seed function
def seed_users(n=10):
    conn = sqlite3.connect("airbnb.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT
    )
    """)

    for user in user_generator(n):
        cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", user)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    seed_users(20)
    print("Database seeded successfully!")
