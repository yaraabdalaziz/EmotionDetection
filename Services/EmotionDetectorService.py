from Library.EmotionDetector import EmotionDetector
from Database.HistoryRepo import HistoryRepo
from typing import Tuple
class EmotionDetectorService:
    def __init__(self, model_path:str='yaraabdalaziz/EmotionDetection')-> None:
        self.detector = EmotionDetector(model_path)
        self.history_repo = HistoryRepo()
    
    def detect_emotion(self, text:str, user_id:int)-> Tuple[str, str, float]:
        preprocessed, label, prob = self.detector.predict(text)
        self.history_repo.add_record(text, label, prob, user_id)
        return preprocessed, label, prob