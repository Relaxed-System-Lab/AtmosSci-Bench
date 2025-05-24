"""
Open-Ended Question (OEQ) type definition and prompt template.
"""

# Prompt template for Open-Ended Questions (OEQ)
TEMPLATE = """
Question: {question}
"""

# System message for OEQ
SYSTEM_MESSAGE = """You are an expert in Earth System Science. Think step by step using logical reasoning and scientific principles. Provide a detailed explanation or derivation leading to your answer.If the question includes subparts (e.g., a), b)), address each subpart sequentially. Conclude each subpart with its final result formatted as a LaTeX expression, using:
a) \\boxed{...}
b) \\boxed{...}
For single-part questions, conclude with a single \\boxed{final_answer}."""

def get_prompt(question):
    """
    Get the formatted prompt for an open-ended question.

    Args:
        question (str): The question to answer

    Returns:
        str: The formatted prompt
    """
    return TEMPLATE.format(question=question)
