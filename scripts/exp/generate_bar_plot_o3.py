import matplotlib.pyplot as plt
import numpy as np
import os

# o3 model results
data = {
    "model": ["4K", "8K", "16K", "32K", "40K"],
    "Hydro": [84.0, 98.0, 96.0, 100.0, 98.0],
    "AtmDyn": [56.76, 72.7, 84.32, 87.57, 88.65],
    "AtmosPhy": [83.57, 90.0, 90.0, 90.71, 90.0],
    "GeoPhy": [68.57, 94.28, 81.43, 95.71, 95.71],
    "PhyOcean": [60.0, 80.0, 85.0, 87.5, 77.5],
    "Overall Acc": [65.82, 80.89, 86.12, 90.0, 89.7],
}

# o3-mini bar plot

base_path = "./"
output_path = "output_plots"
os.makedirs(output_path, exist_ok=True)

# Colors
colors = ["#7DABCF", "#CFE7EB", "#FBC1AD", "#F46E49", "#FFDF70", "#E5E1E0"]

# Extract values
categories = ["Hydro", "AtmDyn", "AtmosPhy", "GeoPhy", "PhyOcean", "Overall Acc"]
models = data["model"]
values = [data[category] for category in categories]

# Bar width and positions
x = np.arange(len(categories))
bar_width = 0.18
positions = [x + i * bar_width for i in range(len(models))]

# Plotting
plt.figure(figsize=(14, 5))
for i, (pos, model, value) in enumerate(zip(positions, models, zip(*values))):
    plt.bar(pos, value, width=bar_width, label=model, color=colors[i])

# Formatting
plt.xlabel("Metrics", fontsize=28)
plt.ylabel("Accuracy (%)", fontsize=28)
plt.xticks(x + 1.5 * bar_width, categories, fontsize=25)
plt.yticks(fontsize=25)
# plt.legend(title="Reasoning Steps", fontsize=14, title_fontsize=14, loc="upper right", ncol=4)
plt.legend(title="", fontsize=14, title_fontsize=14, loc="upper right", ncol=5)

plt.tight_layout()

# Save figure
output_file = os.path.join(output_path, "bar_plot_o3mini.png")
plt.savefig(output_file)
plt.close()

print(f"Bar plot generated and saved to '{output_path}' as 'bar_plot_o3mini.png'.")
