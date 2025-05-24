"""
Google API model implementation for generating responses to physics problems.
"""

import logging
import os
import requests
from dotenv import load_dotenv
from .api_base import APIBaseModel, format_api_response
from src.type import get_type_module

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class GoogleBaseModel(APIBaseModel):
    """
    Google API model implementation for generating responses to physics problems.
    """

    def __init__(self, model_name="gemini-2.0-flash-thinking-exp-01-21", parallel_size=4, max_tokens=2000):
        """
        Initialize the Google model.

        Args:
            model_name (str): The specific Google model to use
            parallel_size (int): Number of parallel API calls to make
            max_tokens (int): Maximum number of tokens in the response
        """
        super().__init__(parallel_size=parallel_size, max_tokens=max_tokens)
        self.api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY environment variable is not set")

        self.model_name = model_name
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
        self.use_client_library = "gemini-2.0-flash-thinking-exp" in model_name or "gemini-2.0-flash-exp" in model_name
        logger.info(f"Initialized Google model: {model_name}, max_tokens: {max_tokens}, use_client_library: {self.use_client_library}")

    def _make_api_call(self, question_data, question_type):
        """
        Make the API call to Google.

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

            # Combine system message and prompt
            full_prompt = f"{system_message}\n\n{prompt}"

            logger.info(f"Sending request to Google API with model: {self.model_name} for question: {short_question}")

            # Use the appropriate API method based on the model
            if self.use_client_library:
                # Use the Gemini client library for flash models
                if "gemini-2.0-flash-thinking-exp-01-21" in self.model_name:
                    # Use the google.generativeai package for the flash-thinking-exp-01-21 model
                    import google.generativeai as genai
                    genai.configure(api_key=self.api_key)
                    model = genai.GenerativeModel(
                        model_name=self.model_name,
                        generation_config={
                            "temperature": 0.2,
                            "top_p": 0.95,
                            "top_k": 40,
                            "max_output_tokens": self.max_tokens,
                            "response_mime_type": "text/plain",
                        }
                    )
                    response = model.generate_content(full_prompt)

                    # Extract content and thought
                    content = response.text
                    thought = ""

                    # Extract usage information
                    usage_metadata = response.usage_metadata
                    standardized_usage = {
                        "prompt_tokens": getattr(usage_metadata, "prompt_token_count", 0),
                        "completion_tokens": getattr(usage_metadata, "candidates_token_count", 0),
                        "total_tokens": getattr(usage_metadata, "total_token_count", 0)
                    }
                elif "gemini-2.0-flash-exp" in self.model_name:
                    # Use the google.genai package for flash-exp models
                    from google import genai
                    from google.genai import types
                    client = genai.Client(api_key=self.api_key, http_options={'api_version':'v1alpha'})
                    response = client.models.generate_content(
                        model=self.model_name,
                        contents=full_prompt,
                        config=types.GenerateContentConfig(
                            temperature=0.2,
                            top_p=0.95,
                            top_k=40,
                            max_output_tokens=self.max_tokens,
                        )
                    )

                    # Extract content and thought
                    content = ""
                    thought = ""
                    if response.candidates:
                        # For flash-exp models, the response structure is different
                        if hasattr(response.candidates[0].content, 'parts'):
                            for part in response.candidates[0].content.parts:
                                if hasattr(part, 'text'):
                                    content = part.text

                        # Check for thinking/reasoning content
                        if hasattr(response, 'thinking') and response.thinking:
                            thought = response.thinking
                        elif hasattr(response, 'reasoning') and response.reasoning:
                            thought = response.reasoning
                        elif hasattr(response.candidates[0], 'thinking') and response.candidates[0].thinking:
                            thought = response.candidates[0].thinking
                        elif hasattr(response.candidates[0], 'reasoning') and response.candidates[0].reasoning:
                            thought = response.candidates[0].reasoning
                        elif hasattr(response.candidates[0].content, 'thinking') and response.candidates[0].content.thinking:
                            thought = response.candidates[0].content.thinking
                        elif hasattr(response.candidates[0].content, 'reasoning') and response.candidates[0].content.reasoning:
                            thought = response.candidates[0].content.reasoning

                    # Extract usage information
                    standardized_usage = {
                        "prompt_tokens": getattr(response.usage_metadata, "prompt_token_count", 0),
                        "completion_tokens": getattr(response.usage_metadata, "candidates_token_count", 0),
                        "total_tokens": getattr(response.usage_metadata, "total_token_count", 0)
                    }
                else:
                    # Use the google.genai package for other models
                    from google import genai
                    from google.genai import types
                    client = genai.Client(api_key=self.api_key, http_options={'api_version':'v1alpha'})
                    response = client.models.generate_content(
                        model=self.model_name,
                        contents=full_prompt,
                        config=types.GenerateContentConfig(
                            temperature=0.2,
                            top_p=0.95,
                            top_k=40,
                            max_output_tokens=self.max_tokens,
                        )
                    )

                    # Extract content and thought
                    content = ""
                    thought = ""
                    if response.candidates:
                        for part in response.candidates[0].content.parts:
                            if getattr(part, "thought", False):
                                thought = part.text
                            else:
                                content = part.text

                    # Extract usage information
                    standardized_usage = {
                        "prompt_tokens": getattr(response.usage_metadata, "prompt_token_count", 0),
                        "completion_tokens": getattr(response.usage_metadata, "candidates_token_count", 0),
                        "total_tokens": getattr(response.usage_metadata, "total_token_count", 0)
                    }

                # Create a response object that includes both content and thought
                response_obj = {
                    "content": content,
                    "thought": thought,
                    "usage_metadata": standardized_usage,
                    "original_response": response
                }

                # If there's a thought, add it to the response
                if thought:
                    logger.info(f"Thought content: {len(thought)} characters")
                    response_obj["reasoning_content"] = thought

                # Use the standardized response format function
                result = format_api_response(content, standardized_usage, response_obj)

                # Add reasoning_content if there's a thought
                if thought:
                    result["reasoning_content"] = thought
            else:
                # Use the REST API for other models
                headers = {
                    "Content-Type": "application/json",
                    "x-goog-api-key": self.api_key
                }

                data = {
                    "contents": [
                        {
                            "role": "user",
                            "parts": [
                                {
                                    "text": full_prompt
                                }
                            ]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.2,
                        "maxOutputTokens": self.max_tokens,
                        "topP": 0.95,
                        "topK": 40
                    }
                }

                # Make the API call
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=data
                )
                response.raise_for_status()
                response_json = response.json()

                # Extract the content
                content = response_json.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")

                # Extract usage information if available
                usage = response_json.get("usageMetadata", {})

                # Convert usage to a standardized format
                standardized_usage = {
                    "prompt_tokens": usage.get("promptTokenCount", 0),
                    "completion_tokens": usage.get("candidatesTokenCount", 0),
                    "total_tokens": usage.get("totalTokenCount", 0)
                }

                # Use the standardized response format function
                result = format_api_response(content, standardized_usage, response_json)

            logger.info(f"Google API call successful for question: {short_question}")
            logger.info(f"Received {len(content)} characters of content, {standardized_usage['total_tokens']} total tokens")

            return result

        except Exception as e:
            logger.error(f"Error in Google API call: {str(e)}")

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

            logger.error(f"Error in Google API call for question: {short_question}")
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
class GeminiModel(GoogleBaseModel):
    """Gemini 2.0 Flash Thinking Exp model implementation."""
    def __init__(self, parallel_size=4, max_tokens=2000):
        super().__init__(model_name="gemini-2.0-flash-thinking-exp-01-21", parallel_size=parallel_size, max_tokens=max_tokens)

class GeminiFlashExpModel(GoogleBaseModel):
    """Gemini 2.0 Flash Exp model implementation."""
    def __init__(self, parallel_size=4, max_tokens=2000):
        super().__init__(model_name="gemini-2.0-flash-exp", parallel_size=parallel_size, max_tokens=max_tokens)
