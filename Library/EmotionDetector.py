from Library.load_model import load_model
import torch
import torch.nn.functional as F
import re
from typing import Tuple


class EmotionDetector:

    def __init__(self, model_path: str, use_cuda: bool = True) -> None:
        self.id2label = {
            0: "sadness",
            1: "joy",
            2: "love",
            3: "anger",
            4: "fear",
            5: "surprise",
        }
        self.tokenizer, self.model = load_model(model_path)
        if use_cuda:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = "cpu"
        self.model.to(self.device)

    def predict(self, text: str) -> Tuple[str, str, float]:

        text = self.preprocess(text)
        inputs = self.tokenizer(
            text, return_tensors="pt", padding=True, truncation=True, max_length=512
        )

        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits

        probs = F.softmax(logits, dim=1)
        predicted_class_id = torch.argmax(probs, dim=1).item()
        predicted_label = self.id2label[predicted_class_id]
        probability = probs[0, predicted_class_id].item()

        return text, predicted_label, probability

    @staticmethod
    def preprocess(text: str) -> str:
        def remove_special_characters(text: str) -> str:
            return re.sub(r"[^A-Za-z0-9\s]", "", text)

        def normalize_whitespace(text: str) -> str:
            return re.sub(r"\s+", " ", text).strip()

        return normalize_whitespace(remove_special_characters(text)).lower()
