from load_model import load_model
import torch
import numpy as np
import re
class EmotionDetector :
    
    def __init__(self, model_path, use_cuda=True):
        self.id2label = {0: "sadness", 1: "joy", 2: "love", 3: "anger", 4: "fear", 5: "surprise"}
        self.label2id = {v: k for k, v in self.id2label.items()}
        self.tokenizer  , self.model = load_model(model_path)
        if use_cuda:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
             self.device = 'cpu'
        self.model.to(self.device)
        print("Model is ready")

    @staticmethod
    def preprocess(text):
        def remove_special_characters(text):
            return re.sub(r'[^A-Za-z0-9\s]', '', text)
        def normalize_whitespace(text):
            return re.sub(r'\s+', ' ', text).strip()
        return normalize_whitespace(remove_special_characters(text)).lower()

    def predict(self, text):
            """
            Predicts the emotion of an input text using the fine-tuned model.

            Args:
                text: The input text to analyze.
                model: The fine-tuned BertForSequenceClassification model.
                tokenizer: The tokenizer used for the model.
                id2label: A dictionary mapping label IDs to label names.

            Returns:
                A dictionary containing the predicted emotion label and its associated probability.
            """
            
            text = self.preprocess(text)
            # Tokenize the input text
            inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length = 512)

            # Move inputs to the device (GPU if available, otherwise CPU)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Make prediction
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits

            # Get predicted label and probability
            predicted_class_id = np.argmax(logits.cpu().numpy()).item()
            predicted_label = self.id2label[predicted_class_id]
            probability = np.exp(logits.cpu().numpy()[0][predicted_class_id]) / np.sum(np.exp(logits.cpu().numpy()[0]))

            return  text , predicted_label,  float(probability)