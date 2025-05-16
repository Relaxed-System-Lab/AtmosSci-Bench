#!/usr/bin/env python
import os
import sys
import argparse
import json
import logging
import datetime

# Import evaluators - only MCQEvaluator for MCQ and CODE
from src.evaluate.evaluators import MCQEvaluator
from src.evaluate.utils import (
    extract_subquestions,
    extract_expected_answers,
    deduplicate_expected_answers
)

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
        logger.info(f"Successfully loaded {len(data)} items from {file_path}")
        return data
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}")
        raise

def write_jsonl(data, file_path, mode='w'):
    """
    Write data to a JSONL file.

    Args:
        data: List of items to write
        file_path: Path to the output file
        mode: File open mode ('w' for write/overwrite, 'a' for append)
    """
    try:
        # Only create directories if the file_path has a directory component
        dirname = os.path.dirname(file_path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)

        # Write the data
        with open(file_path, mode, encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps(item) + '\n')

        logger.info(f"Successfully wrote {len(data)} items to {file_path} (mode: {mode})")
    except Exception as e:
        logger.error(f"Error writing data to {file_path}: {e}")
        raise

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

def get_latest_log(logs_dir):
    """
    Get the path to the latest log file in the logs directory.

    Args:
        logs_dir (str): Path to the logs directory

    Returns:
        str: Path to the latest log file, or None if no logs exist
    """
    try:
        log_files = [os.path.join(logs_dir, f) for f in os.listdir(logs_dir) if f.startswith("evaluation_") and f.endswith(".log")]
        if not log_files:
            return None
        # Sort by modification time (newest first)
        log_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        return log_files[0]
    except Exception as e:
        logger.error(f"Error getting latest log file: {e}")
        return None

def evaluate_response(expected_answers, actual_response, question_type="MCQ", tolerance=0.05):
    """
    Evaluate a single response using MCQEvaluator.

    Args:
        expected_answers (dict): Dictionary mapping subquestion IDs to expected answers
        actual_response (str): The model's response
        question_type (str): Type of question (MCQ or CODE)
        tolerance (float): Tolerance for numerical comparisons

    Returns:
        dict: Evaluation results
    """
    # Initialize MCQ evaluator
    mcq_evaluator = MCQEvaluator(tolerance=tolerance)

    # Extract the answer using the MCQEvaluator
    extracted_answer = mcq_evaluator.extract_mcq_answer(actual_response)
    logger.debug(f"Extracted MCQ answer: {extracted_answer}")

    # Create a dictionary with a single answer
    extracted_answers = {'a': extracted_answer} if extracted_answer else {'a': None}

    logger.debug(f"Extracted answers: {extracted_answers}")

    # Create a mapping between expected and extracted answers
    answer_mapping = {}

    # First, try to match by subquestion ID
    logger.debug(f"Matching answers by subquestion ID")
    for subq_id, expected_answer in expected_answers.items():
        if subq_id in extracted_answers:
            answer_mapping[subq_id] = extracted_answers[subq_id]
            logger.debug(f"Matched subquestion {subq_id} by ID")

    # If some expected answers don't have a match, try to match by order
    unmatched_expected = [subq_id for subq_id in expected_answers if subq_id not in answer_mapping]
    unmatched_extracted = [subq_id for subq_id in extracted_answers if subq_id not in expected_answers]

    if unmatched_expected:
        logger.debug(f"Some expected answers don't have a match: {unmatched_expected}")
        logger.debug(f"Unmatched extracted answers: {unmatched_extracted}")

        # Sort unmatched expected and extracted answers by their IDs
        unmatched_expected.sort()
        unmatched_extracted.sort()
        logger.debug(f"Sorted unmatched expected: {unmatched_expected}")
        logger.debug(f"Sorted unmatched extracted: {unmatched_extracted}")

        # Match remaining answers in order
        for i, subq_id in enumerate(unmatched_expected):
            if i < len(unmatched_extracted):
                answer_mapping[subq_id] = extracted_answers[unmatched_extracted[i]]
                logger.debug(f"Matched subquestion {subq_id} with extracted answer {unmatched_extracted[i]} by order")

    # Evaluate each subquestion
    logger.info(f"Starting evaluation of {len(expected_answers)} subquestions")
    logger.debug(f"Final answer mapping: {answer_mapping}")

    subquestion_results = {}
    correct_count = 0
    total_count = 0

    for subq_id, expected_answer in expected_answers.items():
        logger.debug(f"Evaluating subquestion {subq_id}")
        logger.debug(f"Expected answer: {expected_answer}")

        if subq_id not in answer_mapping:
            # If the model didn't answer this subquestion, mark it as incorrect
            logger.info(f"Subquestion {subq_id} has no matching answer, marking as incorrect")
            subquestion_results[subq_id] = {
                'is_correct': False,
                'expected_answer': expected_answer,
                'extracted_answer': None,
                'evaluator_results': []
            }
            total_count += 1
            continue

        actual_answer = answer_mapping[subq_id]
        logger.debug(f"Actual answer: {actual_answer}")

        # Evaluate with MCQEvaluator
        try:
            result = mcq_evaluator.evaluate(expected_answer, actual_answer)
            is_correct = result['is_correct']

            if is_correct:
                logger.info(f"Subquestion {subq_id} marked as correct")
                correct_count += 1
            else:
                logger.debug(f"Subquestion {subq_id} marked as incorrect")

        except Exception as e:
            logger.warning(f"Error in MCQEvaluator evaluation: {e}")
            # Create a result with is_correct=None to indicate an error
            result = {
                'is_correct': None,
                'details': {
                    'evaluator': str(mcq_evaluator),
                    'expected': expected_answer,
                    'actual': actual_answer,
                    'error': str(e)
                }
            }
            is_correct = False

        subquestion_results[subq_id] = {
            'is_correct': is_correct,
            'expected_answer': expected_answer,
            'extracted_answer': actual_answer,
            'evaluator_results': [result]
        }

        total_count += 1

    # Calculate the score for this response
    score = correct_count / total_count if total_count > 0 else 0

    return {
        'subquestion_results': subquestion_results,
        'score': score,
        'correct_count': correct_count,
        'total_count': total_count,
        'answer_mapping': answer_mapping
    }

def evaluate_responses(responses, expected_answers, question_type="MCQ", evaluation_path=None, results_path=None, tolerance=0.05, remove_duplicate=False):
    """
    Evaluate all model responses against expected answers.

    Args:
        responses (list): List of response dictionaries
        expected_answers (list): List of expected answer dictionaries
        question_type (str): Type of question (MCQ or CODE)
        evaluation_path (str, optional): Path to save evaluation results
        results_path (str, optional): Path to save summary results
        tolerance (float): Tolerance for numerical comparisons
        remove_duplicate (bool): Whether to remove duplicate questions from evaluation.jsonl

    Returns:
        tuple: (results, accuracy)
    """
    results = []
    total_score = 0
    total_problems = 0

    # # Step 1: Remove duplicates from evaluation.jsonl if requested and file exists
    # if remove_duplicate and evaluation_path and os.path.exists(evaluation_path):
    #     try:
    #         # Read existing evaluation results
    #         existing_data = read_jsonl(evaluation_path)
    #         logger.info(f"Read {len(existing_data)} existing results from {evaluation_path}")

    #         # Create a dictionary to store unique results (by problem ID)
    #         unique_results = {}
    #         for item in existing_data:
    #             problem_id = item.get('id')
    #             if problem_id:
    #                 unique_results[problem_id] = item

    #         # Write the deduplicated results back to the file
    #         deduplicated_data = list(unique_results.values())
    #         write_jsonl(deduplicated_data, evaluation_path, mode='w')
    #         logger.info(f"Removed duplicates from {evaluation_path}, now contains {len(deduplicated_data)} unique results")
    #     except Exception as e:
    #         logger.error(f"Error removing duplicates from evaluation file: {e}")

    # Process each problem
    for response in responses:
        problem_id = response.get('id')
        question_data = response.get('question')
        model_response = response.get('response', '')

        # Debug logging
        logger.info(f"Processing problem {problem_id}")

        # Handle nested question structure
        if isinstance(question_data, dict):
            question = question_data.get('problem', '')
            logger.info(f"Found nested question structure, extracted problem field")
        else:
            question = question_data

        # Find the expected answer dictionary
        expected_answer_dict = next((item for item in expected_answers if item.get('id') == problem_id), None)

        if not expected_answer_dict:
            logger.warning(f"No expected answer found for problem {problem_id}")

            # Create a placeholder result for problems without expected answers
            result = {
                'id': problem_id,
                'question': question_data,
                'response': model_response,
                'expected_answers': {},
                'extracted_answers': {},
                'evaluation': [],
                'score': 0,
                'correct_count': 0,
                'total_count': 0,
                'error': "No expected answer found in dataset"
            }

            # Add to results
            results.append(result)
            continue

        # Debug logging
        logger.info(f"Expected answer dict: {expected_answer_dict.keys()}")

        # Handle nested question structure in the expected answers
        if isinstance(expected_answer_dict.get('question'), dict):
            nested_question = expected_answer_dict.get('question')
            logger.info(f"Found nested question structure in expected answers")

            # Extract the correct_option field if available
            if 'correct_option' in nested_question:
                expected_answer_dict['correct_option'] = nested_question['correct_option']
                logger.info(f"Extracted correct_option: {nested_question['correct_option']}")

            # Extract the answer field if available
            if 'answer' in nested_question and 'answer' not in expected_answer_dict:
                expected_answer_dict['answer'] = nested_question['answer']
                logger.info(f"Extracted answer: {nested_question['answer']}")

        # Extract subquestions from the problem text
        subquestions = extract_subquestions(question)

        # Extract expected answers for each subquestion
        expected_subquestion_answers = {}

        # For MCQ/CODE questions, use the correct_option field if available
        if 'correct_option' in expected_answer_dict:
            expected_subquestion_answers['a'] = expected_answer_dict['correct_option']
        else:
            # If there's no correct_option field, try to use the answer field
            if 'answer' in expected_answer_dict:
                answer_text = expected_answer_dict['answer']
                # Try to extract the option letter from the answer
                mcq_evaluator = MCQEvaluator()
                extracted_option = mcq_evaluator.extract_mcq_answer(answer_text)
                if extracted_option:
                    expected_subquestion_answers['a'] = extracted_option
                else:
                    # If we can't extract an option, just use the answer as is
                    expected_subquestion_answers['a'] = answer_text
            else:
                logger.warning(f"No correct_option or answer field found for problem {problem_id}")
                continue

        # Deduplicate expected answers to avoid redundancy
        expected_subquestion_answers = deduplicate_expected_answers(expected_subquestion_answers)
        logger.debug(f"Deduplicated expected answers: {expected_subquestion_answers}")

        # Evaluate the response
        evaluation = evaluate_response(
            expected_subquestion_answers,
            model_response,
            question_type=question_type,
            tolerance=tolerance
        )

        # Extract the answer using the MCQEvaluator
        mcq_evaluator = MCQEvaluator(tolerance=tolerance)
        extracted_answer = mcq_evaluator.extract_mcq_answer(model_response)
        extracted_answers = {'a': extracted_answer} if extracted_answer else {'a': None}

        # Create a clean, organized result structure
        subquestions = []

        # Process each subquestion
        for subq_id, subq_result in evaluation['subquestion_results'].items():
            # Get MCQ evaluator results
            mcq_result = next((r for r in subq_result['evaluator_results'] if r['details']['evaluator'] == 'MCQEvaluator'), None)

            # Create a clean subquestion result
            subq_data = {
                'id': subq_id,
                'is_correct': subq_result['is_correct'],
                'expected_answer': subq_result['expected_answer'],
                'extracted_answer': subq_result['extracted_answer'],
                'evaluations': {}
            }

            # print(mcq_result)

            # Include MCQ evaluator results
            if mcq_result:
                subq_data['evaluations']['mcq'] = {
                    'is_correct': mcq_result['is_correct'],
                    'expected': mcq_result['details']['expected'],
                    'extracted': mcq_result['details']['extracted'],
                    'error': mcq_result['details']['error'] if 'error' in mcq_result['details'] else None
                }

            subquestions.append(subq_data)

        # Add to results with the new order
        result = {
            # First: id, question, and response
            'id': problem_id,
            'question': question,
            'response': model_response,

            # Second: expected_answers and extracted_answers
            'expected_answers': expected_subquestion_answers,
            'extracted_answers': extracted_answers,

            # Third: evaluation (renamed from subquestions)
            'evaluation': subquestions,

            # Last: score and counts
            'score': evaluation['score'],
            'correct_count': evaluation['correct_count'],
            'total_count': evaluation['total_count']
        }

        # Add to results
        results.append(result)

        # Update totals
        total_score += evaluation['score']
        total_problems += 1

        logger.info(f"Problem {problem_id} score: {evaluation['score']:.2f} ({evaluation['correct_count']}/{evaluation['total_count']} correct)")



    # Calculate overall accuracy
    accuracy = total_score / total_problems if total_problems > 0 else 0
    logger.info(f"Overall accuracy: {accuracy:.4f} ({total_score:.2f}/{total_problems})")

    # Calculate statistics for MCQ evaluator
    evaluator_stats = {
        'mcq': {'true': 0, 'false': 0, 'null': 0}
    }

    # Add accuracy stats
    accuracy_stats = {'true': 0, 'false': 0, 'null': 0}

    # Count the number of true, false, and null results for MCQ evaluator
    for result in results:
        # Update accuracy stats
        if result.get('score') is not None:
            if result['score'] > 0:
                accuracy_stats['true'] += 1
            else:
                accuracy_stats['false'] += 1
        else:
            accuracy_stats['null'] += 1

        for subq in result['evaluation']:
            for eval_type, eval_result in subq['evaluations'].items():
                if eval_result['is_correct'] is True:
                    evaluator_stats[eval_type]['true'] += 1
                elif eval_result['is_correct'] is False:
                    evaluator_stats[eval_type]['false'] += 1
                else:  # is_correct is None
                    evaluator_stats[eval_type]['null'] += 1

    # Create a summary results object
    summary_results = {
        'total_questions': total_problems,
        'average_score': accuracy,
        'evaluator_stats': evaluator_stats,
        'accuracy_stats': accuracy_stats
    }

    # Write the evaluation results to the evaluation.jsonl file if provided
    if evaluation_path:
        write_jsonl(results, evaluation_path, mode='w')
        logger.info(f"Wrote {len(results)} results to {evaluation_path}")

    # Write the summary results to the results.json file if provided
    if results_path:
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(summary_results, f, indent=2)
        logger.info(f"Wrote summary results to {results_path}")

    return results, accuracy

def main():
    parser = argparse.ArgumentParser(description="Evaluate model responses for MCQ and CODE problems")
    parser.add_argument("--base", type=str, required=True, help="Base model type (e.g., openai, together, deepseek, huggingface)")
    parser.add_argument("--model", type=str, required=True, help="Model name (e.g., gpt4o, llama, mistral)")
    parser.add_argument("--data", type=str, default="PAC", help="Dataset name (e.g., PAC)")
    parser.add_argument("--type", type=str, default="MCQ", choices=["MCQ", "CODE"], help="Question type (MCQ or CODE)")
    parser.add_argument("--max-tokens", type=int, default=2000, help="Maximum number of tokens in the response")
    parser.add_argument("--tolerance", type=float, default=0.05, help="Tolerance for numerical comparisons")

    # Data processing settings
    parser.add_argument("--remove-duplicate", action="store_true", default=True, help="Remove duplicate questions from the dataset before processing")

    # Logging settings
    parser.add_argument("--log-level", type=str, default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        help="Set the logging level (default: INFO)")

    args = parser.parse_args()

    # Get the project root directory (where this script is located)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))

    # Define paths relative to the project root
    data_path = os.path.join(project_root, "data", "processed", args.type, args.data, "dataset.jsonl")

    # Create output directory path based on question type, base, model, and max_tokens
    output_dir = os.path.join(project_root, "output", args.type, args.data, f"{args.base}-{args.model}-{args.max_tokens}")

    # Create logs directory inside the output directory
    logs_dir = os.path.join(output_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    # Create a timestamped log file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(logs_dir, f"evaluation_{timestamp}.log")

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    response_path = os.path.join(output_dir, "response.jsonl")
    evaluation_path = os.path.join(output_dir, "evaluation.jsonl")
    results_path = os.path.join(output_dir, "results.json")
    metadata_path = os.path.join(output_dir, "metadata.json")

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
    logger.info(f"Starting evaluation for base: {args.base}, model: {args.model}, data: {args.data}, type: {args.type}, max_tokens: {args.max_tokens}")
    logger.info(f"Logs will be saved to: {log_path}")
    logger.info(f"All logs for this model can be found in: {logs_dir}")

    # Read dataset and responses
    try:
        expected_answers = read_jsonl(data_path)
        responses = read_jsonl(response_path)
    except Exception as e:
        logger.error(f"Error reading input files: {e}")
        sys.exit(1)

    # Evaluate responses
    try:
        results, accuracy = evaluate_responses(
            responses,
            expected_answers,
            question_type=args.type,          # Pass the question type
            evaluation_path=evaluation_path,  # Pass the evaluation path
            results_path=results_path,        # Pass the results path for summary statistics
            tolerance=args.tolerance,
            remove_duplicate=args.remove_duplicate  # Pass the remove_duplicate parameter
        )
    except Exception as e:
        logger.error(f"Error during evaluation: {e}")
        sys.exit(1)

    # Create or update metadata
    try:
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
        else:
            metadata = {}

        # Calculate evaluator-specific statistics
        evaluator_stats = {'MCQEvaluator': {'correct': 0, 'total': 0}}

        # Initialize accuracy stats
        accuracy_stats = {'true': 0, 'false': 0, 'null': 0}

        for result in results:
            # Update accuracy stats based on the overall score
            if result.get('score') is not None:
                if result['score'] > 0:
                    accuracy_stats['true'] += 1
                else:
                    accuracy_stats['false'] += 1
            else:
                accuracy_stats['null'] += 1

            for subq_data in result['evaluation']:
                # Count MCQEvaluator results
                if 'evaluations' in subq_data and 'mcq' in subq_data['evaluations']:
                    evaluator_stats['MCQEvaluator']['total'] += 1
                    if subq_data['evaluations']['mcq']['is_correct']:
                        evaluator_stats['MCQEvaluator']['correct'] += 1

        # Calculate accuracy for MCQEvaluator
        if evaluator_stats['MCQEvaluator']['total'] > 0:
            evaluator_stats['MCQEvaluator']['accuracy'] = evaluator_stats['MCQEvaluator']['correct'] / evaluator_stats['MCQEvaluator']['total']
        else:
            evaluator_stats['MCQEvaluator']['accuracy'] = 0.0

        # Add evaluation information to metadata
        metadata['evaluation'] = {
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'accuracy': accuracy,
            'tolerance': args.tolerance,
            'evaluators': ['MCQEvaluator'],
            'evaluator_stats': evaluator_stats,
            'accuracy_stats': accuracy_stats
        }

        # Update metadata file
        update_metadata(metadata, metadata_path)
    except Exception as e:
        logger.error(f"Error updating metadata: {e}")

    # Get the latest log file for reference
    latest_log = get_latest_log(logs_dir)
    if latest_log:
        logger.info(f"Latest log file: {latest_log}")

    logger.info(f"Evaluation completed. Evaluation results saved to {evaluation_path}")
    logger.info(f"Summary results saved to {results_path}")
    logger.info(f"Overall accuracy: {accuracy:.4f}")

    # Log evaluator-specific statistics
    if 'evaluation' in metadata and 'evaluator_stats' in metadata['evaluation']:
        stats = metadata['evaluation']['evaluator_stats']
        for evaluator, eval_stats in stats.items():
            if eval_stats['total'] > 0:
                logger.info(f"{evaluator} accuracy: {eval_stats['accuracy']:.4f} ({eval_stats['correct']}/{eval_stats['total']})")
            else:
                logger.info(f"{evaluator} was not used in any evaluations")

    # Log accuracy statistics
    if 'evaluation' in metadata and 'accuracy_stats' in metadata['evaluation']:
        acc_stats = metadata['evaluation']['accuracy_stats']
        total = acc_stats['true'] + acc_stats['false'] + acc_stats['null']
        logger.info(f"Accuracy stats - total: {total}, true: {acc_stats['true']}, false: {acc_stats['false']}, null: {acc_stats['null']}")

if __name__ == "__main__":
    main()
