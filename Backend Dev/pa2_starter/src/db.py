import os
import sqlite3

# From: https://goo.gl/YzypOI

def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return getinstance


class DatabaseDriver(object):
    """
    Database driver for the Task app.
    Handles with reading and writing data with the database.
    """

    def __init__(self):
        self.conn = sqlite3.connect("users.db", check_same_thread=False) #dont want other processes accesing this, always have it false
        self.create_users_table()

    def create_users_table(self):
        try:
            self.conn.execute("""
                CREATE TABLE users(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    username TEXT NOT NULL,
                    balance INTEGER
                );
            """)
        except Exception as e:
            print(e)

    def get_users(self):
        cursor = self.conn.execute("SELECT * FROM users;")
        users = []
        for row in cursor:
            users.append({"id": row[0], "name": row[1], "username": row[2]})
        return users

    def get_users_by_id(self, id):
        cursor = self.conn.execute("SELECT * FROM users WHERE id = ?;", (id,)) #need ',' to make it a tuple
        for row in cursor:
            return {"id": row[0], "name": row[1], "username": row[2], "balance": row[3]}
        return None

    def create_user(self, name, username, balance):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO users(name, username, balance) VALUES (?, ?, ?);
        """, (name, username, balance))
        self.conn.commit()
        return cursor.lastrowid

    def delete_user(self, user_id):
        get_user = self.get_users_by_id(user_id)
        self.conn.execute("DELETE FROM users WHERE id=?;", (user_id,))
        self.conn.commit()
        return get_user

    def send_money(self, sender_id, receiver_id, amount):
        cursor = self.conn.execute("SELECT * FROM users WHERE id =?;",(sender_id,))
        balance = 0
        for row in cursor:
            balance = row[3]
        if(balance<amount):
            return None
        self.conn.execute("""
            UPDATE users SET balance = ? WHERE id = ?;
        """, (balance-amount, sender_id))
        self.conn.commit()
        cursor = self.conn.execute("SELECT * FROM users WHERE id =?;",(receiver_id,))
        balance = 0
        for row in cursor:
            balance = row[3]
        self.conn.execute("""
            UPDATE users SET balance = ? WHERE id = ?;
        """, (balance+amount, receiver_id))
        self.conn.commit()
        return {"sender_id": sender_id, "receiver_id": receiver_id, "amount": amount}

DatabaseDriver = singleton(DatabaseDriver)