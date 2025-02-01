import pandas as pd
import os
import sys

def analyze_evaluation_results(path_dir):
    # Define paths
    result_path = os.path.join(path_dir, "llm_results.csv")
    output_path = os.path.join(path_dir, "accuracy.csv")
    
    # Check if the results file exists
    if not os.path.exists(result_path):
        print(f"Error: {result_path} does not exist.")
        return
    
    # Load the CSV file
    data = pd.read_csv(result_path)
    
    # Parse the 'id' column to extract question template and instance information
    data[['template', 'instance']] = data['id'].str.extract(r'q(\d+)_(\d+)')
    data['template'] = data['template'].astype(int)
    data['instance'] = data['instance'].astype(int)
    
    # Summarize the data for each question template
    summary = []
    for template, group in data.groupby('template'):
        total = len(group)
        correct_count = group['correct'].sum()
        no_answer_count = group['NoAnswer'].sum()
        original_correct = group[(group['instance'] == 1) & (group['correct'] == True)].shape[0]
        accuracy = round((correct_count / total) * 100,2)
        error_count = group['Error'].sum()
        
        summary.append({
            'Question Template': template,
            'Accuracy (%)': accuracy,
            'Correct/Total': f"{correct_count}/{total}",
            'NoAnswer Count': no_answer_count,
            'Original Correct': original_correct,
            'Error Count': error_count
        })
    
    # Create a DataFrame for the summary
    summary_df = pd.DataFrame(summary)
    
    # Sort the summary by Question Template
    summary_df = summary_df.sort_values('Question Template')
    
    # Display or save the summary
    print(summary_df)
    summary_df.to_csv(output_path, index=False)
    print(f"Summary saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Check for command-line argument
        if len(sys.argv) != 2:
            print("Usage: python script.py <PATH_DIR>")
        else:
            path_dir = sys.argv[1]
            analyze_evaluation_results(path_dir)
    else:
        default_path = "Evaluation/2025-01-17_11-26-04_gpt-4o_b1(Final)"
        analyze_evaluation_results(default_path)