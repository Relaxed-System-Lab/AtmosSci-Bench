# Question Types

This directory contains definitions for different question types used in the generation process.

## Available Question Types

### OEQ (Open-Ended Questions)

Open-ended questions require the model to provide a complete solution with step-by-step reasoning and a final answer.

The prompt template for OEQ includes:
- Instructions to answer step by step
- Guidelines for identifying key concepts and equations
- Instructions to set up the problem systematically
- Requirements for proper units in calculations
- Format for presenting the final answer

### MCQ (Multiple Choice Questions)

Multiple choice questions require the model to analyze different options and select the correct one.

The prompt template for MCQ includes:
- Instructions to analyze each option systematically
- Guidelines for identifying key concepts and equations
- Requirements for proper units in calculations
- Instructions to explain why the chosen option is correct and others are incorrect
- Format for presenting the final answer

## Usage

Question type modules are used by the model implementations to get the appropriate prompt template and system message for a given question type.

```python
from generate.type import get_type_module

# Get the appropriate question type module
type_module = get_type_module(question_type)  # "OEQ" or "MCQ"

# Get the prompt and system message
prompt = type_module.get_prompt(question)
system_message = type_module.SYSTEM_MESSAGE
```

## Adding New Question Types

To add a new question type:

1. Create a new Python file in this directory (e.g., `NEW_TYPE.py`)
2. Define the `TEMPLATE` and `SYSTEM_MESSAGE` constants
3. Implement the `get_prompt(question)` function
4. Add the new type to the `TYPE_REGISTRY` in `__init__.py`

Example:

```python
# In NEW_TYPE.py
"""
New Question Type definition and prompt template.
"""

# Prompt template
TEMPLATE = """
Question: {question}

Prompt: [Instructions for answering this type of question]
"""

# System message
SYSTEM_MESSAGE = "You are an expert who [specific expertise for this question type]."

def get_prompt(question):
    """Get the formatted prompt for this question type."""
    return TEMPLATE.format(question=question)

# In __init__.py, add to TYPE_REGISTRY
from . import NEW_TYPE

TYPE_REGISTRY = {
    "OEQ": OEQ,
    "MCQ": MCQ,
    "NEW_TYPE": NEW_TYPE,
}
```
