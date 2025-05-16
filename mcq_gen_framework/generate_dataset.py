import os
import json
import sys
import argparse
import importlib.util
import importlib
import types
from pathlib import Path

# Import Answer and NestedAnswer from local files
from answer import Answer, NestedAnswer

# Add the current directory to sys.path to allow importing question.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def parse_args():
    parser = argparse.ArgumentParser(description='Generate MCQ dataset')
    parser.add_argument('--dataset', type=str, choices=['main', 'extra', 'eph'], default='main',
                        help='Dataset type: main (questions 1-74), extra (questions 81-90), or eph (questions 91-104)')
    parser.add_argument('--instance_range', type=str, default='1-50',
                        help='Range of instances to generate, e.g., 1-10')
    parser.add_argument('--output_dir', type=str, default=None,
                        help='Output directory for the generated dataset (optional)')
    return parser.parse_args()

def validate_instance_range(instance_range):
    """Validate the instance range format and values."""
    if not instance_range or not isinstance(instance_range, str):
        raise ValueError("Instance range must be a non-empty string")

    if not instance_range.strip():
        raise ValueError("Instance range cannot be empty")

    parts = instance_range.split('-')
    if len(parts) != 2:
        raise ValueError("Instance range must be in format 'start-end', e.g., '1-10'")

    try:
        start = int(parts[0])
        end = int(parts[1])
    except ValueError:
        raise ValueError("Instance range must contain valid integers")

    if start < 1:
        raise ValueError("Start of range must be at least 1")

    if end < start:
        raise ValueError("End of range must be greater than or equal to start")

    return start, end

def main():
    args = parse_args()

    # Get the script directory and project paths
    script_dir = Path(os.path.abspath(__file__)).parent
    project_root = script_dir.parent.parent

    # Parse and validate instance range
    try:
        start_instance, end_instance = validate_instance_range(args.instance_range)
        instance_count = end_instance - start_instance + 1
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Define the output directories and files
    processed_dir = project_root / "processed" / "MCQ" / args.dataset
    processed_dir.mkdir(parents=True, exist_ok=True)
    # processed_file = processed_dir / f"dataset_{args.instance_range}.jsonl"

    local_output_dir = script_dir / "output"
    local_output_dir.mkdir(parents=True, exist_ok=True)
    local_output_file = local_output_dir / f"{args.dataset}_{args.instance_range}.jsonl"

    # If custom output directory is provided, use it
    custom_output_file = None
    if args.output_dir:
        custom_output_dir = Path(args.output_dir) / args.dataset
        custom_output_dir.mkdir(parents=True, exist_ok=True)
        custom_output_file = custom_output_dir / f"dataset_{args.instance_range}.jsonl"

    # Define the seed range
    start_seed = 999 + start_instance - 1
    end_seed = start_seed + instance_count

    # Dynamically import question classes based on dataset type
    question_classes = []
    question_ids = []

    # Define which question numbers to use based on dataset type
    if args.dataset == 'main':
        # Main dataset: questions 1-80 (excluding some)
        excluded_questions = [5, 7, 33, 43, 44, 53, 54, 57, 58, 62, 68, 73, 78]
        question_numbers = [i for i in range(1, 81) if i not in excluded_questions]
    elif args.dataset == 'extra':
        # Extra dataset: questions 81-90
        question_numbers = list(range(81, 105))

    # Import each question class dynamically
    for q_num in question_numbers:
        q_id = f"q{q_num}"
        question_ids.append(q_id)

        # Define the path to the question module
        if args.dataset == 'eph':
            q_module_path = script_dir / 'EPH' / q_id / f"{q_id}.py"
        else:
            q_module_path = script_dir / args.dataset / q_id / f"{q_id}.py"

        if not q_module_path.exists():
            print(f"Warning: Question module {q_module_path} not found, skipping.")
            question_ids.pop()  # Remove the ID we just added
            continue

        # Import the module dynamically
        if args.dataset == 'eph':
            # For EPH questions, we need to handle the relative imports
            # Read the file content and modify the imports
            with open(q_module_path, 'r') as f:
                code = f.read()

            # Replace relative imports with absolute imports
            code = code.replace('from ..question import Question', 'from question import Question')
            code = code.replace('from Questions.answer import Answer, NestedAnswer', 'from answer import Answer, NestedAnswer')

            # Create a temporary module
            module = types.ModuleType(q_id)

            # Add the module to sys.modules to allow relative imports
            sys.modules[q_id] = module

            # Execute the modified code in the module's namespace
            exec(code, module.__dict__)
        else:
            # For main and extra datasets, use the standard import
            spec = importlib.util.spec_from_file_location(q_id, q_module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

        # Get the Question class from the module
        class_name = f"Question{q_num}"
        if hasattr(module, class_name):
            question_classes.append(getattr(module, class_name))
        else:
            print(f"Warning: Class {class_name} not found in {q_module_path}, skipping.")
            question_ids.pop()  # Remove the ID we just added

    # Generate all questions for each instance
    data = []

    # First, generate all questions for each instance
    for instance_idx in range(start_instance, end_instance + 1):
        seed = 999 + instance_idx - 1

        for q_class, q_id in zip(question_classes, question_ids):
            unique_id = f"{q_id}_{instance_idx}"

            # Generate the question
            if instance_idx == 1:  # First instance is the original question
                question = q_class(unique_id=unique_id)
            else:
                question = q_class(unique_id=unique_id, seed=seed)

            # Add to data
            data.append({
                "id": f"MCQ_{q_id[1:]}_{instance_idx}",  # Format: MCQ_1_1, MCQ_2_1, etc.
                "problem": question.question(),
                "answer": question.answer(),
                "options": question.options_str_list(),
                "correct_option": question.correct_option(),
                "type": question.type,
                # "knowledge": question.knowledge if hasattr(question, "knowledge") else ""
            })

    # Sort data by instance first, then by question
    # This will give us q1_1, q2_1, ..., q74_1, q1_2, q2_2, ...
    data.sort(key=lambda x: (int(x["id"].split("_")[2]), int(x["id"].split("_")[1])))

    # Custom JSON encoder to handle Answer and NestedAnswer objects
    class AnswerEncoder(json.JSONEncoder):
        def default(self, obj):
            if hasattr(obj, '__class__') and obj.__class__.__name__ in ('Answer', 'NestedAnswer'):
                return str(obj)
            if isinstance(obj, list):
                return [self.default(item) for item in obj]
            return super().default(obj)

    # Write to JSONL files
    # First, write to the processed directory
    # with open(processed_file, 'w', encoding='utf-8') as f:
    #     for item in data:
    #         f.write(json.dumps(item, ensure_ascii=False, cls=AnswerEncoder) + '\n')

    # Then, write to the local output directory
    with open(local_output_file, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False, cls=AnswerEncoder) + '\n')

    # If a custom output directory was provided, write there too
    if custom_output_file:
        with open(custom_output_file, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False, cls=AnswerEncoder) + '\n')

    # Print output information
    print(f"Generated {len(data)} questions and saved to:")
    # print(f"- {processed_file}")
    print(f"- {local_output_file}")
    if custom_output_file:
        print(f"- {custom_output_file}")

if __name__ == "__main__":
    main()
