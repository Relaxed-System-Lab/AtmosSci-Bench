#!/usr/bin/env python3
"""
Analysis script for MCQ results.

This script analyzes the results from the MCQ datasets (main_1-10 and extra_1-10)
and generates CSV summaries with accuracies by question type, overall accuracy,
and standard deviation.
"""

import os
import json
import csv
import glob
from collections import defaultdict

def get_model_name(model_dir):
    """Extract a clean model name from the directory path."""
    return os.path.basename(model_dir)

def analyze_dataset(dataset_path):
    """
    Analyze all models in a dataset directory.
    
    Args:
        dataset_path: Path to the dataset directory (e.g., output/MCQ/main_1-10)
        
    Returns:
        A list of dictionaries with model results
    """
    results = []
    
    # Get all model directories
    model_dirs = [d for d in glob.glob(os.path.join(dataset_path, "*")) if os.path.isdir(d)]
    
    for model_dir in model_dirs:
        model_name = get_model_name(model_dir)
        model_data = {"model": model_name}
        
        # Get result2.json for question type accuracies
        result2_path = os.path.join(model_dir, "result2.json")
        if os.path.exists(result2_path):
            try:
                with open(result2_path, 'r') as f:
                    result2_data = json.load(f)
                
                # Extract overall accuracy
                model_data["overall_accuracy"] = result2_data.get("overall_accuracy", None)
                
                # Extract question type accuracies
                question_types = result2_data.get("question_types", {})
                for q_type, q_data in question_types.items():
                    model_data[f"{q_type}"] = q_data.get("accuracy", None)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Error reading result2.json for {model_name}: {e}")
        
        # Get instance_analysis.jsonl for standard deviation
        instance_analysis_path = os.path.join(model_dir, "instance_analysis.jsonl")
        if os.path.exists(instance_analysis_path):
            try:
                with open(instance_analysis_path, 'r') as f:
                    instance_data = json.loads(f.read().strip())
                
                model_data["standard_deviation"] = instance_data.get("standard_deviation", None)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Error reading instance_analysis.jsonl for {model_name}: {e}")
        
        results.append(model_data)
    
    return results

def write_csv(results, output_path):
    """
    Write results to a CSV file.
    
    Args:
        results: List of dictionaries with model results
        output_path: Path to the output CSV file
    """
    if not results:
        print(f"No results to write to {output_path}")
        return
    
    # Get all unique keys across all result dictionaries
    all_keys = set()
    for result in results:
        all_keys.update(result.keys())
    
    # Remove 'model' from all_keys and add it back as the first column
    all_keys.discard('model')
    
    # Sort keys: model first, then overall_accuracy, then standard_deviation, then question types
    columns = ['model', 'overall_accuracy', 'standard_deviation']
    
    # Add question type columns (sorted alphabetically)
    question_type_columns = sorted([k for k in all_keys if k not in columns])
    columns.extend(question_type_columns)
    
    # Write to CSV
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Results written to {output_path}")

def main():
    """Main function to analyze MCQ results and generate CSV summaries."""
    # Define paths
    base_dir = "output/MCQ"
    main_dir = os.path.join(base_dir, "main_1-10")
    extra_dir = os.path.join(base_dir, "extra_1-10")
    
    main_output = "scripts/analysis/main_1-10_summary.csv"
    extra_output = "scripts/analysis/extra_1-10_analysis.csv"
    
    # Analyze main dataset
    print(f"Analyzing {main_dir}...")
    main_results = analyze_dataset(main_dir)
    write_csv(main_results, main_output)
    
    # Analyze extra dataset
    print(f"Analyzing {extra_dir}...")
    extra_results = analyze_dataset(extra_dir)
    write_csv(extra_results, extra_output)
    
    print("Analysis complete!")

if __name__ == "__main__":
    main()
