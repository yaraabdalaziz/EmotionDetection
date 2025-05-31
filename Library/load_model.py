from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os 
def load_model(path):
    hf_token = os.environ.get("HF_TOKEN")    
    tokenizer = AutoTokenizer.from_pretrained(path, token=hf_token )
    model = AutoModelForSequenceClassification.from_pretrained(path, num_labels=6, token=hf_token )
    return tokenizer , model