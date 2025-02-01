import pandas as pd
import os
import json
from question_collection import question_collection, INSTANCE_SIZE

from Questions.question import PRECISION


csv_columns = [
    "id", "seed", "type", "generation_method", "variables", "question", "answer", "options", "options_text", "correct_option", "options_types_str",
]


current_file_directory = os.path.dirname(os.path.abspath(__file__))
# csv_file = os.path.join(current_file_directory, "generated_datasets", f"question_collection_i{INSTANCE_SIZE}.csv")
if PRECISION == "original":
    csv_file = os.path.join(current_file_directory, "generated_datasets", f"question_collection_original_precision_i{INSTANCE_SIZE}_v2.csv")
elif PRECISION == "ultra":
    csv_file = os.path.join(current_file_directory, "generated_datasets", f"question_collection_ultra_precision_i{INSTANCE_SIZE}_v2.csv")
else:
    csv_file = os.path.join(current_file_directory, "generated_datasets", f"question_collection_i{INSTANCE_SIZE}_v2.csv")

# create DataFrame data
data = []
for question in question_collection:
    data.append({
        "id": question.id,
        "seed": question.seed,
        "type": question.type,
        "generation_method": "Original" if question.id.split("_")[1] == "1" else "Symbolic Extension",
        "variables": question.variables,
        "question": question.question(),
        "answer": question.answer(),
        "options": json.dumps(question.options_str_list()),
        "options_text": question.options_md(),
        "correct_option": question.options()["correct_option"],
        "options_types_str": question.options_types_str(),
    })


df = pd.DataFrame(data, columns=csv_columns)
df.to_csv(csv_file, index=False, encoding="utf-8")

print(f"CSV file generated: {csv_file}")
