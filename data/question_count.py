import os
import json
import csv
from collections import defaultdict

# File path and expected types
jsonl_dir = './jsonl'
filenames = ['extra_1-10.jsonl', 'main_1-10.jsonl', 'oeq.jsonl']
types = [
    "Atmospheric Dynamics",
    "Atmospheric Physics",
    "Geophysics",
    "Hydrology",
    "Physical Oceanography"
]

# Store statistics results
results = {}

for filename in filenames:
    filepath = os.path.join(jsonl_dir, filename)
    count_dict = defaultdict(int)
    total = 0

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            item = json.loads(line)
            qtype = item.get('type', None)
            if qtype in types:
                count_dict[qtype] += 1
            total += 1

    # Ensure every type is recorded (even if zero)
    for t in types:
        count_dict[t] = count_dict.get(t, 0)
    count_dict["Total"] = total
    results[filename] = count_dict

# Write to CSV file
output_csv = 'question_count.csv'
with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    header = ['Filename'] + types + ['Total']
    writer.writerow(header)
    
    for fname, count_dict in results.items():
        row = [fname] + [count_dict[t] for t in types] + [count_dict["Total"]]
        writer.writerow(row)

print(f"Written results to {output_csv}")
