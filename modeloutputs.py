import json
with open('mapping.json') as json_file:
    label_dict= json.load(json_file)
    
    
import torch
from transformers import BertTokenizer, BertForSequenceClassification
import matplotlib.pyplot as plt
import numpy as np

# Load the tokenizer and model
device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=len(label_dict))

# Load the fine-tuned model weights
model.load_state_dict(torch.load(r'finetuned_BERT_epoch_4.model', map_location=torch.device('cpu')))
model.to(device)
model.eval()

# Invert the label dictionary to map indices back to labels
idx_to_label_dict = {v: k for k, v in label_dict.items()}

# Function to preprocess the input text and make predictions
def predict_probabilities(text):
    inputs = tokenizer(text, return_tensors='pt', max_length=256, padding='max_length', truncation=True)
    inputs = {key: value.to(device) for key, value in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits

    probabilities = torch.nn.functional.softmax(logits, dim=1).cpu().numpy().flatten()
    return probabilities

# Function to get top 5 classes with highest probabilities
def get_top_5_classes(probabilities):
    top_5_indices = np.argsort(probabilities)[-5:][::-1]
    top_5_labels = [idx_to_label_dict[idx] for idx in top_5_indices]
    
    top_5_probs = probabilities[top_5_indices]
    return top_5_labels, top_5_probs


def generate(text):
    probabilities = predict_probabilities(text)
    top_5_labels, top_5_probs = get_top_5_classes(probabilities)
 
    return top_5_labels[0],top_5_probs[0]

"""for label, prob in zip(top_5_labels, top_5_probs):
    print(f"Class: {label}, Probability: {prob:.4f}")"""
