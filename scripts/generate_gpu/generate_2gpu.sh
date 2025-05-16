#!/bin/bash

PROJECT_ROOT=$(dirname "$(dirname "$(dirname "$0")")")
cd "$PROJECT_ROOT"

BASE=huggingface
MODEL=Qwen2.5-72B-GeoGPT
TOKEN=8000
GPU="0,1"
BATCH=2

python3 -m src.generate.generate --base $BASE --model $MODEL --max-tokens $TOKEN --data oeq --type OEQ --retries 1 --parallel $BATCH --log-level DEBUG --gpu $GPU
python3 -m src.generate.generate --base $BASE --model $MODEL --max-tokens $TOKEN --data extra_1-10 --type MCQ --retries 1 --parallel $BATCH --log-level DEBUG --gpu $GPU
python3 -m src.generate.generate --base $BASE --model $MODEL --max-tokens $TOKEN --data main_1-10 --type MCQ --retries 1 --parallel $BATCH --log-level DEBUG --gpu $GPU
