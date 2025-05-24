#!/usr/bin/env python3
"""
Generate result2.json files for each model in output/OEQ and output/MCQ datasets.

This script:
1. Reads evaluation.jsonl files for each model in both OEQ and MCQ datasets
2. Analyzes the data to calculate:
   - Total number of questions
   - Overall accuracy
   - Accuracy by question type
   - Evaluator statistics
3. Saves the results to result2.json in each model directory
"""

import os
import json
from pathlib import Path
from collections import defaultdict

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

# Load question type mapping
QUESTION_TYPE_MAPPING = {}
mapping_file = Path("data/question_type_mapping.json")
if mapping_file.exists():
    with open(mapping_file, 'r', encoding='utf-8') as f:
        QUESTION_TYPE_MAPPING = json.load(f)
    print(f"Loaded {len(QUESTION_TYPE_MAPPING)} question type mappings")
else:
    print(f"Warning: Question type mapping file {mapping_file} not found.")

def extract_question_type(eval_data):
    """Extract the question type from the evaluation data.

    First tries to get the type from the question type mapping,
    then falls back to the type field in the evaluation data,
    and finally falls back to extracting from the question ID.
    """
    # First try to get the type from the mapping
    question_id = eval_data.get("id", "Unknown")
    if question_id in QUESTION_TYPE_MAPPING:
        return QUESTION_TYPE_MAPPING[question_id]

    # If not in mapping, try to get the type directly from the evaluation data
    if "type" in eval_data:
        return eval_data["type"]

    # If not available, fall back to extracting from the question ID
    if '_' not in question_id:
        return "Unknown"

    prefix = question_id.split('_')[0]
    return prefix

def analyze_evaluations(evaluations):
    """Analyze evaluation data and generate result2.json."""
    # Initialize counters
    total_questions = len(evaluations)
    correct_questions = 0

    # Track by question type
    question_types = defaultdict(lambda: {"total": 0, "correct": 0})

    # Track evaluator stats
    evaluator_stats = {
        "quantity": {"true": 0, "false": 0, "null": 0},
        "expression": {"true": 0, "false": 0, "null": 0},
        "llm": {"true": 0, "false": 0, "null": 0},
        "mcq": {"true": 0, "false": 0, "null": 0}
    }

    # Process each evaluation
    for eval_data in evaluations:
        # Extract question ID
        question_id = eval_data.get("id", "Unknown")

        # Get question type from mapping
        if question_id in QUESTION_TYPE_MAPPING:
            question_type = QUESTION_TYPE_MAPPING[question_id]
        else:
            # Fall back to extracting from the question ID
            if '_' not in question_id:
                question_type = "Unknown"
            else:
                question_type = question_id.split('_')[0]

        # Count total by type
        question_types[question_type]["total"] += 1

        # Check if question is correct
        is_correct = eval_data.get("score", 0) > 0
        if is_correct:
            correct_questions += 1
            question_types[question_type]["correct"] += 1

        # Process evaluator stats
        for eval_item in eval_data.get("evaluation", []):
            for evaluator, result in eval_item.get("evaluations", {}).items():
                if evaluator in evaluator_stats:
                    if result.get("is_correct") is True:
                        evaluator_stats[evaluator]["true"] += 1
                    elif result.get("is_correct") is False:
                        evaluator_stats[evaluator]["false"] += 1
                    else:
                        evaluator_stats[evaluator]["null"] += 1

    # Calculate overall accuracy
    overall_accuracy = correct_questions / total_questions if total_questions > 0 else 0

    # Calculate accuracy by type
    type_accuracy = {}
    for qtype, counts in question_types.items():
        type_accuracy[qtype] = counts["correct"] / counts["total"] if counts["total"] > 0 else 0

    # Create result2.json
    result = {
        "total_questions": total_questions,
        "correct_questions": correct_questions,
        "overall_accuracy": overall_accuracy,
        "question_types": {
            qtype: {
                "total": counts["total"],
                "correct": counts["correct"],
                "accuracy": type_accuracy[qtype]
            }
            for qtype, counts in question_types.items()
        },
        "evaluator_stats": evaluator_stats
    }

    return result

def process_dataset(dataset_path, dataset_name):
    """Process all models in a dataset directory."""
    if not dataset_path.exists():
        print(f"Dataset directory {dataset_path} does not exist. Skipping.")
        return

    # Get all subdirectories (could be model directories or dataset subdirectories)
    subdirs = [d for d in dataset_path.iterdir() if d.is_dir()]

    # Check if this is a dataset with subdatasets (like MCQ with main_1-10, extra_1-10, etc.)
    has_subdatasets = all(not (d / "evaluation.jsonl").exists() for d in subdirs if d.is_dir())

    if has_subdatasets:
        print(f"Processing {dataset_name} subdatasets:")
        for subdir in subdirs:
            process_dataset(subdir, f"{dataset_name}/{subdir.name}")
    else:
        # This is a directory with model subdirectories
        model_dirs = subdirs
        print(f"Found {len(model_dirs)} model directories in {dataset_name}")

        # Process each model
        for model_dir in model_dirs:
            model_name = model_dir.name
            print(f"Processing model: {model_name}")

            # Check if evaluation.jsonl exists
            eval_file = model_dir / "evaluation.jsonl"
            if not eval_file.exists():
                print(f"  Skipping {model_name} - evaluation.jsonl not found")
                continue

            # Load evaluations
            evaluations = load_jsonl(eval_file)
            print(f"  Loaded {len(evaluations)} evaluations")

            # Analyze evaluations
            result = analyze_evaluations(evaluations)

            # Save result2.json
            result_file = model_dir / "result2.json"
            save_json(result, result_file)
            print(f"  Saved result2.json with {result['total_questions']} questions, accuracy: {result['overall_accuracy']:.4f}")

            # Print question type stats
            print(f"  Question type stats:")
            for qtype, stats in result["question_types"].items():
                print(f"    {qtype}: {stats['correct']}/{stats['total']} = {stats['accuracy']:.4f}")

def main():
    """Main function to process all datasets."""
    # Process OEQ dataset
    oeq_dir = Path("output/OEQ/oeq")
    process_dataset(oeq_dir, "OEQ/oeq")

    # Process MCQ datasets
    mcq_dir = Path("output/MCQ")
    process_dataset(mcq_dir, "MCQ")

    print("All datasets processed successfully!")

if __name__ == "__main__":
    main()
