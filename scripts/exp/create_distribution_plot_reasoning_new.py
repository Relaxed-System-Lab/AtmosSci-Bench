import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Modified model list
selected_models = [
    "o3-mini-30K",
    "Deepseek_R1", 
    "QwQ-32B-Preview_32K", 
    "gemini-2.0-flash-thinking-exp-01-21_30K"
]

base_path = "./"  # Replace with the path to the model folders
output_path = "output_plots"  # Path to save output images
os.makedirs(output_path, exist_ok=True)

# sns.set_theme(style="whitegrid", palette="pastel")

# Set figure layout
fig, axes = plt.subplots(1, 4, figsize=(23, 7), sharey=True)

MAX_INSTANCE = 30

SIZE = 16

# Iterate through models and plot subfigures
for idx, model_folder in enumerate(selected_models):
    model_path = os.path.join(base_path, model_folder)
    csv_file = os.path.join(model_path, "combined_analysis_results.csv")
    
    if not os.path.isfile(csv_file):
        print(f"File not found: {csv_file}")
        continue

    # Load data
    data = pd.read_csv(csv_file)
    data = data[data["instance"] <= MAX_INSTANCE]

    # Check required columns
    if "instance" not in data.columns or "correct_rate" not in data.columns:
        print(f"Missing required columns in: {csv_file}")
        continue

    # Plot histogram
    sns.histplot(data["correct_rate"], kde=True, bins=10, ax=axes[idx], color="#7DABCF", linewidth=1, edgecolor="#ffffff")

    # Draw vertical dashed line at instance == 1
    if 1 in data["instance"].values:
        instance_1_rate = data.loc[data["instance"] == 1, "correct_rate"].values[0]
        axes[idx].axvline(x=instance_1_rate, color="black", linestyle="--", linewidth=2.5)
    else:
        print(f"Instance == 1 not found in: {csv_file}")
    
    # Set titles and labels
    mean_correct_rate = data["correct_rate"].mean()
    std_correct_rate = data["correct_rate"].std()
    model_folder_map = {
        "Deepseek_R1": "Deepseek-R1",
        "QwQ-32B-Preview_32K": "QwQ-32B",
        "gemini-2.0-flash-thinking-exp-01-21_30K": "Gemini-2.0-flash-think",
        "o3-mini-30K": "o3-mini"
    }
    axes[idx].set_title(f"{model_folder_map[model_folder]}\nMean: {mean_correct_rate:.1f} ± {std_correct_rate:.1f}", fontsize=19+SIZE)
    axes[idx].set_xlabel("", fontsize=24+SIZE)
    if idx == 0:
        axes[idx].set_ylabel("", fontsize=24+SIZE)

    axes[idx].grid(axis="y", linestyle="--", alpha=0.8)
    axes[idx].grid(axis="x", linestyle="--", alpha=0.8)


# Set shared axis labels and increase spacing
fig.supxlabel("GSM Symbolic Accuracy (%)", fontsize=24+SIZE, y=0.03)  # Lower y increases spacing
fig.supylabel("Frequency", fontsize=24+SIZE, x=0.00)

# plt.grid(axis="y", linestyle="--", alpha=0.7)

# Adjust tick font size
for ax in axes:
    ax.tick_params(axis='x', labelsize=18+SIZE)
    ax.tick_params(axis='y', labelsize=18+SIZE)

# Adjust layout
plt.tight_layout(rect=[0.01, 0.00, 0.99, 1])  # left, bottom, right, top (1 is farthest right)

plt.subplots_adjust(wspace=0.1)  # Increase horizontal spacing between subplots

# Save image
output_file = os.path.join(output_path, "reasoning_model_distribution.png")
plt.savefig(output_file)
plt.close()

print(f"Distribution plot generated and saved to '{output_path}' as 'reasoning_model_distribution.png'.")
