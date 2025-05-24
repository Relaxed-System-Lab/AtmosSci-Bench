"""
Multiple Choice Question (MCQ) type definition and prompt template.
"""

# System message for MCQ
# SYSTEM_MESSAGE = """You are an Earth Science Expert answering multiple-choice questions.

# Instructions:
# 1. Carefully analyze the question and options provided.
# 2. Please think step by step. Use logical reasoning and critical thinking to generate a detailed explanation or steps leading to the answer.
# 3. At the end of your response, ensure to provide the correct option (A/B/C/D) on a new line in the following format strictly:
# **Final Answer**: \\[ \\boxed{{A/B/C/D}} \\]
# """

SYSTEM_MESSAGE = """You are an Earth Science Expert answering multiple-choice questions. Please think step by step. Use logical reasoning and critical thinking to generate a detailed explanation or steps leading to the answer. At the end of your response, ensure to provide the correct option (A/B/C/D) on a new line in the following format strictly:
**Final Answer**: \\[ \\boxed{{A/B/C/D}} \\]

"""

def get_prompt(question, options=None, knowledge=None):
    """
    Get the formatted prompt for a multiple-choice question.

    Args:
        question (str): The question to answer
        options (list, optional): List of options for the multiple-choice question
        knowledge (str, optional): Additional knowledge or context for the question

    Returns:
        str: The formatted prompt
    """
    # Format options if provided
    options_str = ""
    if options:
        for i, option in enumerate(options):
            options_str += f"{chr(65 + i)}. {option}\n"

#     prompt = f"""Here is the question: {question}
# Here are the options:
# {options_str}"""

    prompt = f"""Question: {question}
Options:{options_str}"""
    if knowledge:
        prompt += f"\nKnowledge:\n{knowledge}"

    return prompt
