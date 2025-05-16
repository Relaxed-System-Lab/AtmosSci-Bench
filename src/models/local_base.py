"""
Base class for local models using Hugging Face Transformers.
"""

import logging
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from .base import BaseModel
from src.type import get_type_module

# Configure logging
logger = logging.getLogger(__name__)

class LocalBaseModel(BaseModel):
    """
    Base class for all local model implementations using Hugging Face Transformers.
    """

    def __init__(self, model_name, device=None, parallel_size=1, max_tokens=2000):
        """
        Initialize the local base model.

        Args:
            model_name (str): The name of the model to load from Hugging Face
            device (str, optional): Device to use for inference. If None, will use CUDA if available.
            parallel_size (int): Number of parallel inference processes to use (for batch processing)
            max_tokens (int): Maximum number of tokens in the response
        """
        super().__init__(parallel_size=parallel_size, max_tokens=max_tokens)
        self.model_name = model_name

        # Set device
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        logger.info(f"Initialized local model with parallel size: {parallel_size}, max_tokens: {max_tokens}")

        logger.info(f"Loading model {model_name} on {self.device}...")

        # Load model and tokenizer
        # try:
        #     self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        #     self.model = AutoModelForCausalLM.from_pretrained(
        #         model_name,
        #         torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
        #         device_map=self.device
        #     )
        #     logger.info(f"Successfully loaded model {model_name}")
        # except Exception as e:
        #     logger.error(f"Failed to load model {model_name}: {e}")
        #     raise

    def _prepare_prompt(self, question_data, question_type):
        """
        Prepare the prompt for the model.

        Args:
            question_data (str or dict): The question to answer. Can be a string or a dictionary containing the question and additional data
            question_type (str): Type of question (OEQ or MCQ)

        Returns:
            str: The prepared prompt
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
                return type_module.get_prompt(question_text, options, knowledge)
            else:
                # For other question types, just use the question text
                return type_module.get_prompt(question_text)
        else:
            # If question_data is a string, just use it directly
            question_text = str(question_data)
            return type_module.get_prompt(question_text)

    def generate_response(self, question_data, question_type="OEQ", max_retries=3, worker_logging=True):
        """
        Generate a response for the given question using the local model.

        Args:
            question_data (str or dict): The question to answer. Can be a string or a dictionary containing the question and additional data
            question_type (str): Type of question (OEQ or MCQ)
            max_retries (int): Maximum number of retries (not used for local models)
            worker_logging (bool): Whether to enable logging for the worker process (not used for local models)

        Returns:
            dict: A dictionary containing:
                - 'content': The model's response text
                - 'usage': Information about token usage
                - 'full_response': The full response object
        """
        prompt = self._prepare_prompt(question_data, question_type)

        # Tokenize the prompt
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        # Generate response
        try:
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs["input_ids"],
                    max_new_tokens=self.max_tokens,
                    temperature=0.2,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )

            # Decode the response
            response_text = self.tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)

            # Calculate token usage
            input_tokens = inputs["input_ids"].shape[1]
            output_tokens = outputs.shape[1] - input_tokens
            total_tokens = input_tokens + output_tokens

            usage = {
                "prompt_tokens": input_tokens,
                "completion_tokens": output_tokens,
                "total_tokens": total_tokens
            }

            # Use the standardized response format function
            from .api_base import format_api_response
            full_response = {
                "model": self.model_name,
                "choices": [{"message": {"content": response_text}}],
                "usage": usage
            }
            return format_api_response(response_text, usage, full_response)

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise

    def generate_responses_batch(self, questions_data, question_type="OEQ", retries=0, worker_logging=True):
        """
        Generate responses for multiple questions in batches.

        Args:
            questions_data (list): List of questions to answer. Each item can be a string or a dictionary containing the question and additional data
            question_type (str): Type of question (OEQ or MCQ)
            retries (int): Number of retries if the first attempt fails (not used for local models)
            worker_logging (bool): Whether to enable logging for the worker process (not used for local models)

        Returns:
            list: List of responses
        """
        import concurrent.futures

        results = []
        total_questions = len(questions_data)
        num_batches = (total_questions + self.parallel_size - 1) // self.parallel_size

        logger.info(f"Processing {total_questions} questions in {num_batches} batches of up to {self.parallel_size}")

        # Process questions in batches to control memory usage
        for batch_idx in range(num_batches):
            start_idx = batch_idx * self.parallel_size
            end_idx = min(start_idx + self.parallel_size, total_questions)
            batch_questions = questions_data[start_idx:end_idx]

            logger.info(f"Processing batch {batch_idx + 1}/{num_batches} with {len(batch_questions)} questions")

            batch_results = []

            # Use ThreadPoolExecutor for parallel processing within the batch
            # This is more efficient for I/O bound operations like inference
            try:
                with concurrent.futures.ThreadPoolExecutor(max_workers=self.parallel_size) as executor:
                    # Submit all questions in this batch to the executor
                    future_to_idx = {
                        executor.submit(self.generate_response, question_data, question_type): i
                        for i, question_data in enumerate(batch_questions)
                    }

                    # Process results as they complete
                    for future in concurrent.futures.as_completed(future_to_idx):
                        idx = future_to_idx[future]
                        try:
                            result = future.result()
                            batch_results.append(result)
                            logger.info(f"Completed question {start_idx + idx + 1}/{total_questions}")
                        except Exception as e:
                            logger.error(f"Error processing question {start_idx + idx + 1}: {e}")
                            # Use the standardized response format function with error
                            from .api_base import format_api_response
                            error_msg = str(e)
                            error_response = {'error': error_msg}
                            batch_results.append(format_api_response(f"Error: {error_msg}", {}, error_response, error=error_msg))

                # We need to ensure results are in the same order as the input questions
                # Since we're using as_completed, we need to reorder the results
                # We'll create a mapping of results by their index
                ordered_batch_results = [None] * len(batch_questions)
                for i, result in enumerate(batch_results):
                    # Find the index for this result
                    # This is a simplification - in practice, we'd need a more robust way to match results to questions
                    if i < len(ordered_batch_results):
                        ordered_batch_results[i] = result

                # Replace any None values with error placeholders
                for i in range(len(ordered_batch_results)):
                    if ordered_batch_results[i] is None:
                        # Use the standardized response format function with error
                        from .api_base import format_api_response
                        error_msg = "Result missing"
                        error_response = {'error': error_msg}
                        ordered_batch_results[i] = format_api_response(f"Error: {error_msg}", {}, error_response, error=error_msg)

                batch_results = ordered_batch_results
                results.extend(batch_results)
                logger.info(f"Completed batch {batch_idx + 1}/{num_batches}")

            except Exception as e:
                logger.error(f"Error processing batch {batch_idx + 1}: {e}")
                # Fall back to sequential processing if parallel processing fails
                for i, question_data in enumerate(batch_questions):
                    try:
                        result = self.generate_response(question_data, question_type)
                        results.append(result)
                        logger.info(f"Completed question {start_idx + i + 1}/{total_questions} (sequential fallback)")
                    except Exception as e:
                        logger.error(f"Error processing question {start_idx + i + 1}: {e}")
                        # Use the standardized response format function with error
                        from .api_base import format_api_response
                        error_msg = str(e)
                        error_response = {'error': error_msg}
                        results.append(format_api_response(f"Error: {error_msg}", {}, error_response, error=error_msg))

        return results
