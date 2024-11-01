import json
from collections import defaultdict
from datetime import datetime

def load_feedback_data(filepath='path/src/api/models/Feedback.json'):
    with open(filepath, 'r') as f:
        return json.load(f)

def analyze_feedback(feedback_data):
    summary = defaultdict(int)
    for entry in feedback_data:
        summary[entry['feedback']] += 1
    return summary

def main():
    feedback_data = load_feedback_data()
    summary = analyze_feedback(feedback_data)
    print("Feedback Summary:")
    print(f"Thumbs Up: {summary[1]}")
    print(f"Thumbs Down: {summary[-1]}")

if __name__ == "__main__":
    main() 