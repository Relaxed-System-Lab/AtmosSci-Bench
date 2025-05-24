"""
Base model class for generating responses to physics problems.
"""

import abc
import logging

# Configure logging
logger = logging.getLogger(__name__)

class BaseModel(abc.ABC):
    """
    Base class for all model implementations.
    """

    def __init__(self, parallel_size=4, max_tokens=2000):
        """
        Initialize the base model.

        Args:
            parallel_size (int): Number of parallel processes to use
            max_tokens (int): Maximum number of tokens in the response
        """
        self.parallel_size = parallel_size
        self.max_tokens = max_tokens
        logger.info(f"Initialized model with parallel size: {parallel_size}, max_tokens: {max_tokens}")

    @abc.abstractmethod
    def generate_response(self, question, question_type="OEQ", max_retries=3):
        """
        Generate a response for the given question.

        Args:
            question (str): The question to answer
            question_type (str): Type of question (OEQ or MCQ)
            max_retries (int): Maximum number of retries

        Returns:
            dict: A dictionary containing:
                - 'content': The model's response text
                - 'usage': Information about token usage
                - 'full_response': The full response object
        """
        pass

    @abc.abstractmethod
    def generate_responses_batch(self, questions, question_type="OEQ", max_retries=3):
        """
        Generate responses for multiple questions in parallel.

        Args:
            questions (list): List of questions to answer
            question_type (str): Type of question (OEQ or MCQ)
            max_retries (int): Maximum number of retries

        Returns:
            list: List of response dictionaries
        """
        pass
