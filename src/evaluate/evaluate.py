#!/usr/bin/env python
import os
import sys
import argparse
import json
import logging
import datetime
import ray

# Import evaluators
from src.evaluate.evaluators import QuantityEvaluator, ExpressionEvaluator, LLMEvaluator, MCQEvaluator
from src.evaluate.utils import (
    extract_subquestions,
    extract_boxed_answers,
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
    """Write data to a JSONL file."""
    try:
        # Create directories if needed
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
    """Update the metadata file with the latest statistics."""
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

def evaluate_response(expected_answers, actual_response, question_type="OEQ", tolerance=0.05,
                     disable_quantity=False, disable_expression=False, enable_llm=False, llm_batch=False):
    """
    Evaluate a single response using available evaluators.

    Args:
        expected_answers (dict): Dictionary mapping subquestion IDs to expected answers
        actual_response (str): The model's response
        question_type (str): Type of question (OEQ or MCQ)
        tolerance (float): Tolerance for numerical comparisons
        disable_quantity (bool): Whether to disable the QuantityEvaluator
        disable_expression (bool): Whether to disable the ExpressionEvaluator
        enable_llm (bool): Whether to enable the LLM-as-Judge Evaluator
        llm_batch (bool): Whether to skip LLM evaluation for batch processing later

    Returns:
        dict: Evaluation results
    """
    # Initialize evaluators based on which ones are enabled and the question type
    evaluators = []

    if question_type == "MCQ":
        # For MCQ questions, use the MCQEvaluator
        evaluators.append(MCQEvaluator(tolerance=tolerance))
    else:
        # For OEQ questions, use the standard evaluators
        if not disable_quantity:
            evaluators.append(QuantityEvaluator(tolerance=tolerance))

        if not disable_expression:
            evaluators.append(ExpressionEvaluator(tolerance=tolerance))

        # Only add LLM evaluator if enable_llm is True and llm_batch is False
        if enable_llm and not llm_batch:
            evaluators.append(LLMEvaluator(tolerance=tolerance))

    # Extract answers from the response based on question type
    if question_type == "MCQ":
        # For MCQ questions, extract the answer using the MCQEvaluator
        mcq_evaluator = MCQEvaluator(tolerance=tolerance)
        extracted_answer = mcq_evaluator.extract_mcq_answer(actual_response)
        extracted_answers = {'a': extracted_answer} if extracted_answer else {'a': None}
    else:
        # For OEQ questions, extract boxed answers
        extracted_answers = extract_boxed_answers(actual_response)

    # Create a mapping between expected and extracted answers
    answer_mapping = {}

    # First, try to match by subquestion ID
    for subq_id, expected_answer in expected_answers.items():
        if subq_id in extracted_answers:
            answer_mapping[subq_id] = extracted_answers[subq_id]

    # If some expected answers don't have a match, try to match by order
    unmatched_expected = [subq_id for subq_id in expected_answers if subq_id not in answer_mapping]
    unmatched_extracted = [subq_id for subq_id in extracted_answers if subq_id not in expected_answers]

    if unmatched_expected:
        # Sort unmatched expected and extracted answers by their IDs
        unmatched_expected.sort()
        unmatched_extracted.sort()

        # Match remaining answers in order
        for i, subq_id in enumerate(unmatched_expected):
            if i < len(unmatched_extracted):
                answer_mapping[subq_id] = extracted_answers[unmatched_extracted[i]]

    # Evaluate each subquestion
    subquestion_results = {}
    correct_count = 0
    total_count = 0

    for subq_id, expected_answer in expected_answers.items():
        if subq_id not in answer_mapping:
            # If the model didn't answer this subquestion, mark it as incorrect
            subquestion_results[subq_id] = {
                'is_correct': False,
                'expected_answer': expected_answer,
                'extracted_answer': None,
                'evaluator_results': []
            }
            total_count += 1
            continue

        actual_answer = answer_mapping[subq_id]

        # Try each evaluator in sequence
        evaluator_results = []
        is_correct = False

        for evaluator in evaluators:
            try:
                result = evaluator.evaluate(expected_answer, actual_answer)
                evaluator_results.append(result)
            except Exception as e:
                logger.warning(f"Error in {evaluator} evaluation: {e}")
                # Create a result with is_correct=None to indicate an error
                result = {
                    'is_correct': None,
                    'details': {
                        'evaluator': str(evaluator),
                        'expected': expected_answer,
                        'actual': actual_answer,
                        'error': str(e)
                    }
                }
                evaluator_results.append(result)

            # If any evaluator says it's correct, consider it correct
            if result['is_correct']:
                is_correct = True
                break

        subquestion_results[subq_id] = {
            'is_correct': is_correct,
            'expected_answer': expected_answer,
            'extracted_answer': actual_answer,
            'evaluator_results': evaluator_results
        }

        if is_correct:
            correct_count += 1
        total_count += 1

    # Calculate the score for this response
    score = correct_count / total_count if total_count > 0 else 0

    return {
        'subquestion_results': subquestion_results,
        'score': score,
        'correct_count': correct_count,
        'total_count': total_count,
        'answer_mapping': answer_mapping,
        'disabled_evaluators': {
            'quantity': disable_quantity,
            'expression': disable_expression,
            'llm': not enable_llm
        }
    }

@ray.remote
def evaluate_with_llm(expected, actual, model_name="gpt-4o-mini", tolerance=0.05):
    """
    Evaluate a single response using LLM evaluator in parallel.

    Args:
        expected (str): The expected answer
        actual (str): The actual answer
        model_name (str): The LLM model to use
        tolerance (float): Tolerance for numerical comparisons

    Returns:
        dict: Evaluation result
    """
    llm_evaluator = LLMEvaluator(model_name=model_name, tolerance=tolerance)
    try:
        return llm_evaluator.evaluate(expected, actual)
    except Exception as e:
        logger.warning(f"Error in LLM evaluation: {e}")
        return {
            'is_correct': None,
            'details': {
                'evaluator': str(llm_evaluator),
                'expected': expected,
                'actual': actual,
                'model': model_name,
                'explanation': None,
                'error': str(e)
            }
        }

def evaluate_responses(responses, expected_answers, question_type="OEQ", evaluation_path=None, results_path=None,
                      tolerance=0.05, disable_quantity=False, disable_expression=False, enable_llm=False, llm_parallelism=8):
    """
    Evaluate all model responses against expected answers.

    Simplified implementation with no recovery logic:
    1. First pass: Evaluate all problems with quantity and expression evaluators
    2. Second pass: Batch evaluate remaining problems with LLM evaluator in parallel
    3. Third pass: Collect statistics

    Args:
        responses (list): List of response dictionaries
        expected_answers (list): List of expected answer dictionaries
        question_type (str): Type of question (OEQ or MCQ)
        evaluation_path (str, optional): Path to save evaluation results
        results_path (str, optional): Path to save summary results
        tolerance (float): Tolerance for numerical comparisons
        disable_quantity (bool): Whether to disable the QuantityEvaluator
        disable_expression (bool): Whether to disable the ExpressionEvaluator
        enable_llm (bool): Whether to enable the LLM-as-Judge Evaluator
        llm_parallelism (int): Number of parallel LLM evaluations to run

    Returns:
        tuple: (results, accuracy)
    """
    logger.info(f"Starting evaluation of {len(responses)} responses")

    # Initialize results list and statistics
    results = []
    llm_evaluation_tasks = []

    # FIRST PASS: Evaluate all problems with quantity and expression evaluators
    logger.info("Starting first pass: Evaluating with quantity and expression evaluators")

    for response in responses:
        problem_id = response.get('id')
        question_data = response.get('question')
        model_response = response.get('response', '')

        logger.info(f"Processing problem {problem_id}")

        # Handle nested question structure
        if isinstance(question_data, dict):
            question = question_data.get('problem', '')
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

            results.append(result)
            continue

        # For MCQ questions, handle nested question structure in the expected answers
        if question_type == "MCQ" and isinstance(expected_answer_dict.get('question'), dict):
            nested_question = expected_answer_dict.get('question')

            # Extract the correct_option field if available
            if 'correct_option' in nested_question:
                expected_answer_dict['correct_option'] = nested_question['correct_option']

            # Extract the answer field if available
            if 'answer' in nested_question and 'answer' not in expected_answer_dict:
                expected_answer_dict['answer'] = nested_question['answer']

        # Extract subquestions from the problem text
        subquestions = extract_subquestions(question)

        # Extract expected answers for each subquestion
        expected_subquestion_answers = {}

        if question_type == "MCQ":
            # For MCQ questions, use the correct_option field if available
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
                    logger.warning(f"No correct_option or answer field found for MCQ problem {problem_id}")
                    continue
        else:
            # For OEQ questions, use the standard approach
            if 'answer' in expected_answer_dict:
                # If there's a single answer field, extract subquestion answers from it
                answer_text = expected_answer_dict['answer']
                expected_subquestion_answers = extract_expected_answers(answer_text)
            elif 'answers' in expected_answer_dict:
                # If there's an answers dictionary, use it directly
                expected_subquestion_answers = expected_answer_dict['answers']
            else:
                logger.warning(f"No answer field found for problem {problem_id}")
                continue

        # If no subquestion answers were found, use the subquestions from the problem text
        if not expected_subquestion_answers or (len(expected_subquestion_answers) == 1 and 'main' in expected_subquestion_answers):
            if 'answer' in expected_answer_dict:
                # Assign the same answer to all subquestions
                for subq in subquestions:
                    expected_subquestion_answers[subq] = expected_answer_dict['answer']

        # Deduplicate expected answers to avoid redundancy
        expected_subquestion_answers = deduplicate_expected_answers(expected_subquestion_answers)

        # For OEQ questions with LLM evaluation, use a two-pass approach
        if question_type == "OEQ" and enable_llm:
            # First pass: Evaluate with quantity and expression evaluators only
            evaluation = evaluate_response(
                expected_subquestion_answers,
                model_response,
                question_type=question_type,
                tolerance=tolerance,
                disable_quantity=disable_quantity,
                disable_expression=disable_expression,
                enable_llm=False,  # Skip LLM evaluation in first pass
                llm_batch=True     # Mark for batch LLM evaluation
            )

            # Store problem info for LLM evaluation in second pass
            # For OEQ, if a subquestion is not correct, add it to LLM evaluation tasks
            for subq_id, subq_result in evaluation['subquestion_results'].items():
                if not subq_result['is_correct']:
                    # This subquestion needs LLM evaluation
                    llm_evaluation_tasks.append({
                        'problem_id': problem_id,
                        'subq_id': subq_id,
                        'expected': subq_result['expected_answer'],
                        'actual': subq_result['extracted_answer']
                    })
        else:
            # For MCQ questions or OEQ without LLM, evaluate normally
            evaluation = evaluate_response(
                expected_subquestion_answers,
                model_response,
                question_type=question_type,
                tolerance=tolerance,
                disable_quantity=disable_quantity,
                disable_expression=disable_expression,
                enable_llm=enable_llm
            )

        # Extract all answers for easier access
        if question_type == "MCQ":
            # For MCQ questions, extract the answer using the MCQEvaluator
            mcq_evaluator = MCQEvaluator(tolerance=tolerance)
            extracted_answer = mcq_evaluator.extract_mcq_answer(model_response)
            extracted_answers = {'a': extracted_answer} if extracted_answer else {'a': None}
        else:
            # For OEQ questions, extract boxed answers
            extracted_answers = extract_boxed_answers(model_response)

        # Create a clean, organized result structure
        subquestions = []

        # Process each subquestion
        for subq_id, subq_result in evaluation['subquestion_results'].items():
            # Get evaluator results based on question type
            if question_type == "MCQ":
                mcq_result = next((r for r in subq_result['evaluator_results'] if r['details']['evaluator'] == 'MCQEvaluator'), None)

                # Create a clean subquestion result
                subq_data = {
                    'id': subq_id,
                    'is_correct': subq_result['is_correct'],
                    'expected_answer': subq_result['expected_answer'],
                    'extracted_answer': subq_result['extracted_answer'],
                    'evaluations': {}
                }

                # Include MCQ evaluator results
                if mcq_result:
                    subq_data['evaluations']['mcq'] = {
                        'is_correct': mcq_result['is_correct'],
                        'expected': mcq_result['details']['expected'],
                        'extracted': mcq_result['details']['actual'],
                        'error': mcq_result['details']['error'] if 'error' in mcq_result['details'] else None
                    }
            else:
                # For OEQ questions, get the standard evaluator results
                quantity_result = next((r for r in subq_result['evaluator_results'] if r['details']['evaluator'] == 'QuantityEvaluator'), None)
                expression_result = next((r for r in subq_result['evaluator_results'] if r['details']['evaluator'] == 'ExpressionEvaluator'), None)
                llm_result = next((r for r in subq_result['evaluator_results'] if r['details']['evaluator'] == 'LLMEvaluator'), None)

                # Create a clean subquestion result
                # For OEQ with LLM enabled, don't set is_correct to true until after LLM evaluation
                is_correct = subq_result['is_correct']
                if question_type == "OEQ" and enable_llm and not is_correct:
                    # If we need LLM evaluation, set is_correct to null for now
                    is_correct = None

                subq_data = {
                    'id': subq_id,
                    'is_correct': is_correct,
                    'expected_answer': subq_result['expected_answer'],
                    'extracted_answer': subq_result['extracted_answer'],
                    'evaluations': {}
                }

                # Only include enabled evaluators in the results
                if quantity_result and not disable_quantity:
                    subq_data['evaluations']['quantity'] = {
                        'is_correct': quantity_result['is_correct'],
                        'error': quantity_result['details']['error'] if 'error' in quantity_result['details'] else None
                    }

                if expression_result and not disable_expression:
                    subq_data['evaluations']['expression'] = {
                        'is_correct': expression_result['is_correct'],
                        'error': expression_result['details']['error'] if 'error' in expression_result['details'] else None
                    }

                if llm_result and enable_llm:
                    subq_data['evaluations']['llm'] = {
                        'is_correct': llm_result['is_correct'],
                        'explanation': llm_result['details']['explanation'] if 'explanation' in llm_result['details'] else None,
                        'error': llm_result['details']['error'] if 'error' in llm_result['details'] else None
                    }

            subquestions.append(subq_data)

        # For OEQ with LLM enabled, recalculate score based on non-null is_correct values
        correct_count = evaluation['correct_count']
        total_count = evaluation['total_count']
        score = evaluation['score']

        if question_type == "OEQ" and enable_llm:
            # Only count subquestions with non-null is_correct values
            valid_subqs = [sq for sq in subquestions if sq['is_correct'] is not None]
            correct_subqs = [sq for sq in valid_subqs if sq['is_correct']]

            if valid_subqs:
                correct_count = len(correct_subqs)
                total_count = len(valid_subqs)
                score = correct_count / total_count if total_count > 0 else 0
            else:
                # If all subquestions need LLM evaluation, set score to null
                correct_count = 0
                total_count = 0
                score = None

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
            'score': score,
            'correct_count': correct_count,
            'total_count': total_count
        }

        results.append(result)

    # SECOND PASS: Batch evaluate with LLM in parallel (only for OEQ with LLM enabled)
    if question_type == "OEQ" and enable_llm and llm_evaluation_tasks:
        logger.info(f"Starting second pass: Batch LLM evaluation for {len(llm_evaluation_tasks)} subquestions")

        # Remove duplicate tasks (same problem_id and subq_id)
        unique_tasks = {}
        for task in llm_evaluation_tasks:
            task_key = (task['problem_id'], task['subq_id'])
            unique_tasks[task_key] = task

        # Convert back to list
        deduplicated_tasks = list(unique_tasks.values())

        logger.info(f"Processing {len(deduplicated_tasks)} LLM evaluation tasks (after deduplication)")

        # Process LLM evaluation tasks in batches
        total_tasks = len(deduplicated_tasks)
        total_batches = (total_tasks + llm_parallelism - 1) // llm_parallelism  # Ceiling division

        logger.info(f"Processing {total_tasks} LLM evaluation tasks in {total_batches} batches of {llm_parallelism}")

        all_llm_results = []
        for batch_idx in range(total_batches):
            start_idx = batch_idx * llm_parallelism
            end_idx = min(start_idx + llm_parallelism, total_tasks)
            batch_tasks = deduplicated_tasks[start_idx:end_idx]

            logger.info(f"Processing batch {batch_idx+1}/{total_batches} with {len(batch_tasks)} tasks")

            # Submit batch of LLM evaluation tasks in parallel
            llm_futures = []
            for task in batch_tasks:
                llm_futures.append(
                    evaluate_with_llm.remote(
                        task['expected'],
                        task['actual'],
                        model_name="gpt-4o-mini",
                        tolerance=tolerance
                    )
                )

            # Wait for this batch of LLM evaluations to complete
            logger.info(f"Waiting for batch {batch_idx+1} LLM evaluations to complete")
            batch_results = ray.get(llm_futures)
            logger.info(f"Completed batch {batch_idx+1} with {len(batch_results)} LLM evaluations")

            # Add batch results to all results
            all_llm_results.extend(batch_results)

        # Map results back to problems
        for i, task in enumerate(deduplicated_tasks):
            llm_result = all_llm_results[i]
            problem_id = task['problem_id']
            subq_id = task['subq_id']

            # Find the problem in results
            for result in results:
                if result['id'] == problem_id:
                    # Find the subquestion
                    for subq in result['evaluation']:
                        if subq['id'] == subq_id:
                            # Add LLM evaluation result
                            subq['evaluations']['llm'] = {
                                'is_correct': llm_result['is_correct'],
                                'explanation': llm_result['details']['explanation'] if 'explanation' in llm_result['details'] else None,
                                'error': llm_result['details']['error'] if 'error' in llm_result['details'] else None
                            }

                            # Update is_correct based on LLM result
                            subq['is_correct'] = llm_result['is_correct']

                            # Update the overall score for this problem
                            # Recalculate correct count and score
                            correct_count = sum(1 for sq in result['evaluation'] if sq['is_correct'])
                            total_count = len(result['evaluation'])
                            result['correct_count'] = correct_count
                            result['score'] = correct_count / total_count if total_count > 0 else 0
                            break
                    break

    # THIRD PASS: Collect statistics
    logger.info("Starting third pass: Collecting statistics")

    # Calculate overall accuracy
    total_score = 0
    total_problems = 0

    # Calculate statistics for each evaluator type
    evaluator_stats = {
        'quantity': {'true': 0, 'false': 0, 'null': 0},
        'expression': {'true': 0, 'false': 0, 'null': 0},
        'llm': {'true': 0, 'false': 0, 'null': 0},
        'mcq': {'true': 0, 'false': 0, 'null': 0}
    }

    # Add accuracy stats
    accuracy_stats = {'true': 0, 'false': 0, 'null': 0}

    # Count the number of true, false, and null results for each evaluator
    for result in results:
        # Update total score and problems count
        if result.get('score') is not None:
            total_score += result['score']
            total_problems += 1

            # Update accuracy stats
            if result['score'] > 0:
                accuracy_stats['true'] += 1
            else:
                accuracy_stats['false'] += 1
        else:
            accuracy_stats['null'] += 1

        # Process each subquestion
        for subq in result.get('evaluation', []):
            for eval_type, eval_result in subq.get('evaluations', {}).items():
                if eval_result.get('is_correct') is True:
                    evaluator_stats[eval_type]['true'] += 1
                elif eval_result.get('is_correct') is False:
                    evaluator_stats[eval_type]['false'] += 1
                else:  # is_correct is None
                    evaluator_stats[eval_type]['null'] += 1

    # Calculate overall accuracy (only for problems with non-null scores)
    accuracy = total_score / total_problems if total_problems > 0 else 0

    # Count problems with null scores (waiting for LLM evaluation)
    null_score_problems = accuracy_stats['null']

    if null_score_problems > 0:
        logger.info(f"Overall accuracy: {accuracy:.4f} ({total_score:.2f}/{total_problems}) - {null_score_problems} problems waiting for LLM evaluation")
    else:
        logger.info(f"Overall accuracy: {accuracy:.4f} ({total_score:.2f}/{total_problems})")

    # Log evaluator statistics
    for eval_type, stats in evaluator_stats.items():
        total = stats['true'] + stats['false'] + stats['null']
        if total > 0:
            correct_rate = stats['true'] / total if total > 0 else 0
            logger.info(f"{eval_type} evaluator: {correct_rate:.4f} ({stats['true']}/{total}) - true: {stats['true']}, false: {stats['false']}, null: {stats['null']}")

    # Log accuracy statistics
    total_accuracy = accuracy_stats['true'] + accuracy_stats['false'] + accuracy_stats['null']
    logger.info(f"Accuracy stats - total: {total_accuracy}, true: {accuracy_stats['true']}, false: {accuracy_stats['false']}, null: {accuracy_stats['null']}")

    # Create a summary results object
    summary_results = {
        'total_questions': total_problems,
        'average_score': accuracy,
        'evaluator_stats': evaluator_stats,
        'accuracy_stats': accuracy_stats,
        'pending_llm_evaluation': null_score_problems
    }

    # Write the evaluation results to the evaluation.jsonl file
    if evaluation_path:
        write_jsonl(results, evaluation_path, mode='w')
        logger.info(f"Wrote {len(results)} results to {evaluation_path}")

    # Write the summary results to the results.json file
    if results_path:
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(summary_results, f, indent=2)
        logger.info(f"Wrote summary results to {results_path}")

    return results, accuracy

def main():
    parser = argparse.ArgumentParser(description="Evaluate model responses for physics problems")
    parser.add_argument("--base", type=str, required=True, help="Base model type (e.g., openai, together, deepseek, huggingface)")
    parser.add_argument("--model", type=str, required=True, help="Model name (e.g., gpt4o, llama, mistral)")
    parser.add_argument("--data", type=str, default="PAC", help="Dataset name (e.g., PAC)")
    parser.add_argument("--type", type=str, default="OEQ", choices=["OEQ", "MCQ"], help="Question type (OEQ or MCQ)")
    parser.add_argument("--max-tokens", type=int, default=2000, help="Maximum number of tokens in the response")
    parser.add_argument("--tolerance", type=float, default=0.05, help="Tolerance for numerical comparisons")

    # Evaluator settings
    parser.add_argument("--disable-quantity", action="store_true", help="Disable the QuantityEvaluator")
    parser.add_argument("--disable-expression", action="store_true", help="Disable the ExpressionEvaluator")
    parser.add_argument("--enable-llm", action="store_true", help="Enable the LLM-as-Judge Evaluator")
    parser.add_argument("--llm-parallelism", type=int, default=16, help="Number of parallel LLM evaluations to run")

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

    # Initialize Ray for parallel processing if LLM evaluation is enabled
    if args.enable_llm:
        logger.info(f"Initializing Ray for parallel LLM evaluation with {args.llm_parallelism} workers")
        ray.init(ignore_reinit_error=True, num_cpus=args.llm_parallelism)

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
            question_type=args.type,
            evaluation_path=evaluation_path,
            results_path=results_path,
            tolerance=args.tolerance,
            disable_quantity=args.disable_quantity,
            disable_expression=args.disable_expression,
            enable_llm=args.enable_llm,
            llm_parallelism=args.llm_parallelism
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

        # Create a list of enabled evaluators
        enabled_evaluators = []
        if args.type == "MCQ":
            # For MCQ questions, always include the MCQEvaluator
            enabled_evaluators.append('MCQEvaluator')
        else:
            # For OEQ questions, include the standard evaluators
            if not args.disable_quantity:
                enabled_evaluators.append('QuantityEvaluator')
            if not args.disable_expression:
                enabled_evaluators.append('ExpressionEvaluator')
            if args.enable_llm:
                enabled_evaluators.append({'name': 'LLMEvaluator', 'model': 'gpt-4o-mini'})

        # Add evaluation information to metadata
        metadata['evaluation'] = {
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'accuracy': accuracy,
            'tolerance': args.tolerance,
            'evaluators': enabled_evaluators,
            'disabled_evaluators': {
                'quantity': args.type == "MCQ" or args.disable_quantity,
                'expression': args.type == "MCQ" or args.disable_expression,
                'llm': args.type == "MCQ" or not args.enable_llm,
                'mcq': args.type != "MCQ"
            }
        }

        # Update metadata file
        update_metadata(metadata, metadata_path)
    except Exception as e:
        logger.error(f"Error updating metadata: {e}")

    logger.info(f"Evaluation completed. Evaluation results saved to {evaluation_path}")
    logger.info(f"Summary results saved to {results_path}")
    logger.info(f"Overall accuracy: {accuracy:.4f}")

if __name__ == "__main__":
    main()
