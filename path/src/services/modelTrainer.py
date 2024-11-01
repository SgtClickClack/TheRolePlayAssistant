"""
Module: modelTrainer
Description: Contains functions to train the AI model using user feedback.
"""

import openai
import json
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')

def fine_tune_model(positive_filepath='path/data/positive.json'):
    with open(positive_filepath, 'r') as f:
        positive_examples = json.load(f)
    
    # Prepare data in the required format
    training_data = [{"prompt": f"User input: {example}\nResponse:", "completion": " "} for example in positive_examples]
    
    # Save to a file for upload
    with open('path/data/training_data.jsonl', 'w') as f:
        for entry in training_data:
            f.write(json.dumps(entry) + '\n')
    
    # Create a fine-tuning job
    response = openai.FineTune.create(
        training_file='path/data/training_data.jsonl',
        model='text-davinci-003',  # Replace with your base model
        n_epochs=4,
        batch_size=8,
        learning_rate_multiplier=0.1,
    )
    
    print("Fine-tuning started:", response['id'])

def main():
    fine_tune_model()

if __name__ == "__main__":
    main()