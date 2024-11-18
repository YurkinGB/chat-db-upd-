import sqlite3

connection = sqlite3.connect('database.db')
cursor = connection.cursor()


def initiate_db():
    cursor.execute(f'''
CREATE TABLE IF NOT EXISTS Products(
id INTEGER PRIMARY KEY,
title TEXT NOT NULL,
description TEXT,
price INTEGER NOT NULL
)
''')

    # for i in range(1, 5):
    #     cursor.execute("INSERT INTO Products(title, description, price) VALUES (?, ?, ?)",
    #                    (f"Бад{i}", f"Описание к продукту {i}", i*10))

    cursor.execute(f'''
CREATE TABLE IF NOT EXISTS Users(
id INTEGER PRIMARY KEY,
username TEXT NOT NULL,
email TEXT NOT NULL,
age INTEGER NOT NULL,
balance INTEGER NOT NULL
)
''')

    connection.commit()


def is_included(username):
    cursor.execute(f"SELECT username FROM Users WHERE username = ?", (username,))
    return not (cursor.fetchone() is None)


def add_user(username, email, age, balance=1000):
    cursor.execute(f"INSERT INTO Users(username, email, age, balance) VALUES(?, ?, ?, ?)",
                    (f"{username}", f"{email}", f"{age}", f"{balance}"))

    connection.commit()


def get_all_products():
    cursor.execute(f'''
SELECT * FROM Products
''')
    return cursor.fetchall()

