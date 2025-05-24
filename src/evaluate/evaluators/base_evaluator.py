"""
Base evaluator class for evaluating model responses.
"""

import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseEvaluator(ABC):
    """
    Base class for all evaluators.
    """
    
    def __init__(self, tolerance=0.05):
        """
        Initialize the evaluator.
        
        Args:
            tolerance (float): Tolerance for numerical comparisons
        """
        self.tolerance = tolerance
        
    @abstractmethod
    def evaluate(self, expected, actual):
        """
        Evaluate if the actual answer matches the expected answer.
        
        Args:
            expected (str): The expected answer
            actual (str): The actual answer from the model
            
        Returns:
            dict: A dictionary containing:
                - 'is_correct' (bool): Whether the answer is correct
                - 'details' (dict): Additional details about the evaluation
        """
        pass
    
    def __str__(self):
        """Return the name of the evaluator."""
        return self.__class__.__name__
