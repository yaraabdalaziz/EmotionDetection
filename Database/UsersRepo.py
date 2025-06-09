from Database.connection import get_connection
from Database.utils import encrypt_password, generate_api_key
import threading
from collections import defaultdict

class UsersRepo:
    def __init__(self) -> None:
        self.user_locks = defaultdict(threading.Lock)
    def add_new_user(self, email:str, password:str, quota:int)-> str:
        hashed_pw = encrypt_password(password)
        api_key = generate_api_key()
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (email, password, api_key, quota, available_requests)
                VALUES (?, ?, ?, ?, ?)
            ''', (email, hashed_pw, api_key, quota, quota))

            conn.commit()
        return api_key

    def get_user_id(self, api_key:str)->int:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT user_id FROM users WHERE api_key = ?', (api_key,))
            result = cursor.fetchone()
            return result[0] if result else None

    def decrement_user_quota(self, user_id:int)-> bool:
        """Thread-safe quota decrement - returns True if successful"""
        with self.user_locks[user_id]:  
            with get_connection() as conn:
                conn.execute("BEGIN IMMEDIATE") 
                try:
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        UPDATE users 
                        SET available_requests = available_requests - 1 
                        WHERE user_id = ? AND available_requests > 0
                    ''', (user_id,))
                    
                    success = cursor.rowcount > 0
                    conn.commit()
                    return success
                
                except Exception:
                    conn.rollback()
                    return False
    def incerement_user_quota(self, user_id:int)-> bool:
        """Thread-safe quota decrement - returns True if successful"""
        with self.user_locks[user_id]: 
            with get_connection() as conn:
                conn.execute("BEGIN IMMEDIATE")  
                try:
                    cursor = conn.cursor()
                    cursor.execute('''
                        UPDATE users 
                        SET available_requests = available_requests + 1 
                        WHERE user_id = ? 
                    ''', (user_id,))
                    
                    success = cursor.rowcount > 0
                    conn.commit()
                    return success
                    
                except Exception:
                    conn.rollback()
                    return False

    def has_quota(self, user_id:int)->bool:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT available_requests FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result and result[0] > 0
