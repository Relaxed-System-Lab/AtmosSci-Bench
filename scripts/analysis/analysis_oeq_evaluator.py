#!/usr/bin/env python3
"""
Analysis script for OEQ evaluator statistics.

This script analyzes the evaluator statistics from the results.json files in the OEQ dataset
and generates a CSV summary with the following metrics:
1. Number of subquestions = quantity.true + expression.true + llm.true + llm.false + llm.null
2. Quantity evaluator: true, false, and coverage = (true + false) / (number of subquestions)
3. Expression evaluator: true, false, and coverage = (true + false) / (number of subquestions - quantity.true)
4. LLM evaluator: true, false, and coverage = (true + false) / (number of subquestions - quantity.true - expression.true)
"""

import os
import json
import csv
import glob
from collections import defaultdict

def get_model_name(model_dir):
    """Extract a clean model name from the directory path."""
    return os.path.basename(model_dir)

def analyze_evaluator_stats(dataset_path):
    """
    Analyze evaluator statistics for all models in a dataset directory.
    
    Args:
        dataset_path: Path to the dataset directory (e.g., output/OEQ/oeq)
        
    Returns:
        A list of dictionaries with model evaluator statistics
    """
    results = []
    
    # Get all model directories
    model_dirs = [d for d in glob.glob(os.path.join(dataset_path, "*")) if os.path.isdir(d)]
    
    for model_dir in model_dirs:
        model_name = get_model_name(model_dir)
        model_data = {"model": model_name}
        
        # Get results.json for evaluator statistics
        results_path = os.path.join(model_dir, "results.json")
        if os.path.exists(results_path):
            try:
                with open(results_path, 'r') as f:
                    results_data = json.load(f)
                
                # Extract evaluator statistics
                evaluator_stats = results_data.get("evaluator_stats", {})
                
                # Get statistics for each evaluator
                quantity_stats = evaluator_stats.get("quantity", {"true": 0, "false": 0, "null": 0})
                expression_stats = evaluator_stats.get("expression", {"true": 0, "false": 0, "null": 0})
                llm_stats = evaluator_stats.get("llm", {"true": 0, "false": 0, "null": 0})
                
                # Calculate number of subquestions
                quantity_true = quantity_stats.get("true", 0)
                quantity_false = quantity_stats.get("false", 0)
                quantity_null = quantity_stats.get("null", 0)
                
                expression_true = expression_stats.get("true", 0)
                expression_false = expression_stats.get("false", 0)
                expression_null = expression_stats.get("null", 0)
                
                llm_true = llm_stats.get("true", 0)
                llm_false = llm_stats.get("false", 0)
                llm_null = llm_stats.get("null", 0)
                
                # 1. Number of subquestions
                num_subquestions = quantity_true + expression_true + llm_true + llm_false + llm_null
                model_data["num_subquestions"] = num_subquestions
                
                # 2. Quantity evaluator statistics
                model_data["quantity_true"] = quantity_true
                model_data["quantity_false"] = quantity_false
                model_data["quantity_null"] = quantity_null
                
                # Calculate quantity coverage
                quantity_coverage = 0
                if num_subquestions > 0:
                    quantity_coverage = (quantity_true + quantity_false) / num_subquestions
                model_data["quantity_coverage"] = quantity_coverage
                
                # 3. Expression evaluator statistics
                model_data["expression_true"] = expression_true
                model_data["expression_false"] = expression_false
                model_data["expression_null"] = expression_null
                
                # Calculate expression coverage
                expression_coverage = 0
                remaining_after_quantity = num_subquestions - quantity_true
                if remaining_after_quantity > 0:
                    expression_coverage = (expression_true + expression_false) / remaining_after_quantity
                model_data["expression_coverage"] = expression_coverage
                
                # 4. LLM evaluator statistics
                model_data["llm_true"] = llm_true
                model_data["llm_false"] = llm_false
                model_data["llm_null"] = llm_null
                
                # Calculate LLM coverage
                llm_coverage = 0
                remaining_after_expression = remaining_after_quantity - expression_true
                if remaining_after_expression > 0:
                    llm_coverage = (llm_true + llm_false) / remaining_after_expression
                model_data["llm_coverage"] = llm_coverage
                
                # Add overall accuracy
                model_data["overall_accuracy"] = results_data.get("overall_accuracy", 0)
                
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Error reading results.json for {model_name}: {e}")
        
        results.append(model_data)
    
    return results

def write_csv(results, output_path):
    """
    Write results to a CSV file.
    
    Args:
        results: List of dictionaries with model evaluator statistics
        output_path: Path to the output CSV file
    """
    if not results:
        print(f"No results to write to {output_path}")
        return
    
    # Define column order
    columns = [
        'model', 
        'overall_accuracy',
        'num_subquestions',
        'quantity_true', 
        'quantity_false', 
        'quantity_null', 
        'quantity_coverage',
        'expression_true', 
        'expression_false', 
        'expression_null', 
        'expression_coverage',
        'llm_true', 
        'llm_false', 
        'llm_null', 
        'llm_coverage'
    ]
    
    # Write to CSV
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Results written to {output_path}")

def main():
    """Main function to analyze OEQ evaluator statistics and generate CSV summary."""
    # Define paths
    oeq_dir = "output/OEQ/oeq"
    output_file = "scripts/analysis/oeq_evaluator_summary.csv"
    
    # Analyze OEQ evaluator statistics
    print(f"Analyzing evaluator statistics in {oeq_dir}...")
    evaluator_results = analyze_evaluator_stats(oeq_dir)
    write_csv(evaluator_results, output_file)
    
    print("Analysis complete!")

if __name__ == "__main__":
    main()
