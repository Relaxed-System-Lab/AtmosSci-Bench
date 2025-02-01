import matplotlib.pyplot as plt
import numpy as np
import os

# Data
data = {
    "model": ["4K", "8K", "16K", "32K"],
    "Hydro": [58.0, 82.0, 82.0, 88.0],
    "AtmDyn": [29.73, 55.41, 61.08, 60.27],
    "AtmosPhy": [57.86, 82.14, 87.86, 87.86],
    "GeoPhy": [28.57, 67.14, 71.43, 74.28],
    "PhyOcean": [27.5, 42.5, 62.5, 60.0],
    "Overall Acc": [37.46, 63.43, 69.4, 69.55],
}

base_path = "./"  #
output_path = "output_plots"  #
os.makedirs(output_path, exist_ok=True)

# Colors
colors = ["#7DABCF", "#CFE7EB", "#FBC1AD", "#F46E49", "#FFDF70", "#E5E1E0"]

# Extract values
categories = ["Hydro", "AtmDyn", "AtmosPhy", "GeoPhy", "PhyOcean", "Overall Acc"]
models = data["model"]
values = [data[category] for category in categories]

# Bar width and positions
x = np.arange(len(categories))
bar_width = 0.2
positions = [x + i * bar_width for i in range(len(models))]

# Plot
plt.figure(figsize=(14, 5))
for i, (pos, model, value) in enumerate(zip(positions, models, zip(*values))):
    plt.bar(pos, value, width=bar_width, label=model, color=colors[i])

# Formatting
plt.xlabel("Metrics", fontsize=28)
plt.ylabel("Accuracy (%)", fontsize=28)
plt.xticks(x + 1.5 * bar_width, categories, fontsize=25)
plt.yticks(fontsize=25)
# plt.legend(title="Reasoning Steps", fontsize=14, title_fontsize=14, loc="upper right", ncol=4)
plt.legend(title="", fontsize=18, title_fontsize=14, loc="upper right", ncol=4)

plt.tight_layout()

output_file = os.path.join(output_path, "bar_plot.png")
plt.savefig(output_file)
plt.close()

print(f"Image has been saved to {output_path} folder 'bar_plot.png'。")
