#!/bin/bash

PROJECT_ROOT=$(dirname "$(dirname "$(dirname "$0")")")
cd "$PROJECT_ROOT"

# Run the evaluation script
BASE=openai
MODEL=gpt4o
TOKEN=8000

python3 -m src.evaluate.evaluate_mcq --base $BASE --model $MODEL --max-tokens $TOKEN --data extra_1-10 --type MCQ --tolerance 0.05
python3 -m src.evaluate.evaluate_mcq --base $BASE --model $MODEL --max-tokens $TOKEN --data main_1-10 --type MCQ --tolerance 0.05
python3 -m src.evaluate.evaluate --base $BASE --model $MODEL --max-tokens $TOKEN --data oeq --type OEQ --tolerance 0.05 --enable-llm
