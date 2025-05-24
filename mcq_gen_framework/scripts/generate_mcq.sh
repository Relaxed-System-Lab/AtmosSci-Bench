#!/bin/bash

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MCQ_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

# Run the Python script with specific parameters
cd "$MCQ_DIR"
python generate_dataset.py --dataset main --instance_range 1-10
python generate_dataset.py --dataset main --instance_range 11-30
python generate_dataset.py --dataset extra --instance_range 1-10


python convert_jsonl_to_csv.py