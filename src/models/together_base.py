"""
Together AI API model implementation for generating responses to physics problems.
"""

import logging
import os
import re
import time
from dotenv import load_dotenv
from .api_base import APIBaseModel, format_api_response
from src.type import get_type_module

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class TogetherBaseModel(APIBaseModel):
    """
    Together AI API model implementation for generating responses to physics problems.
    """

    def __init__(self, model_name="togethercomputer/llama-2-70b-chat", parallel_size=4, max_tokens=2000):
        """
        Initialize the Together AI model.

        Args:
            model_name (str): The specific Together AI model to use
            parallel_size (int): Number of parallel API calls to make
            max_tokens (int): Maximum number of tokens in the response
        """
        super().__init__(parallel_size=parallel_size, max_tokens=max_tokens)
        self.api_key = os.environ.get("TOGETHER_API_KEY")
        if not self.api_key:
            raise ValueError("TOGETHER_API_KEY environment variable is not set")

        self.model_name = model_name
        logger.info(f"Initialized Together AI model: {model_name}, max_tokens: {max_tokens}")

    def _make_api_call(self, question_data, question_type):
        """
        Make the API call to Together AI using the client library.

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

            # Format the prompt for Together AI
            formatted_prompt = f"{system_message}\n\n{prompt}"

            # Import the Together client
            try:
                from together import Together
            except ImportError:
                logger.error("Together client library not installed. Please install it with 'pip install together'")
                raise ImportError("Together client library not installed. Please install it with 'pip install together'")

            # Initialize the Together client
            client = Together(api_key=self.api_key)

            logger.info(f"Sending request to Together AI with model: {self.model_name} for question: {short_question}")

            respond = ""
            try_count = 0
            max_tries = 1  # Set to 1 for now, can be increased if needed

            while respond == "" and try_count < max_tries:
                try_count += 1

                # Handle different models with specific configurations
                if "gemma" in self.model_name.lower():
                    # For Gemma models, we need to be careful about token limits
                    logger.info(f"Using Gemma-specific configuration for model: {self.model_name}")
                    response = client.chat.completions.create(
                        model=self.model_name,
                        messages=[{"role": "user", "content": formatted_prompt}],
                        max_tokens=min(6000, self.max_tokens)  # Ensure we don't exceed Gemma's limits
                    )
                else:
                    # For all other models
                    response = client.chat.completions.create(
                        model=self.model_name,
                        messages=[{"role": "user", "content": formatted_prompt}],
                        max_tokens=self.max_tokens,
                    )

                # Extract usage information
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }

                # Extract the content
                respond = response.choices[0].message.content
                logger.info(f"Received response with length: {len(respond)} characters")

                # Extract reasoning_content if available
                reasoning_content = None

                # Check for reasoning content in the response
                if "Qwen/Qwen3-235B-A22B-fp8-tput" in self.model_name:
                    # Try to extract reasoning content from Qwen3 model response
                    logger.info(f"Extracted reasoning content from <think> tags...")
                    try:
                        if "<think>" in respond and "</think>" in respond:
                            # Extract content between <think> and </think> tags
                            think_pattern = re.compile(r"<think>(.*?)</think>", re.DOTALL)
                            matches = think_pattern.findall(respond)

                            if matches:
                                # Combine all thinking sections if there are multiple
                                reasoning_content = "\n\n".join(match.strip() for match in matches)
                                logger.info(f"Extracted reasoning content from <think> tags: {len(reasoning_content)} characters")

                                # Remove the <think> sections from the main content
                                cleaned_content = think_pattern.sub("", respond).strip()

                                # If there's content left after removing thinking sections, update the respond variable
                                if cleaned_content:
                                    respond = cleaned_content
                                    logger.info(f"Updated main content after removing <think> sections: {len(respond)} characters")
                    except Exception as e:
                        logger.warning(f"Error extracting reasoning content: {e}")

                # If we got an empty response and have more tries, wait a bit before retrying
                if respond == "" and try_count < max_tries:
                    logger.warning(f"Received empty response, retrying ({try_count}/{max_tries})...")
                    time.sleep(2)  # Wait 2 seconds before retrying

            # Check if we still have an empty response after all retries
            if respond == "":
                logger.warning(f"Still received empty response after {max_tries} tries")

            # Create a response object with reasoning_content if available
            response_obj = {
                "content": respond,
                "usage": usage,
                "full_response": response
            }

            # Add reasoning_content if available
            if reasoning_content:
                response_obj["reasoning_content"] = reasoning_content

            # Use the standardized response format function
            result = format_api_response(respond, usage, response_obj)

            logger.info(f"Together AI API call successful for question: {short_question}")
            logger.info(f"Received {len(respond)} characters of content, {usage['total_tokens']} total tokens")

            return result

        except Exception as e:
            logger.error(f"Error in Together AI API call: {str(e)}")

            # Get a short version of the question for error logging
            if isinstance(question_data, dict):
                question_text = question_data.get('question', question_data.get('problem', ''))
            else:
                question_text = str(question_data)

            short_question = question_text[:50] + "..." if len(question_text) > 50 else question_text
            short_question = short_question.replace("\n", " ")

            # Log detailed error information
            error_msg = str(e)
            error_type = type(e).__name__

            logger.error(f"Error in Together AI API call for question: {short_question}")
            logger.error(f"Error type: {error_type}")
            logger.error(f"Error message: {error_msg}")

            # Add traceback information
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")

            # Use the standardized response format function with error
            error_response = {
                "error": error_msg,
                "error_type": error_type,
                "question": short_question
            }
            return format_api_response(f"Error: {error_msg}", {}, error_response, error=error_msg)

# Specific model implementations
class LlamaModel(TogetherBaseModel):
    """Llama 2 70B model implementation."""
    def __init__(self, parallel_size=4, max_tokens=2000):
        super().__init__(model_name="togethercomputer/llama-2-70b-chat", parallel_size=parallel_size, max_tokens=max_tokens)

class MistralModel(TogetherBaseModel):
    """Mistral 7B model implementation."""
    def __init__(self, parallel_size=4, max_tokens=2000):
        super().__init__(model_name="mistralai/Mistral-7B-Instruct-v0.2", parallel_size=parallel_size, max_tokens=max_tokens)

class ClaudeModel(TogetherBaseModel):
    """Claude model implementation."""
    def __init__(self, parallel_size=4, max_tokens=2000):
        super().__init__(model_name="anthropic/claude-2.0", parallel_size=parallel_size, max_tokens=max_tokens)

class DeepSeekR1DistillLlama70BModel(TogetherBaseModel):
    """DeepSeek R1 Distill Llama 70B model implementation."""
    def __init__(self, parallel_size=4, max_tokens=2000):
        super().__init__(model_name="deepseek-ai/DeepSeek-R1-Distill-Llama-70B", parallel_size=parallel_size, max_tokens=max_tokens)

class QwQ32BPreviewModel(TogetherBaseModel):
    """QwQ 32B Preview model implementation."""
    def __init__(self, parallel_size=4, max_tokens=2000):
        super().__init__(model_name="Qwen/QwQ-32B-Preview", parallel_size=parallel_size, max_tokens=max_tokens)

class Qwen2572BInstructTurboModel(TogetherBaseModel):
    """Qwen 2.5 72B Instruct Turbo model implementation."""
    def __init__(self, parallel_size=4, max_tokens=2000):
        super().__init__(model_name="Qwen/Qwen2.5-72B-Instruct-Turbo", parallel_size=parallel_size, max_tokens=max_tokens)

class Llama31405BInstructTurboModel(TogetherBaseModel):
    """Llama 3.1 405B Instruct Turbo model implementation."""
    def __init__(self, parallel_size=4, max_tokens=2000):
        super().__init__(model_name="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo", parallel_size=parallel_size, max_tokens=max_tokens)

class Qwen3235BA22BFp8TputModel(TogetherBaseModel):
    """Qwen 3 235B A22B FP8 Throughput model implementation."""
    def __init__(self, parallel_size=4, max_tokens=2000):
        super().__init__(model_name="Qwen/Qwen3-235B-A22B-fp8-tput", parallel_size=parallel_size, max_tokens=max_tokens)

class Llama3370BInstructModel_Togehter(TogetherBaseModel):
    def __init__(self, parallel_size=4, max_tokens=2000):
        super().__init__(model_name="meta-llama/Llama-3.3-70B-Instruct-Turbo", parallel_size=parallel_size, max_tokens=max_tokens)

class Qwen257BInstructModel_Togehter(TogetherBaseModel):
    def __init__(self, parallel_size=4, max_tokens=2000):
        super().__init__(model_name="Qwen/Qwen2.5-7B-Instruct-Turbo", parallel_size=parallel_size, max_tokens=max_tokens)



