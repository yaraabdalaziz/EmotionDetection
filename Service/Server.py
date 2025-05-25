from EmotionDetector import EmotionDetector
from Database.AppDatabase import AppDatabase

class Server():
    def __init__(self):
        self.detector = EmotionDetector('Models/Bert-2epochs')
        print("Model is ready")
        self.db = AppDatabase()
        print("Database is ready")
    def authenticate_user(self, api_key): 
        return  self.db.get_user_id(api_key)
    def user_has_quota(self,user_id):
        if self.db.get_available_requests_by_user_id(user_id) :
            return True
        return False
    def detect_emotion(self,text, user_id):
        preprocessed_text,predicted_label, probability = self.detector.predict(text)     
        self.db.decrement_user_available_request(user_id)
        self.db.add_new_history_record(text,predicted_label,probability,user_id)                                                      
        return preprocessed_text,predicted_label, probability 