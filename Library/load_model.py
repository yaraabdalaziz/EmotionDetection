from transformers import AutoTokenizer, AutoModelForSequenceClassification

def load_model(path):
    tokenizer = AutoTokenizer.from_pretrained(path)
    model = AutoModelForSequenceClassification.from_pretrained(path, num_labels=6)
    return tokenizer , model