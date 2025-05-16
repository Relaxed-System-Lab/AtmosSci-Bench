"""
LLM-as-Judge evaluator for comparing answers using an LLM.
"""

import os
import logging
import json
from openai import OpenAI
from .base_evaluator import BaseEvaluator

logger = logging.getLogger(__name__)

class LLMEvaluator(BaseEvaluator):
    """
    Evaluator that uses an LLM to judge if answers are equivalent.
    """

    def __init__(self, model_name="gpt-4o-mini", tolerance=0.05):
        """
        Initialize the LLM evaluator.

        Args:
            model_name (str): Name of the LLM model to use (default: gpt-4o-mini)
            tolerance (float): Not used for LLM evaluation, but kept for API consistency
        """
        super().__init__(tolerance=tolerance)
        self.model_name = model_name
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    def evaluate(self, expected, actual):
        """
        Evaluate if the actual answer is equivalent to the expected answer using an LLM.

        Args:
            expected (str): The expected answer in LaTeX format
            actual (str): The actual answer from the model in LaTeX format

        Returns:
            dict: A dictionary containing:
                - 'is_correct' (bool): Whether the answer is correct
                - 'details' (dict): Additional details about the evaluation
        """
        try:
            result, explanation = self.compare_with_llm(expected, actual)
            return {
                'is_correct': result,
                'details': {
                    'evaluator': str(self),
                    'expected': expected,
                    'actual': actual,
                    'model': self.model_name,
                    'explanation': explanation,
                    'error': None
                }
            }
        except Exception as e:
            logger.warning(f"LLMEvaluator error: {e}")
            return {
                'is_correct': None,
                'details': {
                    'evaluator': str(self),
                    'expected': expected,
                    'actual': actual,
                    'model': self.model_name,
                    'explanation': None,
                    'error': str(e)
                }
            }

    def compare_with_llm(self, expected, actual):
        """
        Use an LLM to compare two answers.

        Args:
            expected (str): Expected answer in LaTeX format
            actual (str): Actual answer in LaTeX format

        Returns:
            tuple: (is_correct, explanation)
        """
        logger.info(f"LLMEvaluator comparing answers using model: {self.model_name}")
        logger.debug(f"Expected answer: {expected}")
        logger.debug(f"Actual answer: {actual}")

#         prompt = f"""
# You are an expert physics teacher evaluating student answers.
# Compare the following two answers and determine if they are equivalent:

# Expected answer (in LaTeX): {expected}
# Student answer (in LaTeX): {actual}

# Consider the following in your evaluation:
# 1. Mathematical equivalence (e.g., 2π = 6.28)
# 2. Physical unit equivalence (e.g., 1 m/s = 3.6 km/h)
# 3. Conceptual equivalence (e.g., F = ma and a = F/m)
# 4. Numerical tolerance: Allow a tolerance of {self.tolerance * 100}% for numerical values (e.g., if the expected value is 10, values between {10 - 10 * self.tolerance} and {10 + 10 * self.tolerance} are acceptable)

# Respond with a JSON object with the following structure:
# {{
#   "is_correct": true/false,
#   "explanation": "Your detailed explanation here"
# }}
# """
        from pydantic import BaseModel

        class AnswerResponse(BaseModel):
            is_correct: bool
            explanation: str

#         system_prompt = f"""
# You are an expert physics teacher evaluating student answers.
# Compare the following two answers and determine if they are equivalent:

# Expected answer (in LaTeX): {expected}
# Student answer (in LaTeX): {actual}

# Consider the following in your evaluation:
# 1. Mathematical equivalence (e.g., 2π = 6.28)
# 2. Physical unit equivalence (e.g., 1 m/s = 3.6 km/h)
# 3. Conceptual equivalence (e.g., F = ma and a = F/m)
# 4. Numerical tolerance: Allow a tolerance of {self.tolerance * 100}% for numerical values (e.g., if the expected value is 10, values between {10 - 10 * self.tolerance} and {10 + 10 * self.tolerance} are acceptable)

# Respond with a JSON object with the following structure:
# {{
#   "is_correct": true/false,
#   "explanation": "Your detailed explanation here"
# }}
# """

        system_prompt = f"""
You are an expert physics teacher evaluating student answers.
Compare the following two answers and determine if they are equivalent:

Consider the following in your evaluation:
1. Mathematical equivalence (e.g., 2π = 6.28)
2. Physical unit equivalence (e.g., 1 m/s = 3.6 km/h)
3. Conceptual equivalence (e.g., F = ma and a = F/m)
4. Numerical tolerance: Allow a tolerance of {self.tolerance * 100}% for numerical values (e.g., if the expected value is 10, values between {10 - 10 * self.tolerance} and {10 + 10 * self.tolerance} are acceptable)

Respond with is_correct(true/false) and explanation.
"""

        user_prompt = f"""
Expected answer (in LaTeX): {expected}
Student answer (in LaTeX): {actual}
        """

        try:
            logger.info(f"Sending request to OpenAI API with model: {self.model_name}")
            response = self.client.beta.chat.completions.parse(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=800,
                # response_format={"type": "json_object"}
                response_format=AnswerResponse
            )

            answer_response = response.choices[0].message.parsed
            # print("answer_response::", answer_response)
            is_correct = answer_response.is_correct
            explanation = answer_response.explanation
            
            # content = response.choices[0].message.content
            # result = json.loads(content)

            # is_correct = result["is_correct"]
            # explanation = result["explanation"]

            logger.info(f"LLM evaluation result: {is_correct}")
            logger.debug(f"LLM explanation: {explanation}")

            return is_correct, explanation
        except Exception as e:
            logger.error(f"Error in LLMEvaluator.compare_with_llm: {e}")
            raise
