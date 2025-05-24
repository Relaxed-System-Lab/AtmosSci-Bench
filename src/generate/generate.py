#!/usr/bin/env python
import os
import sys
import argparse
import json
import logging
import datetime
import time
from statistics import mean, median

# Import the model registry
from src.models import get_model

# Configure root logger to capture logs from all modules
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Console handler
    ]
)

# Create module logger
logger = logging.getLogger(__name__)

# File handler will be added in the main function after the output directory is created

def read_jsonl(file_path):
    """Read data from a JSONL file."""
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                data.append(json.loads(line))
        logger.info(f"Successfully loaded {len(data)} problems from {file_path}")
        return data
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}")
        raise

def write_jsonl(data, file_path):
    """Write data to a JSONL file."""
    try:
        # Custom JSON encoder to handle non-serializable objects
        class CustomJSONEncoder(json.JSONEncoder):
            def default(self, obj):
                # Convert non-serializable objects to their string representation
                try:
                    return super().default(obj)
                except TypeError:
                    return str(obj)

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            for item in data:
                try:
                    # Try to serialize with the custom encoder
                    f.write(json.dumps(item, cls=CustomJSONEncoder) + '\n')
                except Exception as e:
                    # If serialization still fails, log the error and create a simplified version
                    logger.error(f"Error serializing item: {e}")
                    # Create a simplified version with just the essential fields
                    simplified_item = {
                        'id': item.get('id', 'unknown'),
                        'question': item.get('question', ''),
                        'error': f"Serialization error: {str(e)}",
                        'model': item.get('model', ''),
                        'base': item.get('base', '')
                    }
                    f.write(json.dumps(simplified_item) + '\n')

        logger.info(f"Successfully wrote {len(data)} items to {file_path}")
    except Exception as e:
        logger.error(f"Error writing data to {file_path}: {e}")
        raise

def get_latest_log(logs_dir):
    """
    Get the path to the latest log file in the logs directory.

    Args:
        logs_dir (str): Path to the logs directory

    Returns:
        str: Path to the latest log file, or None if no logs exist
    """
    try:
        log_files = [os.path.join(logs_dir, f) for f in os.listdir(logs_dir) if f.startswith("generation_") and f.endswith(".log")]
        if not log_files:
            return None
        # Sort by modification time (newest first)
        log_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        return log_files[0]
    except Exception as e:
        logger.error(f"Error getting latest log file: {e}")
        return None

def update_metadata(metadata, metadata_path):
    """
    Update the metadata file with the latest statistics.

    Args:
        metadata (dict): The metadata dictionary to write
        metadata_path (str): Path to the metadata file
    """
    try:
        # Update the timestamp
        metadata['timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Write the metadata to the file
        os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Updated metadata at {metadata_path}")
    except Exception as e:
        logger.error(f"Error updating metadata: {e}")
        # Don't raise the exception to avoid interrupting the main process

def process_problems(problems, model_name, output_path, base_name, question_type="OEQ", dataset_name="PAC", retries=0, parallel_size=4, max_tokens=2000, no_fallback=False, metadata_path=None, logs_dir=None, worker_logging=True, gpu=None):
    """
    Process all problems and save the responses to a JSONL file.
    Always resumes from previous run by default.

    Args:
        problems (list): List of problem dictionaries
        model_name (str): Name of the model to use
        output_path (str): Path to save the responses
        base_name (str): Name of the base model
        question_type (str): Type of question (OEQ or MCQ)
        dataset_name (str): Name of the dataset
        retries (int): Number of retries if the first attempt fails (0 means try once, 1 means try once and retry once if it fails)
        parallel_size (int): Number of parallel processes to use
        max_tokens (int): Maximum number of tokens in the response
        no_fallback (bool): Whether to disable fallback to individual processing
        metadata_path (str, optional): Path to save the metadata file. If provided, metadata will be updated after each batch.
        logs_dir (str, optional): Directory to save log files. If provided, logs will be saved to this directory.
        worker_logging (bool): Whether to enable logging for the worker processes
        gpu (str, optional): GPU device IDs to use (e.g., "0" or "0,1,2,3"). If None, use all available GPUs.

    Returns:
        tuple: (all_responses, metadata_dict) where metadata_dict contains statistics about the processing
    """
    # Get the model implementation
    ModelClass = get_model(model_name, base_name)

    # Initialize model parameters
    model_params = {
        "parallel_size": parallel_size,
        "max_tokens": max_tokens
    }

    # If using a local model (huggingface) and GPU configuration is provided
    if base_name == "huggingface" and gpu is not None:
        model_params["gpu"] = gpu
        logger.info(f"Using GPU(s): {gpu}")

    # Initialize the model with the parameters
    model = ModelClass(**model_params)

    logger.info(f"Using model: {model_name} with base: {base_name}, parallel size: {parallel_size}, max_tokens: {max_tokens}")
    logger.info(f"Retries: {retries}, Worker logging: {worker_logging}")

    # Always check for existing responses to resume from
    existing_responses = {}

    if os.path.exists(output_path):
        logger.info(f"Checking for existing responses in {output_path}")
        try:
            existing_data = read_jsonl(output_path)
            successful_count = 0
            error_count = 0

            for item in existing_data:
                if 'id' in item:
                    if 'error' in item:
                        # Skip items with errors so they can be reprocessed
                        error_count += 1
                        logger.info(f"Found error in item {item['id']}, will reprocess")
                        continue
                    elif 'response' in item:
                        # Only store successful responses
                        existing_responses[item['id']] = item
                        successful_count += 1

            logger.info(f"Loaded {successful_count} successful responses, found {error_count} errors that will be reprocessed")
        except Exception as e:
            logger.error(f"Error loading existing responses: {e}")
            logger.info("Will start from scratch")
            existing_responses = {}

    # Prepare questions and problem IDs
    questions_data = []
    problem_ids = []
    original_indices = []

    print("existing_responses", existing_responses.keys())
    for idx, problem in enumerate(problems):
        problem_id = problem.get('id', f"problem_{idx}")
        # print("problem_id", problem_id)
        # print("problem_id in existing_responses", problem_id in existing_responses)
        # Skip problems that have already been processed successfully
        if problem_id in existing_responses:
            logger.info(f"Skipping problem {problem_id} as it was already processed successfully")
            continue

        # For MCQ questions, pass the full problem object to include options and knowledge
        if question_type == "MCQ":
            questions_data.append(problem)
        else:
            # For other question types, just extract the question text
            question = problem.get('question', problem.get('problem', ''))
            questions_data.append(question)

        problem_ids.append(problem_id)
        original_indices.append(idx)

    if len(questions_data) == 0:
        logger.info("All problems have already been processed. Nothing to do.")
        return list(existing_responses.values())

    logger.info(f"Processing {len(questions_data)} problems in batches of {parallel_size}")

    # Initialize responses list with existing responses
    all_responses = list(existing_responses.values())

    # Define total_questions for statistics
    total_questions = len(problems)

    # Function to calculate statistics
    def calculate_statistics():
        successful_count = sum(1 for resp in all_responses if 'id' in resp and 'response' in resp and 'error' not in resp)
        error_count = sum(1 for resp in all_responses if 'id' in resp and 'error' in resp)
        missing_count = total_questions - len(all_responses)
        completion_percentage = round((successful_count / total_questions) * 100, 2) if total_questions > 0 else 0

        return {
            'total_questions': total_questions,
            'successful_responses': successful_count,
            'error_responses': error_count,
            'missing_questions': missing_count,
            'completion_percentage': completion_percentage,
            'processed_questions': len(questions_data),
            'remaining_questions': len(questions_data) - (len(all_responses) - len(existing_responses.values()))
        }

    # Get model details
    model_details = {
        'max_tokens': max_tokens
    }

    # Add GPU configuration to model details if applicable
    if base_name == "huggingface" and gpu is not None:
        model_details['gpu'] = gpu

    # Add model name if available
    if hasattr(model, 'model_name'):
        model_details['model_name'] = model.model_name

    # Get log directory information
    logs_dir = os.path.join(os.path.dirname(output_path), "logs")
    os.makedirs(logs_dir, exist_ok=True)

    # Get current log file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    current_log_file = os.path.join(logs_dir, f"generation_{timestamp}.log")

    # Create initial metadata dictionary
    metadata = {
        'model': {
            'name': model_name,
            'base': base_name,
            'details': model_details
        },
        'dataset': {
            'name': dataset_name,
            'type': question_type,
            'total_questions': total_questions
        },
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'statistics': calculate_statistics(),
        'parameters': {
            'retries': retries,
            'parallel_size': parallel_size,
            'max_tokens': max_tokens,
            'no_fallback': no_fallback,
            'worker_logging': worker_logging
        },
        'logs': {
            'directory': logs_dir,
            'current_log': current_log_file
        }
    }

    # Write initial metadata if path is provided
    if metadata_path:
        update_metadata(metadata, metadata_path)
        logger.info(f"Initial metadata written to {metadata_path}")

    # Calculate batch size and number of batches
    batch_size = parallel_size
    num_batches = (len(questions_data) + batch_size - 1) // batch_size

    # Counter for consecutive failed batches
    consecutive_failed_batches = 0
    max_consecutive_failures = 4  # Terminate after 4 consecutive batch failures

    # Track batch processing times for estimating remaining time
    batch_times = []

    # Process questions in batches
    for batch_idx in range(num_batches):
        start_idx = batch_idx * batch_size
        end_idx = min(start_idx + batch_size, len(questions_data))

        batch_questions = questions_data[start_idx:end_idx]
        batch_problem_ids = problem_ids[start_idx:end_idx]

        logger.info(f"Processing batch {batch_idx + 1}/{num_batches} with {len(batch_questions)} questions")

        # Start timing the batch
        batch_start_time = time.time()

        try:
            # Process this batch
            batch_results = model.generate_responses_batch(batch_questions, question_type, retries, worker_logging)

            # Calculate batch processing time
            batch_end_time = time.time()
            batch_duration = batch_end_time - batch_start_time
            batch_times.append(batch_duration)

            # Calculate average batch time and estimate remaining time
            avg_batch_time = mean(batch_times) if batch_times else 0
            remaining_batches = num_batches - (batch_idx + 1)
            estimated_remaining_time = avg_batch_time * remaining_batches

            # Format times for logging
            batch_duration_str = f"{batch_duration:.2f} seconds"
            if batch_duration > 60:
                batch_duration_str = f"{batch_duration/60:.2f} minutes"

            remaining_time_str = f"{estimated_remaining_time:.2f} seconds"
            if estimated_remaining_time > 60:
                remaining_time_str = f"{estimated_remaining_time/60:.2f} minutes"
                if estimated_remaining_time > 3600:
                    remaining_time_str = f"{estimated_remaining_time/3600:.2f} hours"

            logger.info(f"Batch {batch_idx + 1} completed in {batch_duration_str}, got {len(batch_results)} results")
            if remaining_batches > 0:
                logger.info(f"Estimated time for remaining {remaining_batches} batches: {remaining_time_str}")

            # Check if the number of results matches the number of questions in this batch
            if len(batch_results) != len(batch_questions):
                logger.warning(f"Number of results ({len(batch_results)}) doesn't match number of questions in batch ({len(batch_questions)})")
                # Pad the results list if it's shorter than the questions list
                if len(batch_results) < len(batch_questions):
                    logger.warning(f"Padding results list with {len(batch_questions) - len(batch_results)} error placeholders")
                    for _ in range(len(batch_questions) - len(batch_results)):
                        batch_results.append({
                            'content': "Error: No result returned",
                            'usage': {},
                            'error': "No result returned"  # Add explicit error field
                        })
                # Truncate the results list if it's longer than the questions list
                elif len(batch_results) > len(batch_questions):
                    logger.warning(f"Truncating results list from {len(batch_results)} to {len(batch_questions)}")
                    batch_results = batch_results[:len(batch_questions)]

            # Process the results for this batch
            batch_responses = []
            for idx, (problem_id, question, result) in enumerate(zip(batch_problem_ids, batch_questions, batch_results)):
                try:
                    # Check if there's an error in the result
                    if 'error' in result:
                        # Create response with error information
                        error_response = {
                            'id': problem_id,
                            'question': question,
                            'error': result['error'],
                            'model': model_name,
                            'base': base_name,
                            'usage': result.get('usage', {})
                        }
                        # Add response content if available
                        if 'content' in result:
                            error_response['response'] = result['content']

                        # Add reasoning_content if it exists
                        if 'reasoning_content' in result:
                            error_response['reasoning_content'] = result['reasoning_content']

                        batch_responses.append(error_response)
                        logger.info(f"Processed error result for problem {problem_id} ({start_idx + idx + 1}/{len(questions_data)})")
                    else:
                        # Extract components for successful result
                        content = result.get('content', "Error: No content returned")
                        usage = result.get('usage', {})

                        # Create response dictionary without full_response
                        response = {
                            'id': problem_id,
                            'question': question,
                            'response': content,
                            'usage': usage,
                            'model': model_name,
                            'base': base_name
                        }

                        # Add reasoning_content if it exists
                        if 'reasoning_content' in result:
                            response['reasoning_content'] = result['reasoning_content']

                        batch_responses.append(response)
                        logger.info(f"Generated response for problem {problem_id} ({start_idx + idx + 1}/{len(questions_data)})")

                except Exception as e:
                    logger.error(f"Error processing result for problem {problem_id}: {e}")

                    # Save error information
                    error_response = {
                        'id': problem_id,
                        'question': question,
                        'error': str(e),
                        'model': model_name,
                        'base': base_name,
                        'usage': {}
                    }

                    batch_responses.append(error_response)

            # Add batch responses to all responses
            all_responses.extend(batch_responses)

            # Check if all items in the batch had errors
            all_errors = all('error' in resp for resp in batch_responses)
            if all_errors:
                consecutive_failed_batches += 1
                logger.warning(f"Batch {batch_idx + 1} had errors for all items. Consecutive failed batches: {consecutive_failed_batches}")

                # Check if we've reached the maximum number of consecutive failures
                if consecutive_failed_batches >= max_consecutive_failures and batch_idx < max_consecutive_failures:
                    error_msg = f"Terminating after {consecutive_failed_batches} consecutive batch failures. The model appears to be consistently failing."
                    logger.error(error_msg)

                    # Update metadata with termination reason
                    metadata['termination_reason'] = error_msg
                    if metadata_path:
                        update_metadata(metadata, metadata_path)

                    # Write the current responses to the output file
                    write_jsonl(all_responses, output_path)

                    # Raise an exception to terminate processing
                    raise RuntimeError(error_msg)
            else:
                # Reset the counter if a batch succeeds
                consecutive_failed_batches = 0
                logger.info(f"Batch {batch_idx + 1} had at least one successful response. Resetting consecutive failure counter.")

            # Save the current progress to the output file
            write_jsonl(all_responses, output_path)
            logger.info(f"Saved {len(all_responses)} responses to {output_path} after batch {batch_idx + 1}")

            # Update metadata if path is provided
            if metadata_path:
                metadata['statistics'] = calculate_statistics()
                update_metadata(metadata, metadata_path)

        except Exception as e:
            logger.error(f"Error processing batch {batch_idx + 1}: {e}")

            if no_fallback:
                logger.warning(f"Skipping batch {batch_idx + 1} due to error (fallback disabled)")

                # Add error responses for all questions in this batch
                for i, (problem_id, question) in enumerate(zip(batch_problem_ids, batch_questions)):
                    error_response = {
                        'id': problem_id,
                        'question': question,
                        'error': f"Batch processing failed: {str(e)}",
                        'model': model_name,
                        'base': base_name,
                        'usage': {}
                    }
                    all_responses.append(error_response)

                # Increment consecutive failed batches counter
                consecutive_failed_batches += 1
                logger.warning(f"Batch {batch_idx + 1} failed entirely. Consecutive failed batches: {consecutive_failed_batches}")

                # Check if we've reached the maximum number of consecutive failures
                if consecutive_failed_batches >= max_consecutive_failures and batch_idx < max_consecutive_failures:
                    error_msg = f"Terminating after {consecutive_failed_batches} consecutive batch failures. The model appears to be consistently failing."
                    logger.error(error_msg)

                    # Update metadata with termination reason
                    metadata['termination_reason'] = error_msg
                    if metadata_path:
                        update_metadata(metadata, metadata_path)

                    # Write the current responses to the output file
                    write_jsonl(all_responses, output_path)

                    # Raise an exception to terminate processing
                    raise RuntimeError(error_msg)

                # Save progress after the batch
                write_jsonl(all_responses, output_path)
                logger.info(f"Saved {len(all_responses)} responses to {output_path} after batch {batch_idx + 1}")

                # Update metadata if path is provided
                if metadata_path:
                    metadata['statistics'] = calculate_statistics()
                    update_metadata(metadata, metadata_path)
            else:
                # Fall back to individual processing for this batch
                logger.info(f"Falling back to individual processing for batch {batch_idx + 1}")

                # Start timing the fallback batch
                fallback_start_time = time.time()
                individual_times = []

                for i, (problem_id, question) in enumerate(zip(batch_problem_ids, batch_questions)):
                    # Start timing individual problem
                    problem_start_time = time.time()

                    logger.info(f"Processing problem {problem_id} ({start_idx + i + 1}/{len(questions_data)})")

                    try:
                        # Get model's answer (returns content, usage, and full response)
                        result = model.generate_response(question, question_type, retries, worker_logging)

                        # Check if there's an error in the result
                        if 'error' in result:
                            # Create response with error information
                            error_response = {
                                'id': problem_id,
                                'question': question,
                                'error': result['error'],
                                'model': model_name,
                                'base': base_name,
                                'usage': result.get('usage', {})
                            }
                            # Add response content if available
                            if 'content' in result:
                                error_response['response'] = result['content']

                            # Add reasoning_content if it exists
                            if 'reasoning_content' in result:
                                error_response['reasoning_content'] = result['reasoning_content']

                            all_responses.append(error_response)
                            logger.info(f"Processed error result for problem {problem_id}")
                        else:
                            # Extract components for successful result
                            content = result.get('content', "Error: No content returned")
                            usage = result.get('usage', {})

                            # Create response dictionary without full_response
                            response = {
                                'id': problem_id,
                                'question': question,
                                'response': content,
                                'usage': usage,
                                'model': model_name,
                                'base': base_name
                            }

                            # Add reasoning_content if it exists
                            if 'reasoning_content' in result:
                                response['reasoning_content'] = result['reasoning_content']

                            all_responses.append(response)

                            # Calculate and log individual problem time
                            problem_end_time = time.time()
                            problem_duration = problem_end_time - problem_start_time
                            individual_times.append(problem_duration)

                            # Calculate average time and estimate remaining time
                            avg_problem_time = mean(individual_times) if individual_times else 0
                            remaining_problems = len(batch_questions) - (i + 1)
                            estimated_remaining_time = avg_problem_time * remaining_problems

                            # Format times for logging
                            problem_duration_str = f"{problem_duration:.2f} seconds"
                            if problem_duration > 60:
                                problem_duration_str = f"{problem_duration/60:.2f} minutes"

                            remaining_time_str = f"{estimated_remaining_time:.2f} seconds"
                            if estimated_remaining_time > 60:
                                remaining_time_str = f"{estimated_remaining_time/60:.2f} minutes"
                                if estimated_remaining_time > 3600:
                                    remaining_time_str = f"{estimated_remaining_time/3600:.2f} hours"

                            logger.info(f"Generated response for problem {problem_id} in {problem_duration_str}")
                            if remaining_problems > 0:
                                logger.info(f"Estimated time for remaining {remaining_problems} problems in this batch: {remaining_time_str}")

                    except Exception as e:
                        logger.error(f"Error processing problem {problem_id}: {e}")

                        # Still track time even for errors
                        problem_end_time = time.time()
                        problem_duration = problem_end_time - problem_start_time
                        individual_times.append(problem_duration)
                        logger.info(f"Problem {problem_id} failed after {problem_duration:.2f} seconds")

                        # Save error information
                        error_response = {
                            'id': problem_id,
                            'question': question,
                            'error': str(e),
                            'model': model_name,
                            'base': base_name,
                            'usage': {}
                        }

                        all_responses.append(error_response)

                # Check if all individual items in the batch had errors
                batch_start_idx = len(all_responses) - len(batch_problem_ids)
                batch_end_idx = len(all_responses)
                batch_responses = all_responses[batch_start_idx:batch_end_idx]

                all_errors = all('error' in resp for resp in batch_responses)
                if all_errors:
                    consecutive_failed_batches += 1
                    logger.warning(f"Individual processing of batch {batch_idx + 1} had errors for all items. Consecutive failed batches: {consecutive_failed_batches}")

                    # Check if we've reached the maximum number of consecutive failures
                    if consecutive_failed_batches >= max_consecutive_failures and batch_idx < max_consecutive_failures:
                        error_msg = f"Terminating after {consecutive_failed_batches} consecutive batch failures. The model appears to be consistently failing."
                        logger.error(error_msg)

                        # Update metadata with termination reason
                        metadata['termination_reason'] = error_msg
                        if metadata_path:
                            update_metadata(metadata, metadata_path)

                        # Write the current responses to the output file
                        write_jsonl(all_responses, output_path)

                        # Raise an exception to terminate processing
                        raise RuntimeError(error_msg)
                else:
                    # Reset the counter if a batch succeeds
                    consecutive_failed_batches = 0
                    logger.info(f"Individual processing of batch {batch_idx + 1} had at least one successful response. Resetting consecutive failure counter.")

                # Calculate total time for fallback batch
                fallback_end_time = time.time()
                fallback_duration = fallback_end_time - fallback_start_time
                batch_times.append(fallback_duration)  # Add to batch times for overall estimation

                # Format time for logging
                fallback_duration_str = f"{fallback_duration:.2f} seconds"
                if fallback_duration > 60:
                    fallback_duration_str = f"{fallback_duration/60:.2f} minutes"
                    if fallback_duration > 3600:
                        fallback_duration_str = f"{fallback_duration/3600:.2f} hours"

                # Calculate average batch time and estimate remaining time
                avg_batch_time = mean(batch_times) if batch_times else 0
                remaining_batches = num_batches - (batch_idx + 1)
                estimated_remaining_time = avg_batch_time * remaining_batches

                # Format remaining time for logging
                remaining_time_str = f"{estimated_remaining_time:.2f} seconds"
                if estimated_remaining_time > 60:
                    remaining_time_str = f"{estimated_remaining_time/60:.2f} minutes"
                    if estimated_remaining_time > 3600:
                        remaining_time_str = f"{estimated_remaining_time/3600:.2f} hours"

                # Save progress after processing all individual problems in the batch
                write_jsonl(all_responses, output_path)
                logger.info(f"Fallback processing of batch {batch_idx + 1} completed in {fallback_duration_str}")
                logger.info(f"Saved {len(all_responses)} responses to {output_path} after individual processing of batch {batch_idx + 1}")

                if remaining_batches > 0:
                    logger.info(f"Estimated time for remaining {remaining_batches} batches: {remaining_time_str}")

                # Update metadata if path is provided
                if metadata_path:
                    metadata['statistics'] = calculate_statistics()
                    update_metadata(metadata, metadata_path)

    # Update final statistics
    processed_questions = len(questions_data)

    # Calculate final statistics
    final_stats = calculate_statistics()
    successful_responses = final_stats['successful_responses']
    error_responses = final_stats['error_responses']
    missing_questions = final_stats['missing_questions']

    # Add timing information to metadata
    if batch_times:
        timing_stats = {
            'total_batches': len(batch_times),
            'average_batch_time': mean(batch_times),
            'total_processing_time': sum(batch_times),
            'min_batch_time': min(batch_times),
            'max_batch_time': max(batch_times),
            'median_batch_time': median(batch_times) if len(batch_times) > 1 else batch_times[0]
        }
        metadata['timing'] = timing_stats

        # Log timing summary
        total_time = sum(batch_times)
        total_time_str = f"{total_time:.2f} seconds"
        if total_time > 60:
            total_time_str = f"{total_time/60:.2f} minutes"
            if total_time > 3600:
                total_time_str = f"{total_time/3600:.2f} hours"

        avg_time = mean(batch_times)
        avg_time_str = f"{avg_time:.2f} seconds"
        if avg_time > 60:
            avg_time_str = f"{avg_time/60:.2f} minutes"

        logger.info(f"Total processing time: {total_time_str}")
        logger.info(f"Average batch time: {avg_time_str}")

    # Update timestamp and statistics in metadata
    metadata['timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    metadata['statistics'] = final_stats

    # Write final metadata if path is provided
    if metadata_path:
        update_metadata(metadata, metadata_path)
        logger.info(f"Final metadata updated at {metadata_path}")

    logger.info(f"Processed all {processed_questions} problems. Total responses: {len(all_responses)}")
    logger.info(f"Statistics: {successful_responses} successful, {error_responses} errors, {missing_questions} missing")

    return all_responses, metadata

def main():
    parser = argparse.ArgumentParser(description="Generate responses for physics problems using LLMs")
    parser.add_argument("--base", type=str, required=True, help="Base model type (e.g., openai, together, deepseek, huggingface)")
    parser.add_argument("--model", type=str, required=True, help="Model to use (e.g., gpt4o, llama, mistral)")
    parser.add_argument("--data", type=str, default="PAC", help="Dataset name (e.g., PAC)")
    parser.add_argument("--type", type=str, default="OEQ", choices=["OEQ", "MCQ", "CODE"], help="Question type (OEQ or MCQ)")
    parser.add_argument("--retries", type=int, default=0, help="Number of retries if the first attempt fails (0 means try once, 1 means try once and retry once if it fails)")
    parser.add_argument("--parallel", type=int, default=4, help="Number of parallel processes to use")
    parser.add_argument("--worker-logging", action="store_true", help="Enable logging for worker processes")
    parser.add_argument("--max-tokens", type=int, default=2000, help="Maximum number of tokens in the response")
    parser.add_argument("--no-fallback", action="store_true", help="Disable fallback to individual processing when batch processing fails")
    parser.add_argument("--log-level", type=str, default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        help="Set the logging level (default: INFO)")
    # GPU configuration options (for local models only)
    parser.add_argument("--gpu", type=str, help="GPU device IDs to use (e.g., '0' or '0,1,2,3'). If not set, use all available GPUs.")

    args = parser.parse_args()

    # Get the project root directory (where this script is located)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))

    # Define paths relative to the project root
    data_path = os.path.join(project_root, "data", "processed", args.type, args.data, "dataset.jsonl")

    # Create output directory path based on question type, base, model, and max_tokens
    output_dir = os.path.join(project_root, "output", args.type, args.data, f"{args.base}-{args.model}-{args.max_tokens}")

    output_path = os.path.join(output_dir, "response.jsonl")

    # Create logs directory inside the output directory
    logs_dir = os.path.join(output_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    # Create a timestamped log file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(logs_dir, f"generation_{timestamp}.log")

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Set the log level based on the command-line argument
    log_level = getattr(logging, args.log_level)
    logging.getLogger().setLevel(log_level)

    # Add file handler for logging to the output directory
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    # Add file handler to the root logger to capture logs from all modules
    logging.getLogger().addHandler(file_handler)

    logger.info(f"Log level set to: {args.log_level}")

    # Log startup information
    gpu_info = f", gpu: {args.gpu}" if args.gpu is not None and args.base == "huggingface" else ""
    logger.info(f"Starting generation with base: {args.base}, model: {args.model}, data: {data_path}, output: {output_path}, type: {args.type}, retries: {args.retries}, parallel: {args.parallel}, max_tokens: {args.max_tokens}, worker_logging: {args.worker_logging}{gpu_info}")

    logger.info(f"Logs will be saved to: {log_path}")
    logger.info(f"All logs for this model can be found in: {logs_dir}")

    # Read dataset
    problems = read_jsonl(data_path)

    # Define metadata path
    metadata_path = os.path.join(output_dir, "metadata.json")

    # Process problems
    try:
        _ = process_problems(
            problems,
            args.model,
            output_path,
            args.base,
            args.type,
            args.data,
            args.retries,
            args.parallel,
            args.max_tokens,
            args.no_fallback,
            metadata_path,
            logs_dir,
            args.worker_logging,
            args.gpu
        )

        # Generation completed successfully
        logger.info(f"Metadata available at {metadata_path}")
        logger.info(f"Logs available in {logs_dir}")

        # Get the latest log file for reference
        latest_log = get_latest_log(logs_dir)
        if latest_log:
            logger.info(f"Latest log file: {latest_log}")

        logger.info("Generation completed successfully")
    except RuntimeError as e:
        # Handle the case where we terminate due to consecutive batch failures
        logger.error(f"Generation terminated early: {e}")
        logger.info(f"Partial results and metadata available at {output_dir}")
        logger.info(f"Logs available in {logs_dir}")

        # Get the latest log file for reference
        latest_log = get_latest_log(logs_dir)
        if latest_log:
            logger.info(f"Latest log file: {latest_log}")

        sys.exit(1)

if __name__ == "__main__":
    main()
