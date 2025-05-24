"""
MCQ evaluator for evaluating multiple-choice question responses.
"""

import re
import logging
from .base_evaluator import BaseEvaluator

logger = logging.getLogger(__name__)

class MCQEvaluator(BaseEvaluator):
    """
    Evaluator for multiple-choice questions.
    Extracts answers from model responses and compares them to expected answers.
    """

    def __init__(self, tolerance=0.05):
        """
        Initialize the MCQ evaluator.

        Args:
            tolerance (float): Not used for MCQ evaluation, but kept for consistency
        """
        super().__init__(tolerance)

    def extract_mcq_answer(self, response):
        """
        Extract the MCQ answer (A, B, C, or D) from the response.

        Args:
            response (str): The model's response

        Returns:
            str or None: The extracted answer (A, B, C, or D) or None if no answer found
        """
        # Debug logging
        logger.debug(f"Extracting MCQ answer from response of type: {type(response)}")

        if not response:
            logger.debug("Response is empty or None")
            return None

        # Ensure response is a string
        if not isinstance(response, str):
            try:
                response = str(response)
                logger.debug(f"Converted response to string: {response[:100]}...")
            except Exception as e:
                logger.error(f"Failed to convert response to string: {e}")
                return None

        # Regex patterns to extract MCQ answers
        patterns = [
            r"[A,a][N,n][S,s][W,w][E,e][R,r]:?\s*[\*\[\{]*:?\s*([A-Da-d])[\*\[\}]*",  # Matches 'Answer: A', 'Answer: *A*'
            r"\\boxed\{([A-Da-d])\}",  # Matches '\boxed{C}'
            r"\\boxed\{\{([A-Da-d])\}\}",# \\boxed{{A}}
            r"(\\)?boxed\{\{?\s*([A-Da-d])\s*\}?\}",
            r"[O,o][P,p][T,t][I,i][O,o][N,n][S,s]?:?\s*[\*\[\{]*:?\s*([A-Da-d])[\*\[\}]*",  # Matches 'Option: B'
            r"\*\*[F,f]inal\s*[A,a]nswer\*\*:?\s*\\\[\s*\\boxed\{([A-Da-d])\}\s*\\\]",  # Matches '**Final Answer**: \[ \boxed{A} \]'
            r"\*\*Final Answer\*\*:\s*\[\s*(?:\\?boxed\{)?\s*([A-Da-d])\s*\}?\s*\]"
        ]

        for i, pattern in enumerate(patterns):
            try:
                matches = list(re.finditer(pattern, response))
                if matches:
                    last_match = matches[-1]
                    answer = last_match.group(1).strip()
                    logger.debug(f"Found match with pattern {i+1}: {answer}")
                    return answer.upper()
            except Exception as e:
                logger.error(f"Error matching pattern {i+1}: {e}")
                continue

        logger.debug("No MCQ answer found in response")
        return None

    def evaluate(self, expected, actual):
        """
        Evaluate if the actual MCQ answer matches the expected answer.

        Args:
            expected (str): The expected answer (A, B, C, or D)
            actual (str): The actual answer from the model

        Returns:
            dict: A dictionary containing:
                - 'is_correct' (bool): Whether the answer is correct
                - 'details' (dict): Additional details about the evaluation
        """
        # Handle None values
        if actual is None:
            extracted_answer = None
        # Extract the MCQ answer if it's a string with length > 1
        elif isinstance(actual, str) and len(actual) > 1:
            extracted_answer = self.extract_mcq_answer(actual)
        # If it's a single character, just use it
        elif isinstance(actual, str):
            extracted_answer = actual.upper()
        else:
            # If it's not a string, convert to string first
            try:
                extracted_answer = str(actual).upper()
            except:
                extracted_answer = None

        # Handle None values for expected
        if expected is None:
            expected_answer = None
        # Normalize expected answer if it's a string
        elif isinstance(expected, str):
            expected_answer = expected.strip().upper()

            # If expected answer is longer than one character, try to extract it
            if len(expected_answer) > 1:
                expected_match = self.extract_mcq_answer(expected_answer)
                if expected_match:
                    expected_answer = expected_match
                else:
                    # If we can't extract a clear MCQ answer, look for the first A, B, C, or D
                    for char in expected_answer:
                        if char in "ABCD":
                            expected_answer = char
                            break
        else:
            # If it's not a string, convert to string first
            try:
                expected_answer = str(expected).strip().upper()
            except:
                expected_answer = None

        # Check if the answers match
        is_correct = (extracted_answer == expected_answer) if extracted_answer and expected_answer else False

        details = {
            "evaluator": "MCQEvaluator",
            "expected": expected_answer,
            "extracted": extracted_answer,
            "match": is_correct,
            "error": None  # Add error field to match other evaluators
        }

        logger.debug(f"MCQ evaluation: expected={expected_answer}, extracted={extracted_answer}, is_correct={is_correct}")

        return {
            "is_correct": is_correct,
            "details": details
        }
