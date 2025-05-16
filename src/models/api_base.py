"""
Base class for API-based models that use Ray for parallel processing.
"""

import abc
import logging
import time
from .base import BaseModel

# Configure logging
logger = logging.getLogger(__name__)

# Ray initialization and remote function will be defined later when needed

def format_api_response(content, usage, full_response, error=None):
    """
    Standardize the response format across all API models.

    Args:
        content (str): The model's response text
        usage (dict): Information about token usage
        full_response (dict or object): The full response object from the API
        error (str, optional): Error message if there was an error

    Returns:
        dict: A standardized response dictionary
    """
    # Create the base response dictionary
    response = {
        "content": content,
        "usage": usage,
        "full_response": full_response
    }

    # Add error if provided
    if error:
        response["error"] = error

    # Check if reasoning_content already exists in the full_response dictionary
    if isinstance(full_response, dict) and 'reasoning_content' in full_response:
        response["reasoning_content"] = full_response['reasoning_content']
        logger.info(f"Found reasoning_content in full_response dictionary, length: {len(full_response['reasoning_content'])} characters")
    else:
        # Extract reasoning_content if it exists in the response
        # For DeepSeek R1 models
        try:
            if isinstance(full_response, dict) and 'choices' in full_response:
                choice = full_response.get('choices', [{}])[0]
                if isinstance(choice, dict) and 'message' in choice:
                    message = choice.get('message', {})
                    if 'reasoning_content' in message:
                        response["reasoning_content"] = message.get('reasoning_content')
                        logger.info(f"Extracted reasoning_content from DeepSeek R1 model response, length: {len(response['reasoning_content'])} characters")
            # For OpenAI client response objects
            elif hasattr(full_response, 'choices') and len(full_response.choices) > 0:
                choice = full_response.choices[0]
                if hasattr(choice, 'message') and hasattr(choice.message, 'reasoning_content'):
                    response["reasoning_content"] = choice.message.reasoning_content
                    logger.info(f"Extracted reasoning_content from OpenAI client response, length: {len(response['reasoning_content'])} characters")
        except Exception as e:
            logger.warning(f"Error extracting reasoning_content: {e}")

    return response

class APIBaseModel(BaseModel):
    """
    Base class for all API-based model implementations.
    Uses Ray for parallel processing of API calls.
    Falls back to sequential processing if Ray is not available.
    """

    # Class variable to track if Ray has been initialized
    _ray_initialized = False
    _ray_module = None
    _call_api_with_retry = None

    @classmethod
    def init_ray(cls):
        """Initialize Ray if not already initialized."""
        if cls._ray_initialized:
            return True

        try:
            # Only import Ray when needed
            import ray
            cls._ray_module = ray

            # Initialize Ray if not already initialized
            def init_ray_with_fallbacks():
                """Initialize Ray with multiple fallback options if the primary initialization fails."""
                if ray.is_initialized():
                    logger.info("Ray already initialized")
                    return True

                # First attempt: Full configuration
                try:
                    ray.init(
                        ignore_reinit_error=True,
                        logging_level=logging.INFO,
                        log_to_driver=True,
                        object_store_memory=2 * 10**9,  # 2 GB
                        include_dashboard=False
                    )
                    logger.info("Ray initialized with full configuration")
                    return True
                except Exception as e:
                    logger.warning(f"First Ray initialization attempt failed: {e}")

                # Second attempt: With reduced memory and different settings
                try:
                    ray.init(
                        ignore_reinit_error=True,
                        logging_level=logging.INFO,
                        log_to_driver=True,
                        object_store_memory=1 * 10**9,  # 1 GB
                        include_dashboard=False,
                        num_cpus=None  # Use default CPU detection
                    )
                    logger.info("Ray initialized with reduced memory configuration")
                    return True
                except Exception as e:
                    logger.warning(f"Second Ray initialization attempt failed: {e}")

                # Third attempt: Minimal configuration
                try:
                    ray.init(
                        ignore_reinit_error=True,
                        logging_level=logging.INFO,
                        include_dashboard=False
                    )
                    logger.info("Ray initialized with minimal configuration")
                    return True
                except Exception as e:
                    logger.warning(f"Third Ray initialization attempt failed: {e}")

                # Final attempt: Absolute minimal
                try:
                    ray.init(ignore_reinit_error=True)
                    logger.warning("Ray initialized with absolute minimal settings")
                    return True
                except Exception as e:
                    logger.error(f"All Ray initialization attempts failed. Final error: {e}")
                    return False

            # Try to initialize Ray
            ray_initialized = init_ray_with_fallbacks()

            if ray_initialized:
                # Define the remote function
                @ray.remote
                def _call_api_with_retry(model_class_name, model_args, question_data, question_type, retries=0, worker_logging=True):
                    # This is the same function body as _call_api_with_retry_func
                    # Configure logging for this Ray worker
                    import logging
                    worker_logger = logging.getLogger("src.models.api_base.worker")

                    # Set up worker logging based on the worker_logging parameter
                    if worker_logging:
                        worker_logger.setLevel(logging.INFO)

                        # Create console handler if not already present
                        if not worker_logger.handlers:
                            console_handler = logging.StreamHandler()
                            console_handler.setLevel(logging.INFO)
                            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                            console_handler.setFormatter(formatter)
                            worker_logger.addHandler(console_handler)
                    else:
                        # Disable logging for this worker
                        worker_logger.setLevel(logging.ERROR)  # Only log errors

                        # Remove any existing handlers
                        for handler in worker_logger.handlers[:]:
                            worker_logger.removeHandler(handler)

                    # Dynamically import and instantiate the model class
                    import importlib
                    module_name, class_name = model_class_name.rsplit('.', 1)
                    module = importlib.import_module(module_name)
                    model_class = getattr(module, class_name)
                    model_instance = model_class(**model_args)

                    # Get a short version of the question for logging
                    if isinstance(question_data, dict):
                        question_text = question_data.get('question', question_data.get('problem', ''))
                    else:
                        question_text = str(question_data)

                    short_question = question_text[:50] + "..." if len(question_text) > 50 else question_text
                    short_question = short_question.replace("\n", " ")

                    # Calculate max attempts (retries + 1 for the initial attempt)
                    max_attempts = retries + 1

                    worker_logger.info(f"API call starting for question: {short_question}")
                    worker_logger.info(f"Model class: {model_class_name}")
                    worker_logger.info(f"Model args: {model_args}")

                    # Log specific model arguments for debugging
                    if 'parallel_size' in model_args:
                        worker_logger.info(f"Parallel size: {model_args['parallel_size']}")
                    if 'max_tokens' in model_args:
                        worker_logger.info(f"Max tokens: {model_args['max_tokens']}")

                    worker_logger.info(f"Question type: {question_type}")
                    worker_logger.info(f"Retries: {retries} (will try up to {max_attempts} times)")

                    # Call the model's _make_api_call method
                    for attempt in range(max_attempts):
                        try:
                            worker_logger.info(f"Attempt {attempt+1}/{max_attempts} for question: {short_question}")

                            # Call the model's _make_api_call method
                            result = model_instance._make_api_call(question_data, question_type)

                            # Check if result is None
                            if result is None:
                                worker_logger.error(f"_make_api_call returned None for question: {short_question}")
                                # Create a proper error result
                                result = {
                                    'content': "Error: API call returned None",
                                    'usage': {},
                                    'full_response': {'error': "API call returned None"},
                                    'error': "API call returned None",
                                    'logs': [f"API call returned None on attempt {attempt+1}"]
                                }
                                # Raise an exception to trigger retry or error handling
                                raise ValueError("_make_api_call returned None")

                            worker_logger.info(f"API call succeeded for question: {short_question}")
                            worker_logger.info(f"Result type: {type(result)}")

                            # Log some information about the result
                            if isinstance(result, dict):
                                if 'content' in result:
                                    content_length = len(result['content']) if result['content'] else 0
                                    worker_logger.info(f"Content length: {content_length} characters")

                                if 'error' in result:
                                    worker_logger.warning(f"Result contains error: {result['error']}")

                                # Add a log entry to the result so the main process can see it
                                if 'logs' not in result:
                                    result['logs'] = []
                                result['logs'].append(f"API call succeeded after {attempt+1} attempts")
                            else:
                                # If result is not a dict (but not None), convert it to a proper dict
                                worker_logger.warning(f"API call returned non-dict result: {type(result)} for question: {short_question}")
                                worker_logger.warning(f"Result value: {str(result)[:100]}...")
                                original_result = result
                                result = {
                                    'content': str(original_result),
                                    'usage': {},
                                    'full_response': {'original_result': str(original_result)},
                                    'logs': [f"API call returned non-dict result: {type(original_result)}"]
                                }

                            # Log success and return the result
                            worker_logger.info(f"Successfully completed API call for question: {short_question}")
                            return result
                        except Exception as e:
                            error_msg = str(e)
                            error_type = type(e).__name__
                            worker_logger.error(f"Attempt {attempt+1}/{max_attempts} failed for question: {short_question}")
                            worker_logger.error(f"Error type: {error_type}")
                            worker_logger.error(f"Error details: {error_msg}")

                            # Add traceback information
                            import traceback
                            worker_logger.error(f"Traceback: {traceback.format_exc()}")

                            if attempt < max_attempts - 1:
                                # Exponential backoff
                                sleep_time = 2 ** attempt
                                worker_logger.info(f"Retrying in {sleep_time} seconds...")
                                time.sleep(sleep_time)
                            else:
                                worker_logger.error(f"Failed to get response after {max_attempts} attempts for question: {short_question}")
                                worker_logger.error(f"Final error: {error_msg}")

                                # Create an error result with detailed information
                                error_result = {
                                    'content': f"Error: {error_msg}",
                                    'usage': {},
                                    'full_response': {
                                        'error': error_msg,
                                        'error_type': error_type,
                                        'question': short_question
                                    },
                                    'error': error_msg,
                                    'logs': [
                                        f"API call failed after {max_attempts} attempts",
                                        f"Error type: {error_type}",
                                        f"Error message: {error_msg}"
                                    ]
                                }

                                # Return the error result instead of raising an exception
                                worker_logger.info(f"Returning error result for question: {short_question}")
                                return error_result

                # Store the remote function
                cls._call_api_with_retry = _call_api_with_retry
                cls._ray_initialized = True
                return True
            else:
                logger.error("Failed to initialize Ray after multiple attempts. Some functionality may be limited.")
                return False
        except ImportError:
            logger.warning("Ray is not installed. Falling back to sequential processing.")
            return False
        except Exception as e:
            logger.error(f"Error initializing Ray: {e}")
            return False

    def __init__(self, parallel_size=4, max_tokens=2000):
        """
        Initialize the API base model.

        Args:
            parallel_size (int): Number of parallel API calls to make
            max_tokens (int): Maximum number of tokens in the response
        """
        super().__init__(parallel_size=parallel_size)
        self.max_tokens = max_tokens

        # Try to initialize Ray if not already initialized
        self.use_ray = self.__class__.init_ray() if parallel_size > 1 else False

        if self.use_ray:
            logger.info(f"Initialized API base model with Ray parallelization, parallel size: {parallel_size}, max_tokens: {max_tokens}")
        else:
            logger.warning(f"Initialized API base model WITHOUT Ray parallelization (sequential mode). Performance may be reduced.")

    def _make_api_call(self, question_data, question_type):
        """
        Make the actual API call. To be implemented by subclasses.

        Args:
            question_data (str or dict): The question to answer. Can be a string or a dictionary containing the question and additional data
            question_type (str): Type of question (OEQ or MCQ)

        Returns:
            dict: The model's response
        """
        raise NotImplementedError("Subclasses must implement _make_api_call")

    def generate_response(self, question_data, question_type="OEQ", retries=0, worker_logging=True):
        """
        Generate a response for the given question using the API.
        Uses Ray for parallel processing if available, otherwise falls back to direct API calls.

        Args:
            question_data (str or dict): The question to answer. Can be a string or a dictionary containing the question and additional data
            question_type (str): Type of question (OEQ or MCQ)
            retries (int): Number of retries if the first attempt fails (0 means try once, 1 means try once and retry once if it fails)
            worker_logging (bool): Whether to enable logging for the worker process

        Returns:
            dict: A dictionary containing:
                - 'content': The model's response text
                - 'usage': Information about token usage
                - 'full_response': The full response object
        """
        # If Ray is not available, fall back to direct API call
        if not self.use_ray:
            return self._direct_api_call_with_retry(question_data, question_type, retries)

        # Ray is available, use parallel processing
        try:
            # Get the fully qualified class name for serialization
            model_class_name = f"{self.__class__.__module__}.{self.__class__.__name__}"

            # Create a dictionary of model arguments
            model_args = {'parallel_size': self.parallel_size, 'max_tokens': self.max_tokens}

            # Get a short version of the question for logging
            if isinstance(question_data, dict):
                question_text = question_data.get('question', question_data.get('problem', ''))
            else:
                question_text = str(question_data)

            short_question = question_text[:50] + "..." if len(question_text) > 50 else question_text
            short_question = short_question.replace("\n", " ")

            logger.info(f"Submitting Ray task for question: {short_question}")
            logger.info(f"Retries: {retries}, Worker logging: {worker_logging}")

            # Submit the task using the class variable
            task = self.__class__._call_api_with_retry.remote(
                model_class_name, model_args, question_data, question_type, retries, worker_logging
            )

            # Get the result without a timeout
            logger.info(f"Waiting for Ray task to complete")
            result = self.__class__._ray_module.get(task)

            # Check if result is None
            if result is None:
                logger.error(f"Ray task returned None")
                raise ValueError("Ray task returned None")

            # Check if result is a dictionary
            if not isinstance(result, dict):
                logger.error(f"Ray task returned non-dict result: {type(result)}")
                raise ValueError(f"Ray task returned non-dict result: {type(result)}")

            # Log any logs from the worker process
            if 'logs' in result:
                for log_entry in result['logs']:
                    logger.info(f"Worker log: {log_entry}")

            logger.info(f"Successfully received result from Ray task")
            return result

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error in generate_response with Ray: {error_msg}")
            logger.error(f"Error type: {type(e).__name__}")

            # Add detailed error information
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")

            # Try falling back to direct API call if Ray fails
            logger.warning(f"Ray task failed, falling back to direct API call")
            try:
                return self._direct_api_call_with_retry(question_data, question_type, retries)
            except Exception as e2:
                error_msg = str(e2)
                logger.error(f"Direct API call also failed: {error_msg}")

                # Return an error result
                return {
                    'content': f"Error: {error_msg}",
                    'usage': {},
                    'full_response': {'error': error_msg, 'error_type': type(e2).__name__},
                    'error': error_msg
                }

    def _direct_api_call_with_retry(self, question_data, question_type, retries=0):
        """
        Make a direct API call with retry logic, without using Ray.
        This is a fallback method when Ray is not available.

        Args:
            question_data (str or dict): The question to answer. Can be a string or a dictionary containing the question and additional data
            question_type (str): Type of question (OEQ or MCQ)
            retries (int): Number of retries if the first attempt fails

        Returns:
            dict: The model's response
        """
        # Get a short version of the question for logging
        if isinstance(question_data, dict):
            question_text = question_data.get('question', question_data.get('problem', ''))
        else:
            question_text = str(question_data)

        short_question = question_text[:50] + "..." if len(question_text) > 50 else question_text
        short_question = short_question.replace("\n", " ")

        logger.info(f"Making direct API call for question: {short_question}")
        logger.info(f"Retries: {retries}")

        # Calculate max attempts (retries + 1 for the initial attempt)
        max_attempts = retries + 1

        # Call the model's _make_api_call method with retry logic
        for attempt in range(max_attempts):
            try:
                logger.info(f"Direct API call attempt {attempt+1}/{max_attempts}")

                # Call the model's _make_api_call method
                result = self._make_api_call(question_data, question_type)

                # Check if result is None
                if result is None:
                    logger.error(f"_make_api_call returned None")
                    raise ValueError("_make_api_call returned None")

                logger.info(f"Successfully completed direct API call")
                return result

            except Exception as e:
                error_msg = str(e)
                logger.error(f"Direct API call attempt {attempt+1}/{max_attempts} failed: {error_msg}")

                if attempt < max_attempts - 1:
                    # Exponential backoff
                    sleep_time = 2 ** attempt
                    logger.info(f"Retrying direct API call in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                else:
                    logger.error(f"Failed to get response after {max_attempts} direct API call attempts")

                    # Create an error result
                    return {
                        'content': f"Error: {error_msg}",
                        'usage': {},
                        'full_response': {'error': error_msg, 'error_type': type(e).__name__},
                        'error': error_msg
                    }

    def generate_responses_batch(self, questions_data, question_type="OEQ", retries=0, worker_logging=True):
        """
        Generate responses for multiple questions in parallel.
        Uses Ray for parallel processing if available, otherwise falls back to sequential processing.

        Args:
            questions_data (list): List of questions to answer. Each item can be a string or a dictionary containing the question and additional data
            question_type (str): Type of question (OEQ or MCQ)
            retries (int): Number of retries if the first attempt fails (0 means try once, 1 means try once and retry once if it fails)
            worker_logging (bool): Whether to enable logging for the worker process

        Returns:
            list: List of responses
        """
        # If Ray is not available, fall back to sequential processing
        if not self.use_ray:
            return self._generate_responses_sequential(questions_data, question_type, retries)

        # Ray is available, use parallel processing
        # Calculate number of batches
        total_questions = len(questions_data)
        num_batches = (total_questions + self.parallel_size - 1) // self.parallel_size

        logger.info(f"Processing {total_questions} questions in {num_batches} batches of up to {self.parallel_size}")
        logger.info(f"Retries: {retries}, Worker logging: {worker_logging}")

        all_results = []

        # Process questions in batches to control memory usage
        for batch_idx in range(num_batches):
            start_idx = batch_idx * self.parallel_size
            end_idx = min(start_idx + self.parallel_size, total_questions)
            batch_questions = questions_data[start_idx:end_idx]

            logger.info(f"Submitting batch {batch_idx + 1}/{num_batches} with {len(batch_questions)} questions")

            # Get the fully qualified class name for serialization
            model_class_name = f"{self.__class__.__module__}.{self.__class__.__name__}"

            # Create a dictionary of model arguments
            model_args = {'parallel_size': self.parallel_size, 'max_tokens': self.max_tokens}

            # Submit all tasks in this batch
            tasks = []
            for question in batch_questions:
                tasks.append(self.__class__._call_api_with_retry.remote(
                    model_class_name, model_args, question, question_type, retries, worker_logging
                ))

            # Get all results from this batch in parallel
            try:
                # Try to get all results, but handle individual failures
                batch_results = []
                for i, task in enumerate(tasks):
                    try:
                        # Add a timeout to ray.get to prevent hanging
                        logger.info(f"Waiting for result of question {start_idx + i + 1}/{total_questions}")

                        # Get the result without a timeout
                        logger.info(f"Waiting for Ray task to complete for question {start_idx + i + 1}")
                        result = self.__class__._ray_module.get(task)

                        # Check if result is None
                        if result is None:
                            logger.error(f"Ray task returned None for question {start_idx + i + 1}")
                            raise ValueError("Ray task returned None")

                        # Check if result is a dictionary
                        if not isinstance(result, dict):
                            logger.error(f"Ray task returned non-dict result: {type(result)} for question {start_idx + i + 1}")
                            raise ValueError(f"Ray task returned non-dict result: {type(result)}")

                        # Log any logs from the worker process
                        if 'logs' in result:
                            for log_entry in result['logs']:
                                logger.info(f"Worker log for question {start_idx + i + 1}: {log_entry}")

                        batch_results.append(result)
                        logger.info(f"Completed question {start_idx + i + 1}/{total_questions}")
                    except Exception as e:
                        error_msg = str(e)
                        logger.error(f"Error processing question {start_idx + i + 1}: {error_msg}")
                        logger.error(f"Error type: {type(e).__name__}")

                        # Add detailed error information
                        import traceback
                        logger.error(f"Traceback: {traceback.format_exc()}")

                        # Add error result with error information in both content and full_response
                        error_result = {
                            'content': f"Error: {error_msg}",
                            'usage': {},
                            'full_response': {'error': error_msg, 'error_type': type(e).__name__},
                            'error': error_msg,  # Add explicit error field
                            'logs': [f"Error in Ray task: {error_msg}"]
                        }
                        batch_results.append(error_result)

                all_results.extend(batch_results)
                logger.info(f"Completed batch {batch_idx + 1}/{num_batches} with {len(batch_results)} results")

                # Count successful and error results
                success_count = sum(1 for r in batch_results if 'error' not in r)
                error_count = sum(1 for r in batch_results if 'error' in r)
                logger.info(f"Batch {batch_idx + 1} results: {success_count} successful, {error_count} errors")
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Error processing batch {batch_idx + 1}: {error_msg}")
                logger.error(f"Error type: {type(e).__name__}")

                # Add detailed error information
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")

                # Try falling back to sequential processing for this batch
                logger.warning(f"Ray batch processing failed, trying sequential processing for batch {batch_idx + 1}")
                try:
                    batch_results = []
                    for i, question in enumerate(batch_questions):
                        logger.info(f"Sequential fallback for question {start_idx + i + 1}/{total_questions}")
                        result = self._direct_api_call_with_retry(question, question_type, retries)
                        batch_results.append(result)

                        # Log success or failure
                        if 'error' in result:
                            logger.error(f"Sequential fallback failed for question {start_idx + i + 1}")
                        else:
                            logger.info(f"Sequential fallback succeeded for question {start_idx + i + 1}")

                    all_results.extend(batch_results)

                    # Count successful and error results
                    sequential_success = sum(1 for r in batch_results if 'error' not in r)
                    sequential_error = sum(1 for r in batch_results if 'error' in r)
                    logger.info(f"Sequential fallback for batch {batch_idx + 1} results: {sequential_success} successful, {sequential_error} errors")

                    # Skip the individual Ray processing below
                    continue

                except Exception as e2:
                    error_msg2 = str(e2)
                    logger.error(f"Sequential fallback also failed for batch {batch_idx + 1}: {error_msg2}")
                    logger.error(f"Falling back to individual Ray processing as last resort")

                # Process questions individually with Ray as last resort
                for i, question in enumerate(batch_questions):
                    try:
                        logger.info(f"Starting individual processing for question {start_idx + i + 1}/{total_questions}")

                        # Submit the task
                        task = self.__class__._call_api_with_retry.remote(
                            model_class_name, model_args, question, question_type, retries, worker_logging
                        )

                        # Get the result without a timeout
                        logger.info(f"Waiting for individual Ray task to complete for question {start_idx + i + 1}")
                        result = self.__class__._ray_module.get(task)

                        # Check if result is None
                        if result is None:
                            logger.error(f"Individual Ray task returned None for question {start_idx + i + 1}")
                            raise ValueError("Ray task returned None")

                        # Check if result is a dictionary
                        if not isinstance(result, dict):
                            logger.error(f"Individual Ray task returned non-dict result: {type(result)} for question {start_idx + i + 1}")
                            raise ValueError(f"Ray task returned non-dict result: {type(result)}")

                        # Log any logs from the worker process
                        if 'logs' in result:
                            for log_entry in result['logs']:
                                logger.info(f"Worker log for question {start_idx + i + 1}: {log_entry}")

                        all_results.append(result)
                        logger.info(f"Completed individual processing for question {start_idx + i + 1}/{total_questions}")
                    except Exception as e:
                        error_msg = str(e)
                        logger.error(f"Error in individual processing for question {start_idx + i + 1}: {error_msg}")
                        logger.error(f"Error type: {type(e).__name__}")

                        # Add detailed error information
                        import traceback
                        logger.error(f"Traceback: {traceback.format_exc()}")

                        # Add error result with error information in both content and full_response
                        error_result = {
                            'content': f"Error: {error_msg}",
                            'usage': {},
                            'full_response': {'error': error_msg, 'error_type': type(e).__name__},
                            'error': error_msg,  # Add explicit error field
                            'logs': [f"Error in individual processing: {error_msg}"]
                        }
                        all_results.append(error_result)

                # Log individual processing results for this batch
                individual_success = sum(1 for r in all_results[-len(batch_questions):] if 'error' not in r)
                individual_error = sum(1 for r in all_results[-len(batch_questions):] if 'error' in r)
                logger.info(f"Individual processing of batch {batch_idx + 1} results: {individual_success} successful, {individual_error} errors")

        # Log final results
        total_success = sum(1 for r in all_results if 'error' not in r)
        total_error = sum(1 for r in all_results if 'error' in r)
        logger.info(f"Final results: {len(all_results)} total, {total_success} successful, {total_error} errors")

        return all_results

    def _generate_responses_sequential(self, questions_data, question_type="OEQ", retries=0):
        """
        Generate responses for multiple questions sequentially.
        This is a fallback method when Ray is not available.

        Args:
            questions_data (list): List of questions to answer. Each item can be a string or a dictionary containing the question and additional data
            question_type (str): Type of question (OEQ or MCQ)
            retries (int): Number of retries if the first attempt fails

        Returns:
            list: List of response dictionaries
        """
        logger.info(f"Processing {len(questions_data)} questions sequentially (Ray not available)")
        logger.info(f"Retries: {retries}")

        results = []
        for i, question_data in enumerate(questions_data):
            logger.info(f"Processing question {i+1}/{len(questions_data)} sequentially")

            # Use the direct API call method
            result = self._direct_api_call_with_retry(question_data, question_type, retries)
            results.append(result)

            # Log success or failure
            if 'error' in result:
                logger.error(f"Sequential processing failed for question {i+1}")
            else:
                logger.info(f"Sequential processing succeeded for question {i+1}")

        # Count successful and error results
        successful = sum(1 for r in results if 'error' not in r)
        errors = sum(1 for r in results if 'error' in r)
        logger.info(f"Sequential processing results: {len(results)} total, {successful} successful, {errors} errors")

        return results
