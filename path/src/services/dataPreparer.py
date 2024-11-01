import json

def load_feedback_data(filepath='path/src/api/models/Feedback.json'):
    with open(filepath, 'r') as f:
        return json.load(f)

def prepare_training_data(feedback_data):
    positive_examples = [fb['context'] for fb in feedback_data if fb['feedback'] == 1]
    negative_examples = [fb['context'] for fb in feedback_data if fb['feedback'] == -1]
    return positive_examples, negative_examples

def save_training_data(positive, negative, pos_filepath='path/data/positive.json', neg_filepath='path/data/negative.json'):
    with open(pos_filepath, 'w') as f:
        json.dump(positive, f, indent=2)
    with open(neg_filepath, 'w') as f:
        json.dump(negative, f, indent=2)

def main():
    feedback_data = load_feedback_data()
    positive, negative = prepare_training_data(feedback_data)
    save_training_data(positive, negative)
    print(f"Saved {len(positive)} positive and {len(negative)} negative examples.")

if __name__ == "__main__":
    main() 