"""
Hugging Face Transformers model implementation for generating responses to physics problems.
"""

import logging
import os
import time
import torch
from transformers import AutoModel, AutoModelForCausalLM, AutoTokenizer, GenerationConfig
from accelerate import Accelerator
from .local_base import LocalBaseModel
from src.type import get_type_module

# Configure logging
logger = logging.getLogger(__name__)

class HuggingFaceBaseModel(LocalBaseModel):
    """
    Hugging Face Transformers model implementation for generating responses to physics problems.
    """

    def __init__(self, model_name, device=None, parallel_size=1, max_tokens=2000, gpu="0", truncation=True):
        """
        Initialize the Hugging Face model.

        Args:
            model_name (str): The specific Hugging Face model to use
            device (str, optional): Device to use for inference. If None, will use CUDA if available.
            parallel_size (int): Number of parallel inference processes to use
            max_tokens (int): Maximum number of tokens in the response
            gpu (str): GPU device IDs to use (e.g., "0" or "0,1,2,3")
        """
        super().__init__(model_name, device, parallel_size, max_tokens)
        self.gpu = gpu
        self.truncation = truncation
        logger.info(f"Initialized Hugging Face model: {model_name} on GPU: {gpu}")

        # Initialize model with accelerator
        self._init_model_with_accelerator()

    def _init_model_with_accelerator(self):
        """Initialize the model using Accelerator for better performance."""
        # Set visible GPUs
        logger.info(f"CUDA_VISIBLE_DEVICES set: {self.gpu}.")
        
        os.environ["CUDA_VISIBLE_DEVICES"] = self.gpu

        # Initialize accelerator
        self.accelerator = Accelerator()

        # Determine model class based on model name
        if self.model_name in ["Qwen/Qwen2.5-Math-PRM-7B"]:
            model_class = AutoModel
        else:
            model_class = AutoModelForCausalLM



        if self.model_name == "GeoGPT-Research-Project/Qwen2.5-72B-GeoGPT":
            # hard code
            model_path = "/GLOBALFS/yt_ust_bhyuan_1/.cache/modelscope/hub/models/GeoGPT/Qwen2.5-72B-GeoGPT"
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_path,
                use_fast=False,
                padding_side="left"
            )

            # Initialize model
            self.model = model_class.from_pretrained(
                model_path,
                torch_dtype="auto",
                device_map="auto",  # accelerator will handle the device mapping
            ).eval()
        else:
            # Initialize tokenizer with padding_side="left" for Decoder-only models
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                use_fast=False,
                padding_side="left"
            )

            # Initialize model
            self.model = model_class.from_pretrained(
                self.model_name,
                torch_dtype="auto",
                device_map="auto",  # accelerator will handle the device mapping
            ).eval()

        # logger.info(f"torch_dtype: {next(self.model.parameters()).dtypee}.")

        # Handle model-specific configurations
        if 'Llama' in self.model_name:
            self.model.generation_config.pad_token_id = self.tokenizer.pad_token_id

        if 'deepseek-math' in self.model_name:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.model.generation_config.pad_token_id = self.tokenizer.pad_token_id

        if 'eci-io/climategpt-70b' in self.model_name:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.model.generation_config.pad_token_id = self.tokenizer.pad_token_id

        logger.info(f"Successfully loaded model {self.model_name} with accelerator")

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
        Generate a response for the given question using the Hugging Face model with accelerator.

        Args:
            question_data (str or dict): The question to answer. Can be a string or a dictionary containing the question and additional data
            question_type (str): Type of question (OEQ or MCQ)
            max_retries (int): Maximum number of retries if the first attempt fails
            worker_logging (bool): Whether to enable logging for the worker process

        Returns:
            dict: A dictionary containing:
                - 'content': The model's response text
                - 'usage': Information about token usage
                - 'full_response': The full response object
        """
        # Process a single question by calling generate_responses_parallel with a batch of size 1
        results = self.generate_responses_parallel([question_data], question_type, max_retries, worker_logging)
        return results[0] if results else {
            "content": "Error: Failed to generate response",
            "usage": {},
            "error": "Failed to generate response"
        }

    def generate_responses_parallel(self, batch_questions, question_type="OEQ", max_retries=3, worker_logging=True):
        """
        Generate responses for multiple questions in parallel.

        Args:
            batch_questions (list): List of questions to answer in parallel
            question_type (str): Type of question (OEQ or MCQ)
            max_retries (int): Maximum number of retries if the first attempt fails
            worker_logging (bool): Whether to enable logging for the worker process

        Returns:
            list: List of responses
        """
        # Handle empty batch
        if not batch_questions:
            return []

        # Get the appropriate question type module
        type_module = get_type_module(question_type)

        # Get the system message from the question type module
        system_message = type_module.SYSTEM_MESSAGE

        # Prepare prompts for all questions in the batch
        prompts = []
        for question_data in batch_questions:
            prompt = self._prepare_prompt(question_data, question_type)
            prompts.append(prompt)

        # Create messages list format with system message for each prompt
        messages_list = [
            [
                # {"role": "system", "content": system_message},
                {"role": "user", "content": system_message + prompt}
            ] for prompt in prompts
        ]

        # Record start time
        time_start = time.time()

        # Apply chat template to all messages
        texts = [self.tokenizer.apply_chat_template(msg, tokenize=False, add_generation_prompt=True) for msg in messages_list]

        # Log the formatted prompts for debugging
        for i, prompt in enumerate(prompts):
            short_prompt = prompt[:50] + "..." if len(prompt) > 50 else prompt
            short_prompt = short_prompt.replace("\n", " ")
            logger.debug(f"Question {i+1}/{len(prompts)}: {short_prompt}")

        # Log batch size
        logger.info(f"Processing batch of {len(batch_questions)} questions in parallel")

        # Tokenize inputs
        model_inputs = self.tokenizer(texts, return_tensors="pt", padding=True, truncation=self.truncation).to(self.accelerator.device)

        # Generate response
        retry_count = 0
        MAX_RETRIES = max_retries
        MAX_NEW_TOKEN = self.max_tokens
        success = False
        error = ""
        responses = [""] * len(batch_questions)

        while not success and retry_count <= MAX_RETRIES:
            try:
                # Generate outputs with the model
                # with torch.no_grad():
                with torch.inference_mode():
                    generated_ids = self.model.generate(
                        **model_inputs,
                        max_new_tokens=MAX_NEW_TOKEN
                    )

                    # Remove input tokens from output to get generated tokens only
                    generated_ids = [
                        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
                    ]

                    # Decode generated tokens into human-readable text
                    responses = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)

                success = True
                logger.info(f"Successfully generated {len(responses)} responses in parallel")

            except torch.cuda.OutOfMemoryError:
                # Handle out-of-memory error
                torch.cuda.empty_cache()  # Release GPU memory
                retry_count += 1  # Increment retry count
                logger.warning(f"Out of memory error (retry {retry_count}/{MAX_RETRIES})")

                if retry_count > MAX_RETRIES:
                    responses = ["Error: Out of memory"] * len(batch_questions)
                    error = f"Out of memory error after {MAX_RETRIES} retries"
                    logger.error(error)

                    # If OOM and batch size > 1, try with smaller batch size
                    if len(batch_questions) > 1:
                        logger.warning("Reducing batch size and trying again with smaller batches")
                        # Split the batch in half
                        mid = len(batch_questions) // 2
                        first_half = batch_questions[:mid]
                        second_half = batch_questions[mid:]

                        # Process each half separately
                        first_results = self.generate_responses_parallel(first_half, question_type, max_retries, worker_logging)
                        second_results = self.generate_responses_parallel(second_half, question_type, max_retries, worker_logging)

                        # Combine results
                        return first_results + second_results

            except Exception as e:
                retry_count += 1
                logger.warning(f"Error during generation (retry {retry_count}/{MAX_RETRIES}): {e}")

                if retry_count > MAX_RETRIES:
                    responses = [f"Error: {str(e)}"] * len(batch_questions)
                    error = f"Error generating response: {str(e)}"
                    logger.error(error)

        # Calculate token usage and prepare results
        time_end = time.time()
        batch_time = time_end - time_start
        results = []

        logger.info(f"Batch processing completed in {batch_time:.2f} seconds")

        for i, response in enumerate(responses):
            # Calculate approximate token counts
            input_tokens = len(self.tokenizer.encode(texts[i]))
            output_tokens = len(self.tokenizer.encode(response)) if response else 0
            total_tokens = input_tokens + output_tokens

            usage = {
                "prompt_tokens": input_tokens,
                "completion_tokens": output_tokens,
                "total_tokens": total_tokens,
                "time_taken": batch_time
            }

            # Create result dictionary
            result = {
                "content": response,
                "usage": usage,
                "full_response": {
                    "model": self.model_name,
                    "choices": [{"message": {"content": response}}],
                    "usage": usage
                }
            }

            # Add error information if there was an error
            if error:
                result["error"] = error

            results.append(result)

        return results

    def generate_responses_batch(self, questions_data, question_type="OEQ", retries=0, worker_logging=True):
        """
        Generate responses for multiple questions in batches.

        Args:
            questions_data (list): List of questions to answer. Each item can be a string or a dictionary containing the question and additional data
            question_type (str): Type of question (OEQ or MCQ)
            retries (int): Number of retries if the first attempt fails
            worker_logging (bool): Whether to enable logging for the worker process

        Returns:
            list: List of responses
        """
        results = []
        total_questions = len(questions_data)
        num_batches = (total_questions + self.parallel_size - 1) // self.parallel_size

        logger.info(f"Processing {total_questions} questions in {num_batches} batches of up to {self.parallel_size}")

        # Process questions in batches to control memory usage
        for batch_idx in range(num_batches):
            start_idx = batch_idx * self.parallel_size
            end_idx = min(start_idx + self.parallel_size, total_questions)
            batch_questions = questions_data[start_idx:end_idx]

            logger.info(f"Processing batch {batch_idx + 1}/{num_batches} with {len(batch_questions)} questions in parallel")

            try:
                # Process the batch in parallel
                batch_results = self.generate_responses_parallel(batch_questions, question_type, max_retries=retries, worker_logging=worker_logging)
                results.extend(batch_results)
                logger.info(f"Completed batch {batch_idx + 1}/{num_batches}")
            except Exception as e:
                logger.error(f"Error processing batch {batch_idx + 1}: {e}")
                # Fall back to individual processing if parallel processing fails
                logger.warning("Falling back to individual processing")
                for i, question_data in enumerate(batch_questions):
                    try:
                        # Use a batch of size 1 to avoid recursion
                        individual_results = self.generate_responses_parallel([question_data], question_type, max_retries=retries, worker_logging=worker_logging)
                        if individual_results:
                            results.append(individual_results[0])
                        else:
                            results.append({
                                'content': f"Error: Failed to generate response",
                                'usage': {},
                                'error': "Failed to generate response"
                            })
                        logger.info(f"Completed question {start_idx + i + 1}/{total_questions}")
                    except Exception as e:
                        logger.error(f"Error processing question {start_idx + i + 1}: {e}")
                        # Add error result with error information
                        results.append({
                            'content': f"Error: {str(e)}",
                            'usage': {},
                            'full_response': {'error': str(e)},
                            'error': str(e)
                        })

        return results

# Specific model implementations
class LlamaLocalModel(HuggingFaceBaseModel):
    """Llama 2 7B model implementation."""
    def __init__(self, device=None, parallel_size=1, max_tokens=2000, gpu="0"):
        super().__init__(model_name="meta-llama/Llama-2-7b-chat-hf", device=device, parallel_size=parallel_size, max_tokens=max_tokens, gpu=gpu)

class MistralLocalModel(HuggingFaceBaseModel):
    """Mistral 7B model implementation."""
    def __init__(self, device=None, parallel_size=1, max_tokens=2000, gpu="0"):
        super().__init__(model_name="mistralai/Mistral-7B-Instruct-v0.2", device=device, parallel_size=parallel_size, max_tokens=max_tokens, gpu=gpu)

class PhiLocalModel(HuggingFaceBaseModel):
    """Phi-2 model implementation."""
    def __init__(self, device=None, parallel_size=1, max_tokens=2000, gpu="0"):
        super().__init__(model_name="microsoft/phi-2", device=device, parallel_size=parallel_size, max_tokens=max_tokens, gpu=gpu)

# Qwen models
class QwenMathModel(HuggingFaceBaseModel):
    """Qwen 2.5 Math PRM 7B model implementation."""
    def __init__(self, device=None, parallel_size=1, max_tokens=2000, gpu="0"):
        super().__init__(model_name="Qwen/Qwen2.5-Math-PRM-7B", device=device, parallel_size=parallel_size, max_tokens=max_tokens, gpu=gpu)

class Qwen2532BInstructModel(HuggingFaceBaseModel):
    """Qwen 2.5 32B Instruct model implementation."""
    def __init__(self, device=None, parallel_size=1, max_tokens=2000, gpu="0"):
        super().__init__(model_name="Qwen/Qwen2.5-32B-Instruct", device=device, parallel_size=parallel_size, max_tokens=max_tokens, gpu=gpu)

class Qwen253BInstructModel(HuggingFaceBaseModel):
    """Qwen 2.5 3B Instruct model implementation."""
    def __init__(self, device=None, parallel_size=1, max_tokens=2000, gpu="0"):
        super().__init__(model_name="Qwen/Qwen2.5-3B-Instruct", device=device, parallel_size=parallel_size, max_tokens=max_tokens, gpu=gpu)

class Qwen257BInstructModel(HuggingFaceBaseModel):
    """Qwen 2.5 7B Instruct model implementation."""
    def __init__(self, device=None, parallel_size=1, max_tokens=2000, gpu="0"):
        super().__init__(model_name="Qwen/Qwen2.5-7B-Instruct", device=device, parallel_size=parallel_size, max_tokens=max_tokens, gpu=gpu)

class Qwen25Coder32BInstructModel(HuggingFaceBaseModel):
    """Qwen 2.5 Coder 32B Instruct model implementation."""
    def __init__(self, device=None, parallel_size=1, max_tokens=2000, gpu="0"):
        super().__init__(model_name="Qwen/Qwen2.5-Coder-32B-Instruct", device=device, parallel_size=parallel_size, max_tokens=max_tokens, gpu=gpu)

class Qwen25Math15BInstructModel(HuggingFaceBaseModel):
    """Qwen 2.5 Math 1.5B Instruct model implementation."""
    def __init__(self, device=None, parallel_size=1, max_tokens=2000, gpu="0"):
        super().__init__(model_name="Qwen/Qwen2.5-Math-1.5B-Instruct", device=device, parallel_size=parallel_size, max_tokens=max_tokens, gpu=gpu)

class Qwen25Math72BInstructModel(HuggingFaceBaseModel):
    """Qwen 2.5 Math 72B Instruct model implementation."""
    def __init__(self, device=None, parallel_size=1, max_tokens=2000, gpu="0"):
        super().__init__(model_name="Qwen/Qwen2.5-Math-72B-Instruct", device=device, parallel_size=parallel_size, max_tokens=max_tokens, gpu=gpu)

class Qwen25Math7BInstructModel(HuggingFaceBaseModel):
    """Qwen 2.5 Math 7B Instruct model implementation."""
    def __init__(self, device=None, parallel_size=1, max_tokens=2000, gpu="0"):
        super().__init__(model_name="Qwen/Qwen2.5-Math-7B-Instruct", device=device, parallel_size=parallel_size, max_tokens=max_tokens, gpu=gpu)

# DeepSeek models
class DeepSeekMathModel(HuggingFaceBaseModel):
    """DeepSeek Math model implementation."""
    def __init__(self, device=None, parallel_size=1, max_tokens=2000, gpu="0"):
        super().__init__(model_name="deepseek-ai/deepseek-math-7b-instruct", device=device, parallel_size=parallel_size, max_tokens=max_tokens, gpu=gpu)

class DeepSeekMathRLModel(HuggingFaceBaseModel):
    """DeepSeek Math RL model implementation."""
    def __init__(self, device=None, parallel_size=1, max_tokens=2000, gpu="0"):
        super().__init__(model_name="deepseek-ai/deepseek-math-7b-rl", device=device, parallel_size=parallel_size, max_tokens=max_tokens, gpu=gpu)

# ClimateGPT models
class ClimateGPT70BModel(HuggingFaceBaseModel):
    """ClimateGPT 70B model implementation."""
    def __init__(self, device=None, parallel_size=1, max_tokens=2000, gpu="0"):
        super().__init__(model_name="eci-io/climategpt-70b", device=device, parallel_size=parallel_size, max_tokens=max_tokens, gpu=gpu)

class ClimateGPT7BModel(HuggingFaceBaseModel):
    """ClimateGPT 7B model implementation."""
    def __init__(self, device=None, parallel_size=1, max_tokens=2000, gpu="0"):
        super().__init__(model_name="eci-io/climategpt-7b", device=device, parallel_size=parallel_size, max_tokens=max_tokens, gpu=gpu)

# Gemma models
class Gemma227BITModel(HuggingFaceBaseModel):
    """Gemma 2 27B IT model implementation."""
    def __init__(self, device=None, parallel_size=1, max_tokens=2000, gpu="0", truncation=False):
        super().__init__(model_name="google/gemma-2-27b-it", device=device, parallel_size=parallel_size, max_tokens=max_tokens, gpu=gpu)

class Gemma29BITModel(HuggingFaceBaseModel):
    """Gemma 2 9B IT model implementation."""
    def __init__(self, device=None, parallel_size=1, max_tokens=2000, gpu="0", truncation=False):
        super().__init__(model_name="google/gemma-2-9b-it", device=device, parallel_size=parallel_size, max_tokens=max_tokens, gpu=gpu)

# Llama models
class Llama3370BInstructModel(HuggingFaceBaseModel):
    """Llama 3.3 70B Instruct model implementation."""
    def __init__(self, device=None, parallel_size=1, max_tokens=2000, gpu="0"):
        super().__init__(model_name="meta-llama/Llama-3.3-70B-Instruct", device=device, parallel_size=parallel_size, max_tokens=max_tokens, gpu=gpu)

# GeoGPT models
class Qwen2572BGeoGPTModel(HuggingFaceBaseModel):
    """Qwen 2.5 72B GeoGPT model implementation."""
    def __init__(self, device=None, parallel_size=1, max_tokens=2000, gpu="0"):
        logger.info(f"Each GPU group will process its datasets SEQUENTIALLY")
        super().__init__(model_name="GeoGPT-Research-Project/Qwen2.5-72B-GeoGPT", device=device, parallel_size=parallel_size, max_tokens=max_tokens, gpu=gpu)
