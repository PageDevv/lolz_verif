import sqlite3
import datetime
from os import system


def check_db():
    _ = system("cls")
    _datetime = get_now_date()
    databaseFile = ("database.db")
    db = sqlite3.connect(databaseFile, check_same_thread=False)
    cursor = db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users("
                   "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                   "user_id INT)")

    cursor.execute("CREATE TABLE IF NOT EXISTS notes("
                   "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                   "user_id INT, "
                   "message_title TEXT, "
                   "message_text TEXT)")
    db.commit()
    print("---   Database was connect   ---")
    print(f"-----   {_datetime}   -----")
    print(f"---------   Users: {len(get_all_users())}   --------\n")


def add_user_to_db(user_id):
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    if not (cursor.execute(f"SELECT user_id FROM users WHERE user_id = '{user_id}'").fetchone()):
        cursor.execute(f"INSERT INTO users(user_id) "
                       f"VALUES ({user_id})")
    db.commit()


def add_note_to_db(user_id, note_title, note_text):
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute(f"INSERT INTO notes(user_id, message_title, message_text) "
                   f"VALUES ({user_id}, '{note_title}', '{note_text}')")
    db.commit()


def get_now_date():
    date = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
    return date


def get_all_users():
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT user_id FROM users ORDER BY id")
    row = cursor.fetchall()
    return row


def get_all_notes(user_id):
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM notes WHERE user_id = {user_id} ORDER BY id")
    row = cursor.fetchall()
    return row


def get_note(note_id):
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM notes WHERE id = {note_id}")
    row = cursor.fetchone()
    return row


def delete_note(note_id):
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute(f"DELETE FROM notes WHERE id = {note_id}")
    db.commit()


def find_note(user_id, note_title):
    print(note_title)
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM notes WHERE user_id = {user_id} AND message_title LIKE '%{note_title}%'")
    row = cursor.fetchall()
    return row
