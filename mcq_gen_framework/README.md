# MCQ Generation Framework

A symbolic Multiple-Choice Question (MCQ) generation framework for evaluating the reasoning and problem-solving capabilities of Large Language Models (LLMs).

## Overview

This framework generates rigorous, physics-based multiple-choice questions using symbolic techniques. It creates scalable and diverse question sets while ensuring logical coherence and alignment with real-world physical laws. The framework uses template-based question perturbation with placeholder variables that can be systematically instantiated through symbolic extensions, ensuring models are tested on genuine reasoning ability rather than pattern matching.

## Key Features

- **Symbolic Question Generation**: Creates questions with variable parameters that test true reasoning
- **Template-Based Perturbation**: Uses placeholder variables that can be systematically instantiated
- **Rule-Based Mechanism**: Ensures logical coherence and alignment with physical laws
- **Diverse Question Types**: Covers various domains including Atmospheric Dynamics, Hydrology, Geophysics, and more
- **Automatic Option Generation**: Creates plausible distractors to test understanding


## Usage

To generate the MCQ dataset, simply run:

```bash
./mcq_gen_framework/scripts/generate_mcq.sh
```

## Output

The generated questions are saved in:
- JSONL format: `mcq_gen_framework/output/*.jsonl`
- CSV format: `mcq_gen_framework/output/*.csv`

Each question includes:
- Question ID
- Problem statement
- Correct answer
- Multiple choice options
- Correct option letter
- Question type

## Extending the Framework

To add new questions:
1. Create a new directory in `main/` or `extra/` (e.g., `q105/`)
2. Create a Python file with the same name (e.g., `q105.py`)
3. Implement a class that inherits from `Question`
4. Define the question template, variables, and calculation function
5. Update the question range in `generate_dataset.py` if needed
