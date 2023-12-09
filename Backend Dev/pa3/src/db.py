import os
import sqlite3
from datetime import datetime

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
        self.create_transactions_table()

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
        cursor2 = self.conn.execute("SELECT * FROM transactions WHERE sender_id = ? OR receiver_id = ?;",(id,id))
        cursor = self.conn.execute("SELECT * FROM users WHERE id = ?;", (id,)) #need ',' to make it a tuple
        users = {}
        temp = []
        for row2 in cursor2:
            if row2[6] == None:
                temp.append({"id": row2[0], "timestamp": row2[1], "sender_id": row2[2], "receiver_id": row2[3], "amount": row2[4], "message": row2[5], "accepted": row2[6]})
            else:
                temp.append({"id": row2[0], "timestamp": row2[1], "sender_id": row2[2], "receiver_id": row2[3], "amount": row2[4], "message": row2[5], "accepted": bool(row2[6])})
        for row in cursor:
            users['id'] = row[0]
            users['name'] = row[1]
            users['username'] = row[2]
            users['balance'] = row[3]
            users['transactions'] = temp
            return users
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
        if get_user is None:
            return None
        self.conn.execute("DELETE FROM users WHERE id=?;", (user_id,))
        self.conn.commit()
        returns = []
        returns.append({"success": "true", "data": get_user})
        return returns

    def create_transaction(self, sender_id, receiver_id, amount, message, accepted):
        cursor = self.conn.execute("SELECT * FROM users WHERE id =?;",(sender_id,))
        balance = 0
        for row in cursor:
            balance = row[3]
        if(balance<amount and accepted):
            return None
        elif (balance<amount):
            time = datetime.timestamp(datetime.now())
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO transactions(timestamp, sender_id, receiver_id, amount, message, accepted) VALUES (?, ?, ?, ?, ?, ?);
            """, (time, sender_id, receiver_id, amount, message, accepted))
            self.conn.commit()
            return cursor.lastrowid
        if accepted:
            self.conn.execute("""
                UPDATE users SET balance = ? WHERE id = ?;
            """, (balance-amount, sender_id))
            self.conn.commit()
            cursor = self.conn.execute("SELECT * FROM users WHERE id =?;",(receiver_id,))
            for row in cursor:
                balance = row[3]
            self.conn.execute("""
                UPDATE users SET balance = ? WHERE id = ?;
            """, (balance+amount, receiver_id))
            self.conn.commit()
        time = datetime.timestamp(datetime.now())
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO transactions(timestamp, sender_id, receiver_id, amount, message, accepted) VALUES (?, ?, ?, ?, ?, ?);
        """, (time, sender_id, receiver_id, amount, message, accepted))
        self.conn.commit()
        return cursor.lastrowid

    def get_transactions_by_id(self, id):
        cursor = self.conn.execute("SELECT * FROM transactions WHERE id = ?;", (id,)) #need ',' to make it a tuple
        for row in cursor:
            return ({"id": row[0], "timestamp": row[1], "sender_id": row[2], "receiver_id": row[3], "amount": row[4], "message": row[5], "accepted": bool(row[6])})
        return None

    def create_transactions_table(self):
        try:
            self.conn.execute("""
                CREATE TABLE transactions(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp FLOAT NOT NULL,
                    sender_id INTEGER SECONDARY KEY NOT NULL,
                    receiver_id INTEGER SECONDARY KEY NOT NULL,
                    amount INTEGER NOT NULL,
                    message TEXT NOT NULL,
                    accepted BOOLEAN
                );
            """)
        except Exception as e:
            print(e)

    def manage_transaction(self, id, accepted):
        cursor = self.conn.execute("SELECT * FROM transactions WHERE id =?;",(id,))
        sender_id = 0
        receiver_id = 0
        amount = 0
        accept_status = False
        for row in cursor:
            if row[6] == None:
                accept_status = row[6]
            else:
                accept_status == bool(row[6])
            sender_id = row[2]
            receiver_id = row[3]
            amount = row[4]
        if accept_status!=None:
            return None
        self.conn.execute("""
            UPDATE transactions SET accepted = ? WHERE id = ?;
        """, (accepted, id))
        self.conn.commit()
        if accepted == True:
            cursor = self.conn.execute("SELECT * FROM users WHERE id =?;",(sender_id,))
            balance = 0
            for row in cursor:
                balance = row[3]
            if(balance<amount):
                print("running")
                return None
            self.conn.execute("""
                UPDATE users SET balance = ? WHERE id = ?;
            """, (balance-amount, sender_id))
            self.conn.commit()
            cursor = self.conn.execute("SELECT * FROM users WHERE id =?;",(receiver_id,))
            for row in cursor:
                balance = row[3]
            self.conn.execute("""
                UPDATE users SET balance = ? WHERE id = ?;
            """, (balance+amount, receiver_id))
        return id

DatabaseDriver = singleton(DatabaseDriver)