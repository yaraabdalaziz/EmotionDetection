from Database.connection import get_connection
from Library.utils import encrypt_password, generate_api_key

class UsersRepo:
    def add_new_user(self, email, password, quota):
        conn = get_connection()
        cursor = conn.cursor()
        hashed_pw = encrypt_password(password)
        api_key = generate_api_key()

        cursor.execute('''
            INSERT INTO Users (email, password, api_key, quota, available_requests)
            VALUES (?, ?, ?, ?, ?)
        ''', (email, hashed_pw, api_key, quota, quota))

        conn.commit()
        conn.close()

    def get_user_id(self, api_key):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM Users WHERE api_key = ?', (api_key,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def decrement_user_quota(self, user_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE Users SET available_requests = available_requests - 1 WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()

    def has_quota(self, user_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT available_requests FROM Users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result and result[0] > 0
