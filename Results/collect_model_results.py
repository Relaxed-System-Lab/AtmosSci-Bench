import os
import pandas as pd
import numpy as np
import subprocess

# Define the list of models and the max instance to filter
model_list = [
    "GPT-4o", "GPT-o1", "GPT-4o-mini",
    "Deepseek-v3-8K", "Deepseek-V3-8K","Deepseek_R1", "Deepseek_R1_original_precision",
    "QwQ-32B-Preview_8K", "QwQ-32B-Preview_16K", "QwQ-32B-Preview_32K", "QwQ-32B-Preview_32K_original_precision", "QwQ-32B-Preview_4K", "QwQ-32B-Preview_32K_ultra_precision",
    "Llama-3.3-70B-Instruct", "Llama-3.1-405B-Instruct-Turbo",
    "Qwen2.5-3B-Instruct", "Qwen2.5-7B-Instruct", "Qwen2.5-32B-Instruct", "Qwen2.5-72B-Instruct-Turbo",
    "Qwen2.5-Math-1.5B-Instruct", "Qwen2.5-Math-7B-Instruct", "Qwen2.5-Math-72B-Instruct",
    "deepseek-math-7b-rl", "deepseek-math-7b-instruct",
    "gemini-2.0-flash-thinking-exp-01-21_8K", "gemini-2.0-flash-thinking-exp-01-21_30K", "gemini-2.0-flash-thinking-exp-12-19_8K", "gemini-2.0-flash-exp", "gemini-2.0-flash-thinking-exp-01-21_30K-original-precision", "gemini-2.0-flash-thinking-exp-01-21_30K-ultra-precision",
    "gemma-2-9b-it", "gemma-2-27b-it",
    "climategpt-7b_4K","climategpt-70b",
    "Qwen2.5-7B-Instruct-original-precision", "Qwen2.5-7B-Instruct-ultra-precision", "Qwen2.5-Math-7B-Instruct-original-precision", "Qwen2.5-Math-7B-Instruct-ultra-precision",
]
MAX_INSTANCE = 10  # You can change this value as needed

# Initialize the results list
results = []

# Iterate through each model folder
for model in model_list:
    model_path = os.path.join(os.getcwd(), model)
    
    # Check if the folder exists
    if not os.path.isdir(model_path):
        print(f"Folder for model {model} does not exist.")
        continue

    # Define the file paths
    # instance_analysis_path = os.path.join(model_path, "instance_analysis_results.csv")
    instance_analysis_path = os.path.join(model_path, "combined_analysis_results.csv")
    # 
    llm_results_path = os.path.join(model_path, "llm_results.csv")

    UPDATE_ANSWER = True
    if UPDATE_ANSWER:
        subprocess.run(["python", "check_and_update_answer.py", llm_results_path, llm_results_path])
        subprocess.run(["python", "generate_accuracy.py", model_path])
        subprocess.run(["python", "instance_analysis.py", model_path])

    # Check if instance_analysis_results.csv exists
    if not os.path.isfile(instance_analysis_path):
        print(f"instance_analysis_results.csv not found for model {model}.")
        continue

    # Read the instance_analysis_results.csv file
    df = pd.read_csv(instance_analysis_path)

    # Filter rows based on MAX_INSTANCE
    filtered_df = df[(df['instance'] >= 1) & (df['instance'] <= MAX_INSTANCE)]

    # Calculate required statistics
    instance_count = len(filtered_df)
    acc_mean = round(filtered_df['correct_rate'].mean(), 2)
    acc_sigma = round(filtered_df['correct_rate'].std(), 2)
    no_answer_count = filtered_df['no_answer_count'].sum()
    error_count = filtered_df['error_count'].sum()

    # Calculate original_question_diff for instance == 1
    original_question_diff = None
    if 1 in filtered_df['instance'].values:
        instance_1_rate = filtered_df[filtered_df['instance'] == 1]['correct_rate'].values[0]
        original_question_diff = round(instance_1_rate - acc_mean, 2)

    # Extract type-specific correct rates
    hydrology_rate = filtered_df['Hydrology'].mean() if 'Hydrology' in filtered_df.columns else None
    atmospheric_dynamics_rate = filtered_df['Atmospheric Dynamics'].mean() if 'Atmospheric Dynamics' in filtered_df.columns else None
    atmospheric_physics_rate = filtered_df['Atmospheric Physics'].mean() if 'Atmospheric Physics' in filtered_df.columns else None
    geophysics_rate = filtered_df['Geophysics'].mean() if 'Geophysics' in filtered_df.columns else None
    physical_oceanography_rate = filtered_df['Physical Oceanography'].mean() if 'Physical Oceanography' in filtered_df.columns else None

    # Append the results for the model
    results.append({
        'model': model,
        'instance_count': instance_count,
        'acc_mean': acc_mean,
        'acc_sigma': acc_sigma,
        'no_answer_count': no_answer_count,
        'original_question_diff': original_question_diff,
        'error_count': error_count,
        'Hydrology_correct_rate': round(hydrology_rate, 2) if hydrology_rate is not None else None,
        'Atmospheric_Dynamics_correct_rate': round(atmospheric_dynamics_rate, 2) if atmospheric_dynamics_rate is not None else None,
        'Atmospheric_Physics_correct_rate': round(atmospheric_physics_rate, 2) if atmospheric_physics_rate is not None else None,
        'Geophysics_correct_rate': round(geophysics_rate, 2) if geophysics_rate is not None else None,
        'Physical_Oceanography_correct_rate': round(physical_oceanography_rate, 2) if physical_oceanography_rate is not None else None
    })

# Create a DataFrame from the results
results_df = pd.DataFrame(results)

# Save the results to a CSV file
output_file = f"models_result_{MAX_INSTANCE}.csv"
results_df.to_csv(output_file, index=False)

print(f"Results saved to {output_file}.")