# Database/connection.py
from .DatabaseManager import db

def get_connection():
    """Get database connection context manager"""
    return db.get_connection()