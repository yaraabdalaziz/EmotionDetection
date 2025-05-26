import sqlite3

DB_PATH = 'Database/emotion_detection.db'

def get_connection():
    return sqlite3.connect(DB_PATH)
