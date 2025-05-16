#!/usr/bin/env python3
"""
Create instance accuracy analysis by grouping questions by their instance number.

This script reads evaluation.jsonl files, groups questions by their instance number,
and calculates the accuracy for each instance. It also outputs a summary file with
average accuracy and standard deviation.

The script automatically processes all models under the output/MCQ directory.

Usage:
    python create_instance_acc.py --base <base_dir>

Example:
    python create_instance_acc.py --base output
"""

import os
import json
import argparse
import math
import statistics
from collections import defaultdict
import re


def parse_id(question_id):
    """
    Parse the question ID to extract template and instance numbers.

    Args:
        question_id (str): Question ID in the format "MCQ_2_1"

    Returns:
        tuple: (template_number, instance_number)
    """
    match = re.match(r'([A-Za-z]+)_(\d+)_(\d+)', question_id)
    if match:
        question_type, template_number, instance_number = match.groups()
        return int(template_number), int(instance_number)
    return None, None


def calculate_instance_accuracy(evaluation_file):
    """
    Calculate accuracy for each instance by grouping questions by instance number.

    Args:
        evaluation_file (str): Path to the evaluation.jsonl file

    Returns:
        dict: Dictionary with instance numbers as keys and accuracy data as values
    """
    # Dictionary to store results for each instance
    instance_results = defaultdict(lambda: {'correct': 0, 'total': 0, 'questions': []})

    # Read the evaluation file
    with open(evaluation_file, 'r') as f:
        for line in f:
            data = json.loads(line.strip())

            # Extract template and instance numbers from the ID
            template_number, instance_number = parse_id(data['id'])

            if instance_number is not None:
                # Add to the instance results
                instance_results[instance_number]['questions'].append(data['id'])
                instance_results[instance_number]['total'] += 1

                # Check if the answer is correct
                if data.get('score', 0) == 1.0:
                    instance_results[instance_number]['correct'] += 1

    # Calculate accuracy for each instance
    for instance_number, results in instance_results.items():
        results['accuracy'] = results['correct'] / results['total'] if results['total'] > 0 else 0

    return instance_results


def save_instance_accuracy(instance_results, output_file):
    """
    Save instance accuracy results to a JSONL file.

    Args:
        instance_results (dict): Dictionary with instance numbers as keys and accuracy data as values
        output_file (str): Path to the output file
    """
    with open(output_file, 'w') as f:
        for instance_number, results in sorted(instance_results.items()):
            output = {
                'instance': instance_number,
                'accuracy': results['accuracy'],
                'correct': results['correct'],
                'total': results['total'],
                'questions': results['questions']
            }
            f.write(json.dumps(output) + '\n')


def calculate_summary_statistics(instance_results):
    """
    Calculate summary statistics for instance accuracies.

    Args:
        instance_results (dict): Dictionary with instance numbers as keys and accuracy data as values

    Returns:
        dict: Dictionary with summary statistics
    """
    # Extract accuracies
    accuracies = [results['accuracy'] for results in instance_results.values()]

    # Calculate statistics
    avg_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0
    std_dev = statistics.stdev(accuracies) if len(accuracies) > 1 else 0

    # Calculate total correct and total questions
    total_correct = sum(results['correct'] for results in instance_results.values())
    total_questions = sum(results['total'] for results in instance_results.values())
    overall_accuracy = total_correct / total_questions if total_questions > 0 else 0

    return {
        'average_instance_accuracy': avg_accuracy,
        'standard_deviation': std_dev,
        'overall_accuracy': overall_accuracy,
        'total_correct': total_correct,
        'total_questions': total_questions,
        'num_instances': len(instance_results)
    }


def save_summary_statistics(summary_stats, output_file):
    """
    Save summary statistics to a JSONL file.

    Args:
        summary_stats (dict): Dictionary with summary statistics
        output_file (str): Path to the output file
    """
    with open(output_file, 'w') as f:
        f.write(json.dumps(summary_stats) + '\n')


def find_mcq_datasets_and_models(base_dir):
    """
    Find all MCQ datasets and models under the base directory.

    Args:
        base_dir (str): Base directory (e.g., output)

    Returns:
        list: List of (dataset_path, model_path) tuples
    """
    mcq_dir = os.path.join(base_dir, 'MCQ')
    if not os.path.exists(mcq_dir):
        print(f"Error: MCQ directory not found: {mcq_dir}")
        return []

    dataset_model_pairs = []

    # Find all dataset directories under MCQ
    for dataset_name in os.listdir(mcq_dir):
        dataset_path = os.path.join('MCQ', dataset_name)
        dataset_full_path = os.path.join(base_dir, dataset_path)

        if os.path.isdir(dataset_full_path):
            # Find all model directories under this dataset
            for model_name in os.listdir(dataset_full_path):
                model_full_path = os.path.join(dataset_full_path, model_name)

                if os.path.isdir(model_full_path):
                    # Check if evaluation.jsonl exists
                    eval_file = os.path.join(model_full_path, 'evaluation.jsonl')
                    if os.path.exists(eval_file):
                        dataset_model_pairs.append((dataset_path, model_name))

    return dataset_model_pairs


def process_model(base_dir, dataset, model):
    """
    Process a single model to calculate and save instance accuracy.

    Args:
        base_dir (str): Base directory (e.g., output)
        dataset (str): Dataset directory (e.g., MCQ/main_1-10)
        model (str): Model directory name

    Returns:
        bool: True if processing was successful, False otherwise
    """
    # Construct file paths
    evaluation_file = os.path.join(base_dir, dataset, model, 'evaluation.jsonl')
    instance_acc_file = os.path.join(base_dir, dataset, model, 'instance_acc.jsonl')
    instance_analysis_file = os.path.join(base_dir, dataset, model, 'instance_analysis.jsonl')

    # Check if evaluation file exists
    if not os.path.exists(evaluation_file):
        print(f"Error: Evaluation file not found: {evaluation_file}")
        return False

    # Calculate instance accuracy
    print(f"Processing {evaluation_file}...")
    instance_results = calculate_instance_accuracy(evaluation_file)

    # Save instance accuracy results
    save_instance_accuracy(instance_results, instance_acc_file)
    print(f"Instance accuracy saved to {instance_acc_file}")

    # Calculate and save summary statistics
    summary_stats = calculate_summary_statistics(instance_results)
    save_summary_statistics(summary_stats, instance_analysis_file)
    print(f"Instance analysis saved to {instance_analysis_file}")

    # Print summary
    print(f"Total instances: {summary_stats['num_instances']}")
    print(f"Average instance accuracy: {summary_stats['average_instance_accuracy']:.2%}")
    print(f"Standard deviation: {summary_stats['standard_deviation']:.4f}")
    print(f"Overall accuracy: {summary_stats['overall_accuracy']:.2%}")

    return True


def main():
    parser = argparse.ArgumentParser(description='Calculate instance accuracy from evaluation results')
    parser.add_argument('--base', required=True, help='Base directory (e.g., output)')
    parser.add_argument('--dataset', help='Optional: Specific dataset directory (e.g., MCQ/main_1-10)')
    parser.add_argument('--model', help='Optional: Specific model directory name')
    args = parser.parse_args()

    # If specific dataset and model are provided, process only that model
    if args.dataset and args.model:
        process_model(args.base, args.dataset, args.model)
        return

    # Otherwise, find and process all MCQ datasets and models
    dataset_model_pairs = find_mcq_datasets_and_models(args.base)

    if not dataset_model_pairs:
        print("No MCQ datasets or models found.")
        return

    print(f"Found {len(dataset_model_pairs)} dataset-model pairs to process.")

    # Process each dataset-model pair
    successful = 0
    for dataset, model in dataset_model_pairs:
        print(f"\nProcessing dataset: {dataset}, model: {model}")
        if process_model(args.base, dataset, model):
            successful += 1

    print(f"\nCompleted processing {successful} out of {len(dataset_model_pairs)} dataset-model pairs.")


if __name__ == "__main__":
    main()
