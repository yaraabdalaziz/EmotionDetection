# Database/connection.py
from .DatabaseManager import db


def get_connection():
    return db.get_connection()
