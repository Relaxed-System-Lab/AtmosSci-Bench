import os
import pandas as pd
import sys

def analyze_gpt_results(path_dir):
    """
    Analyze GPT results from a CSV file.

    Args:
        path_dir (str): Path to the directory containing the CSV file.
    """
    file_path = os.path.join(path_dir, "llm_results.csv")

    # Try reading the CSV file
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return

    # Extract instance information
    df['instance'] = df['id'].str.extract(r'q\d+_(\d+)')

    # Calculate statistics for each instance
    instance_results = df.groupby('instance').agg(
        correct_rate=('correct', 'mean'),
        no_answer_count=('NoAnswer', 'sum'),
        total_questions=('id', 'count'),
        correct_count=('correct', 'sum'),
        error_count=('Error', 'sum')
    ).reset_index()

    # Convert correct rate to percentage format
    instance_results['correct_rate'] = (instance_results['correct_rate'] * 100).round(2)

    # Add a "correct/total" column
    instance_results['correct_over_total'] = instance_results['correct_count'].astype(int).astype(str) + "/" + instance_results['total_questions'].astype(int).astype(str)

    # Calculate accuracy for each type and merge with instance_results
    type_correct_rates = df.groupby(['instance', 'type']).agg(
        type_correct_rate=('correct', 'mean')
    ).reset_index()

    type_correct_rates['type_correct_rate'] = (type_correct_rates['type_correct_rate'] * 100).round(2)

    # Pivot type_correct_rates to have one column per type
    type_correct_rates_pivot = type_correct_rates.pivot(index='instance', columns='type', values='type_correct_rate').reset_index()

    # Merge instance results with type correct rates
    combined_results = pd.merge(instance_results, type_correct_rates_pivot, on='instance', how='left')

    # Ensure all required type columns are present
    for col in ['Hydrology', 'Atmospheric Dynamics', 'Atmospheric Physics', 'Geophysics', 'Physical Oceanography']:
        if col not in combined_results.columns:
            combined_results[col] = None

    # Print results
    print("Analysis Results:")
    print(combined_results)

    # Save results to a CSV file
    output_file = os.path.join(os.path.dirname(file_path), 'combined_analysis_results.csv')
    combined_results.to_csv(output_file, index=False)
    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    """
    Main entry point for the script. Supports both direct execution and command-line arguments.
    """
    if len(sys.argv) > 1:
        # Command-line mode: Use the file path provided as an argument
        if len(sys.argv) != 2:
            print("Usage: python script.py <PATH_DIR>")
        else:
            path_dir = sys.argv[1]
            if os.path.exists(path_dir):
                analyze_gpt_results(path_dir)
            else:
                print(f"Error: Path does not exist: {path_dir}")
    else:
        # Direct execution mode: Use default directory and file
        path_dir = "Evaluation/2025-01-17_11-26-04_gpt-4o_b1(Final)"

        if os.path.exists(path_dir):
            analyze_gpt_results(path_dir)
        else:
            print(f"Error: Default path does not exist: {path_dir}")
