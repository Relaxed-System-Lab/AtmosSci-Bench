"""
OpenAI API model implementation for generating responses to physics problems.
"""

import logging
import os
from openai import OpenAI
from dotenv import load_dotenv
from .api_base import APIBaseModel
from src.type import get_type_module

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class OpenAIBaseModel(APIBaseModel):
    """
    OpenAI API model implementation for generating responses to physics problems.
    """

    def __init__(self, model_name="gpt-4o", parallel_size=4, max_tokens=2000, use_max_completion_tokens=False):
        """
        Initialize the OpenAI model.

        Args:
            model_name (str): The specific OpenAI model to use
            parallel_size (int): Number of parallel API calls to make
            max_tokens (int): Maximum number of tokens in the response
            use_max_completion_tokens (bool): Whether to use max_completion_tokens instead of max_tokens
        """
        super().__init__(parallel_size=parallel_size, max_tokens=max_tokens)
        self.client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
        self.model_name = model_name
        self.use_max_completion_tokens = use_max_completion_tokens

        token_param = "max_completion_tokens" if use_max_completion_tokens else "max_tokens"
        logger.info(f"Initialized OpenAI model: {model_name}, {token_param}: {max_tokens}")

    def _make_api_call(self, question_data, question_type):
        """
        Make the API call to OpenAI.

        Args:
            question_data (str or dict): The question to answer. Can be a string or a dictionary containing the question and additional data
            question_type (str): Type of question (OEQ or MCQ)

        Returns:
            dict: The model's response
        """
        try:
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

            # Get a short version of the question for logging
            short_question = question_text[:50] + "..." if len(question_text) > 50 else question_text
            short_question = short_question.replace("\n", " ")

            # Get the system message from the question type module
            system_message = type_module.SYSTEM_MESSAGE

            # Determine which token parameter to use
            token_param = "max_completion_tokens" if self.use_max_completion_tokens else "max_tokens"

            logger.info(f"Sending request to OpenAI API with model: {self.model_name} for question: {short_question}")

            # Log the API request details
            logger.debug(f"System message: {system_message[:100]}...")
            logger.debug(f"Prompt length: {len(prompt)} characters")
            logger.debug(f"{token_param}: {self.max_tokens}")

            # Create API parameters
            api_params = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
            }

            # Add the appropriate token parameter
            api_params[token_param] = self.max_tokens

            # Make the API call
            response = self.client.chat.completions.create(**api_params)

            # Extract the content and usage information
            content = response.choices[0].message.content

            # Create basic usage dictionary
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }

            # Check if completion_tokens_details exists and contains reasoning_tokens (for o3-mini model)
            try:
                if hasattr(response.usage, 'completion_tokens_details'):
                    completion_tokens_details = response.usage.completion_tokens_details
                    if hasattr(completion_tokens_details, 'reasoning_tokens'):
                        reasoning_tokens = completion_tokens_details.reasoning_tokens
                        if reasoning_tokens is not None:
                            usage["reasoning_tokens"] = reasoning_tokens
                            logger.info(f"Found reasoning tokens: {usage['reasoning_tokens']}")
            except Exception as e:
                # If anything goes wrong, just log it and continue without reasoning tokens
                logger.warning(f"Error extracting reasoning tokens: {e}")

            # Use the standardized response format function
            from .api_base import format_api_response
            result = format_api_response(content, usage, response)

            logger.info(f"OpenAI API call successful for question: {short_question}")

            # Log token usage information
            token_info = f"Received {len(content)} characters of content, {usage['total_tokens']} total tokens"
            if 'reasoning_tokens' in usage:
                token_info += f", {usage['reasoning_tokens']} reasoning tokens"
            if 'reasoning_content' in result:
                token_info += f", reasoning_content: {len(result['reasoning_content'])} characters"
            logger.info(token_info)
            return result

        except Exception as e:
            # Get a short version of the question for logging
            if isinstance(question_data, dict):
                question_text = question_data.get('question', question_data.get('problem', ''))
            else:
                question_text = str(question_data)

            short_question = question_text[:50] + "..." if len(question_text) > 50 else question_text
            short_question = short_question.replace("\n", " ")

            # Log detailed error information
            error_msg = str(e)
            error_type = type(e).__name__

            logger.error(f"Error in OpenAI API call for question: {short_question}")
            logger.error(f"Error type: {error_type}")
            logger.error(f"Error message: {error_msg}")

            # Add traceback information
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")

            # Use the standardized response format function with error
            from .api_base import format_api_response
            error_response = {
                "error": error_msg,
                "error_type": error_type,
                "question": short_question
            }
            return format_api_response(f"Error: {error_msg}", {}, error_response, error=error_msg)

# Specific model implementations
class GPT4oModel(OpenAIBaseModel):
    """GPT-4o model implementation."""
    def __init__(self, parallel_size=4, max_tokens=2000):
        super().__init__(model_name="gpt-4o", parallel_size=parallel_size, max_tokens=max_tokens)

class GPT4oMiniModel(OpenAIBaseModel):
    """GPT-4o-mini model implementation."""
    def __init__(self, parallel_size=4, max_tokens=2000):
        super().__init__(model_name="gpt-4o-mini", parallel_size=parallel_size, max_tokens=max_tokens)

class GPT35TurboModel(OpenAIBaseModel):
    """GPT-3.5 Turbo model implementation."""
    def __init__(self, parallel_size=4, max_tokens=2000):
        super().__init__(model_name="gpt-3.5-turbo", parallel_size=parallel_size, max_tokens=max_tokens)

class O1Model(OpenAIBaseModel):
    """GPT-o1 model implementation."""
    def __init__(self, parallel_size=4, max_tokens=30000):
        super().__init__(model_name="o1", parallel_size=parallel_size, max_tokens=max_tokens, 
                         use_max_completion_tokens=True  # Use max_completion_tokens instead of max_tokens
                         )

class O3MiniModel(OpenAIBaseModel):
    """o3-mini model implementation.

    Special features:
    - Uses max_completion_tokens instead of max_tokens
    - Captures reasoning_tokens from completion_tokens_details when available
    """
    def __init__(self, parallel_size=4, max_tokens=30000):
        super().__init__(
            model_name="o3-mini",
            parallel_size=parallel_size,
            max_tokens=max_tokens,
            use_max_completion_tokens=True  # Use max_completion_tokens instead of max_tokens
        )
