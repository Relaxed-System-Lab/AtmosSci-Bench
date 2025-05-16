"""
DeepSeek API model implementation for generating responses to physics problems.
"""

import logging
import os
import json
import requests
from openai import OpenAI
from dotenv import load_dotenv
from .api_base import APIBaseModel
from src.type import get_type_module

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class DeepSeekBaseModel(APIBaseModel):
    """
    DeepSeek API model implementation for generating responses to physics problems.
    """

    def __init__(self, model_name="deepseek-chat", parallel_size=4, max_tokens=2000):
        """
        Initialize the DeepSeek model.

        Args:
            model_name (str): The specific DeepSeek model to use
            parallel_size (int): Number of parallel API calls to make
            max_tokens (int): Maximum number of tokens in the response
        """
        super().__init__(parallel_size=parallel_size, max_tokens=max_tokens)
        load_dotenv()
        self.api_key = os.environ.get("DeepSeek_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable is not set")

        self.model_name = model_name
        self.max_tokens = max_tokens
        # self.api_url = "https://api.deepseek.com/v1/chat/completions"
        logger.info(f"Initialized DeepSeek model: {model_name}, max_tokens: {max_tokens}")

    def _make_api_call(self, question_data, question_type):
        """
        Make the API call to DeepSeek using the OpenAI client library.

        Args:
            question_data (str or dict): The question to answer. Can be a string or a dictionary containing the question and additional data
            question_type (str): Type of question (OEQ or MCQ)

        Returns:
            dict: The model's response
        """
        # Get the appropriate question type module
        type_module = get_type_module(question_type)

        # Extract question text and additional data if available
        if isinstance(question_data, dict):
            question_text = question_data.get('question', question_data.get('problem', ''))

            # For MCQ questions, extract options and knowledge if available
            if question_type == "MCQ":
                options = question_data.get('options', None)
                knowledge = question_data.get('knowledge', None)
                # Get the prompt with options and knowledge
                prompt = type_module.get_prompt(question_text, options, knowledge)
            else:
                # For other question types, just use the question text
                prompt = type_module.get_prompt(question_text)
        else:
            # If question_data is a string, just use it directly
            question_text = str(question_data)
            prompt = type_module.get_prompt(question_text)

        # Get the system message from the question type module
        system_message = type_module.SYSTEM_MESSAGE

        # Initialize the OpenAI client with DeepSeek base URL
        client = OpenAI(
            api_key=os.environ.get("DeepSeek_API_KEY"),
            base_url="https://api.deepseek.com"
        )

        try:
            # Make the API call
            chat_completion = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                stream=False,
                max_tokens=self.max_tokens,
            )

            # Extract the content
            content = chat_completion.choices[0].message.content

            # Convert the response object to a dictionary for serialization
            response_dict = chat_completion.model_dump()

            # Extract usage information
            usage = response_dict.get("usage", {})

            # For DeepSeek R1 model, extract reasoning_content if it exists
            reasoning_content = None
            if self.model_name == "deepseek-reasoner" and hasattr(chat_completion.choices[0].message, "reasoning_content"):
                reasoning_content = chat_completion.choices[0].message.reasoning_content
                logger.info(f"Found reasoning_content in DeepSeek R1 response: {len(reasoning_content) if reasoning_content else 0} characters")

            # Use the standardized response format function
            from .api_base import format_api_response
            return format_api_response(content, usage, response_dict)
        except Exception as e:
            logger.error(f"Error in DeepSeek {self.model_name} API call: {str(e)}")
            raise

# Specific model implementations
class DeepSeekR1Model(DeepSeekBaseModel):
    """DeepSeek R1 model implementation."""
    def __init__(self, parallel_size=4, max_tokens=2000):
        super().__init__(model_name="deepseek-reasoner", parallel_size=parallel_size, max_tokens=max_tokens)

class DeepSeekV3Model(DeepSeekBaseModel):
    """DeepSeek V3 model implementation using the OpenAI client library."""
    def __init__(self, parallel_size=4, max_tokens=2000):
        super().__init__(model_name="deepseek-chat", parallel_size=parallel_size, max_tokens=max_tokens)