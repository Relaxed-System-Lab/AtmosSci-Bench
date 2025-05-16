#!/bin/bash

# DESCRIPTION:
#   This script runs the generate_gpu_parallel.py module to process multiple
#   datasets in parallel across multiple GPU groups. It optimizes GPU utilization
#   by distributing datasets across available GPUs.
#
# EXECUTION STRATEGY:
#   - GPUs are divided into GPU_PARALLEL groups
#   - Each GPU group processes its assigned datasets SEQUENTIALLY
#   - Different GPU groups run in PARALLEL
#   - Datasets are distributed to balance workload across GPU groups
#
# PARAMETERS:
#   MODEL         - The Hugging Face model to use (default: Qwen2.5-72B-GeoGPT)
#   TOKEN         - Maximum number of tokens in the response (default: 8000)
#   BATCH         - Number of parallel processes per GPU group (default: 2)
#   GPU_PARALLEL  - Number of GPU groups to create (default: 2)
#   DATASET       - Space-separated list of datasets to process
#   GPU           - Optional: Specific GPU IDs to use (e.g., "0,1,2,3")
#                   If not set, all available GPUs will be used
#



PROJECT_ROOT=$(dirname "$(dirname "$(dirname "$0")")")
cd "$PROJECT_ROOT"

# BASE=huggingface
MODEL=Qwen2.5-72B-GeoGPT
TOKEN=8000
BATCH=2

# This will split GPU into GPU_PARALLEL group and each group. And dataset will split into GPU_PARALLEL group to let GPU_PARALLEL group GPU to run.
GPU_PARALLEL=2
DATASET=MCQ/main_1-10 MCQ/extra_1-10 OEQ/oeq


nohup python3 -m src.generate.generate_gpu_parallel \
  --model $MODEL \
  --gpu $GPU \
  --gpu-parallel $GPU_PARALLEL \
  --datasets $DATASET \
  --max-tokens $TOKEN \
  --retries 1 \
  --parallel $BATCH \
  --log-level INFO \
  --worker-logging
