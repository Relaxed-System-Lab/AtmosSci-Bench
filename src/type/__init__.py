"""
Question type module for generating responses to physics problems.

This module contains definitions for different question types.
"""

from . import OEQ, MCQ, CODE

# Dictionary mapping question type names to their modules
TYPE_REGISTRY = {
    "OEQ": OEQ,
    "MCQ": MCQ,
    "CODE": CODE
}

def get_type_module(question_type):
    """
    Get the module for the given question type.
    
    Args:
        question_type (str): Name of the question type
        
    Returns:
        module: The question type module
        
    Raises:
        ValueError: If the question type is not supported
    """
    if question_type not in TYPE_REGISTRY:
        raise ValueError(f"Question type {question_type} is not supported. Supported types: {list(TYPE_REGISTRY.keys())}")
    
    return TYPE_REGISTRY[question_type]
