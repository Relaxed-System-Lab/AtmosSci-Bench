#!/usr/bin/env python3
"""
Create a mapping of question IDs to their types from the original data.

This script:
1. Reads the original data files (oeq.jsonl, main_1-10.jsonl, etc.)
2. Creates a mapping of question IDs to their types
3. Saves the mapping to a JSON file for use by generate_result2.py
"""

import os
import json
from pathlib import Path

def load_jsonl(file_path):
    """Load a JSONL file into a list of dictionaries."""
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line.strip()))
    return data

def save_json(data, file_path):
    """Save a dictionary to a JSON file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def create_question_type_mapping():
    """Create a mapping of question IDs to their types."""
    # Initialize the mapping
    question_type_mapping = {}
    
    # Process OEQ data
    oeq_file = Path("data/jsonl/oeq.jsonl")
    if oeq_file.exists():
        oeq_data = load_jsonl(oeq_file)
        for item in oeq_data:
            question_id = item.get("id")
            question_type = item.get("type")
            if question_id and question_type:
                question_type_mapping[question_id] = question_type
        print(f"Processed {len(oeq_data)} OEQ questions")
    
    # Process MCQ data
    mcq_files = [
        Path("data/jsonl/main_1-10.jsonl"),
        Path("data/jsonl/main_11-30.jsonl"),
        Path("data/jsonl/extra_1-10.jsonl"),
    ]
    
    for mcq_file in mcq_files:
        if mcq_file.exists():
            mcq_data = load_jsonl(mcq_file)
            for item in mcq_data:
                question_id = item.get("id")
                question_type = item.get("type")
                if question_id and question_type:
                    question_type_mapping[question_id] = question_type
            print(f"Processed {len(mcq_data)} MCQ questions from {mcq_file.name}")
    
    # Save the mapping
    output_file = Path("data/question_type_mapping.json")
    save_json(question_type_mapping, output_file)
    print(f"Saved {len(question_type_mapping)} question type mappings to {output_file}")
    
    return question_type_mapping

if __name__ == "__main__":
    create_question_type_mapping()
