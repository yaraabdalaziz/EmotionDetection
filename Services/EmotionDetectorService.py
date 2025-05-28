from Library import EmotionDetector
from Database.HistoryRepo import HistoryRepo

class EmotionDetectorService:
    def __init__(self, model_path='models/Bert-2epochs'):
        self.detector = EmotionDetector(model_path)
        self.history_repo = HistoryRepo()
    
    def detect_emotion(self, text, user_id):
        preprocessed, label, prob = self.detector.predict(text)
        self.history_repo.add_record(text, label, prob, user_id)
        return preprocessed, label, prob