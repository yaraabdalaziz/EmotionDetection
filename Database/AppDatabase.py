import sqlite3

class AppDatabase():
    
    def add_new_user (self,email,password,quota):

        conn = sqlite3.connect('Database/emotion_detection.db')
        cursor = conn.cursor()
        api_key = "api_key_test" #TODO: generate using a generator
        cursor.execute('''
        INSERT INTO Users (email, password, api_key, quota, available_requests)
        VALUES (?, ?, ?, ?, ?)
        ''', (
            email,
            password,  #TODO: In production, hash this!
            api_key, 
            quota,
            quota
        ))
        conn.commit()
        conn.close()

    def decrement_user_available_request(self,user_id): 
        conn = sqlite3.connect('Database/emotion_detection.db')
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE Users
        SET available_requests = available_requests - 1
        WHERE user_id = ?;
        ''', (user_id,))
        conn.commit()
        conn.close()

    def get_api_key_by_user_id(self,user_id):
        conn = sqlite3.connect('Database/emotion_detection.db')
        cursor = conn.cursor()
        cursor.execute('''
        SELECT api_key FROM Users
        WHERE user_id = ?;
        ''', (user_id,))

        result = cursor.fetchone()
        conn.close()

        if result:
            return result[0]  # api_key
        return None # TODO:  user doesn't exist error

    def get_available_requests_by_user_id(self,user_id):
        conn = sqlite3.connect('Database/emotion_detection.db')
        cursor = conn.cursor()
        cursor.execute('''
        SELECT available_requests FROM Users
        WHERE user_id = ?;
        ''', (user_id,))

        result = cursor.fetchone()
        conn.close()

        if result:
            return result[0]  # api_key
        return None # TODO:  user doesn't exist error

    def add_new_history_record(self,input_text,prediction,probability,user_id):
        conn = sqlite3.connect('Database/emotion_detection.db')
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO requests_records (input, prediction,probability, user_id)
        VALUES (?, ?, ?,?)
        ''', (
            input_text,
            prediction,
            probability,
            user_id,
        ))

        conn.commit()
        conn.close()