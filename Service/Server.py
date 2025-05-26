from EmotionDetector import EmotionDetector
from Database.UsersRepo import UsersRepo
from Database.HistoryRepo import HistoryRepo

class Server:
    def __init__(self):
        self.detector = EmotionDetector('Models/Bert-2epochs')
        print("Model is ready")
        self.users_repo = UsersRepo()
        self.history_repo = HistoryRepo()
        print("Database is ready")

    def authenticate_user(self, api_key):
        return self.users_repo.get_user_id(api_key)

    def user_has_quota(self, user_id):
        return self.users_repo.has_quota(user_id)

    def detect_emotion(self, text, user_id):
        preprocessed, label, prob = self.detector.predict(text)
        self.users_repo.decrement_user_quota(user_id)
        self.history_repo.add_record(text, label, prob, user_id)
        return preprocessed, label, prob
