# AtmosSci-Bench

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3109/)

## Introduction

AtmosSci-Bench is a comprehensive benchmark framework for evaluating Large Language Models (LLMs) on atmospheric science tasks. This repository contains the code and resources for the paper: "AtmosSci-Bench: Evaluating the Recent Advance of Large Language Model for Atmospheric Science".

The benchmark consists of:
- **Multiple-Choice Questions (MCQ)**: Rigorous, physics-based questions generated using symbolic techniques
- **Open-Ended Questions (OEQ)**: Problems requiring step-by-step reasoning and detailed explanations
- **Evaluation Framework**: Tools for assessing LLM performance on atmospheric science tasks

## Project Overview

AtmosSci-Bench evaluates LLMs on their ability to understand and reason about atmospheric science concepts. The benchmark covers various domains including:
- Atmospheric Dynamics
- Hydrology
- Geophysics
- Climate Science
- Meteorology

## Getting Started

### Prerequisites

- Python 3.10.9
- Dependencies listed in `requirements.txt`
- GPU resources for local model inference (optional)

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/jimschenchen/AtmosSci-Bench-NeurIPS2025.git
   cd atmossci-bench
   ```

2. Run the setup script:
   ```bash
   chmod +x ./setup.sh
   ./setup.sh
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## MCQ Generation Framework

The MCQ Generation Framework creates rigorous, physics-based multiple-choice questions using symbolic techniques. It ensures questions test genuine reasoning ability rather than pattern matching.

### Key Features

- **Symbolic Question Generation**: Creates questions with variable parameters
- **Template-Based Perturbation**: Uses placeholder variables that can be systematically instantiated
- **Rule-Based Mechanism**: Ensures logical coherence and alignment with physical laws
- **Diverse Question Types**: Covers various domains in atmospheric science

### Generating MCQs

To generate the MCQ dataset:

```bash
./mcq_gen_framework/scripts/generate_mcq.sh
```

For more details, see [mcq_gen_framework/README.md](mcq_gen_framework/README.md).

## Dataset

The benchmark dataset is available in the `data/` directory. It includes:

- **Main MCQ Set**: Core multiple-choice questions
- **Extra MCQ Set**: Additional multiple-choice questions
- **OEQ Set**: Open-ended questions requiring detailed explanations

If you generate the dataset using the MCQ Generation Framework, the output will be placed in `data/`.

## LLM Inference

### Inference Framework

#### API-based Models

Models hosted by providers such as OpenAI, Google, Deepseek, and TogetherAI are accessed via public inference APIs.

1. Create a `.env` file using `.env_example` as a template
2. Add your API keys to the `.env` file
3. Run inference using the provided scripts

We use the `Ray` Python library for parallel execution of API requests, enabling efficient large-scale evaluation.

#### Local Models

Models available through HuggingFace can be run locally using:
- HuggingFace `transformers` library
- `Accelerate` for GPU acceleration

Our evaluation hardware setups include:
- Single machine with 8×NVIDIA RTX 4090 GPUs
- Two nodes with 4×NVIDIA A800 GPUs each

Performance varies by model size:
- 70B models: ~90 hours with batch size 4
- 7B models: ~6 hours with batch size 64

### Running Inference

All output is stored in the `/output` directory, with separate folders for each model and dataset.

#### Using Existing Models

1. Find the LLM name and base in `src/models/__init__.py` (BASE_REGISTRY)
2. Run the appropriate script:
   - API-based models:
     ```bash
     # Edit parameters in the script first
     ./scripts/generate_api/generate.sh
     ```
   - Local models:
     ```bash
     # Edit parameters in the script first
     ./scripts/generate_gpu/generate_2gpu.sh
     ```

#### Adding New Models

1. Add the model to the appropriate file:
   - API-based: `src/models/api_base.py` and `src/models/__init__.py`
   - Local-based: `src/models/local_base.py` and `src/models/__init__.py`
2. Run inference using the scripts mentioned above

## LLM Evaluation

To evaluate model responses:

1. Edit parameters in `scripts/evaluate/evaluate.sh`
2. Run the evaluation script:
   ```bash
   ./scripts/evaluate/evaluate.sh
   ```

This creates `evaluation.jsonl` and `results.json` in the same folder as the inference output.

## LLM Evaluation Analysis

To analyze evaluation results:

1. Ensure result consistency:
   ```bash
   python scripts/generate_result2.py
   ```

2. Generate analysis results:
   ```bash
   python scripts/analysis/analysis_*.py
   ```

3. Generate instance analysis:
   ```bash
   python scripts/instance_analysis/create_instance_acc.py
   ```

## Data Hosting

The dataset is hosted on Kaggle: [AtmosSci-Bench Dataset](https://kaggle.com/datasets/f1d2d8c65b440f5c527d30d31800c5211817cec354ffb47e5c45a829667d90df)

Additional documentation:
- Croissant metadata: `doc/croissant/atmossci-bench-metadata-croissant.json`
- Validation report: `doc/croissant/report_croissant-validation_ATMOSSCI-BENCH.md`

## Settings and Resources

Detailed information about hyperparameters and experimental compute resources is available in [doc/settings.md](doc/settings.md).

## Sources and Licenses

Information about model and library usage licenses, data sources, and usage statements can be found in [doc/sources_license.md](doc/sources_license.md).