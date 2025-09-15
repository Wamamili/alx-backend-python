#!/usr/bin/python3
"""
seed.py - Setup and seed ALX_prodev MySQL database with user_data
"""

import mysql.connector
from mysql.connector import errorcode
import csv
import uuid


def connect_db():
    """Connect to MySQL server"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",          # adjust if your MySQL user is different
            password="root"       # adjust if you have a password set
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None


def create_database(connection):
    """Create database ALX_prodev if it does not exist"""
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
        print("Database ALX_prodev created or already exists")
    except mysql.connector.Error as err:
        print(f"Error creating database: {err}")
    finally:
        cursor.close()


def connect_to_prodev():
    """Connect to ALX_prodev database"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="ALX_prodev"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None


def create_table(connection):
    """Create user_data table if not exists"""
    table_query = """
    CREATE TABLE IF NOT EXISTS user_data (
        user_id CHAR(36) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        age DECIMAL NOT NULL,
        INDEX(user_id)
    );
    """
    try:
        cursor = connection.cursor()
        cursor.execute(table_query)
        connection.commit()
        print("Table user_data created successfully")
    except mysql.connector.Error as err:
        print(f"Error creating table: {err}")
    finally:
        cursor.close()


def insert_data(connection, csv_file):
    """Insert data from CSV into user_data table if not exists"""
    try:
        cursor = connection.cursor()
        with open(csv_file, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                user_id = str(uuid.uuid4())
                name = row["name"]
                email = row["email"]
                age = row["age"]

                # check if email already exists to prevent duplicates
                cursor.execute("SELECT * FROM user_data WHERE email = %s", (email,))
                exists = cursor.fetchone()
                if not exists:
                    cursor.execute(
                        "INSERT INTO user_data (user_id, name, email, age) VALUES (%s, %s, %s, %s)",
                        (user_id, name, email, age),
                    )
        connection.commit()
        print("Data inserted successfully")
    except Exception as e:
        print(f"Error inserting data: {e}")
    finally:
        cursor.close()
