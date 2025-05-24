#!/usr/bin/env python
import os
import sys
import argparse
import subprocess
import logging
import time
import signal
import atexit
from concurrent.futures import ProcessPoolExecutor

# Global list to track all running processes
all_processes = []

# Function to terminate all running processes
def terminate_all_processes():
    """Terminate all running processes when the script exits."""
    if all_processes:
        logger.info(f"Terminating {len(all_processes)} running processes...")
        for process, dataset in all_processes:
            if process.poll() is None:  # Check if process is still running
                try:
                    logger.info(f"Terminating process for dataset: {dataset}")
                    process.terminate()
                    # Give it a moment to terminate gracefully
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # If it doesn't terminate gracefully, kill it
                    logger.warning(f"Process for {dataset} did not terminate gracefully, killing it")
                    process.kill()
                except Exception as e:
                    logger.error(f"Error terminating process for {dataset}: {e}")

# Signal handler for graceful termination
def signal_handler(sig, frame):
    """Handle termination signals by cleaning up processes."""
    logger.info(f"Received signal {sig}, terminating all processes...")
    terminate_all_processes()
    sys.exit(1)

# Setup logging
def setup_logging(log_dir=None, log_level=logging.INFO):
    """
    Set up logging with both console and file output.

    Args:
        log_dir (str): Directory to store log files. If None, logs will only go to console.
        log_level (int): Logging level (e.g., logging.INFO, logging.DEBUG)

    Returns:
        str: Path to the log file if created, None otherwise
    """
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create handlers list with console handler
    handlers = [logging.StreamHandler()]

    log_file_path = None

    # Add file handler if log_dir is specified
    if log_dir:
        # Make sure log_dir is an absolute path
        if not os.path.isabs(log_dir):
            # Get the project root directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(script_dir))
            log_dir = os.path.join(project_root, log_dir)

        # Create log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)

        # Create a timestamped log file name
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        log_file_name = f"parallel_run_{timestamp}.log"
        log_file_path = os.path.join(log_dir, log_file_name)

        # Create file handler
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

    return log_file_path

# Initialize logger (will be properly configured in main)
logger = logging.getLogger(__name__)

# Dataset information with approximate question counts
DATASET_INFO = {
    "MCQ/eph_1-10": 140,
    "MCQ/extra_1-10": 100,
    "MCQ/main_1-10": 670,
    "OEQ/PAC": 113,
    "OEQ/HHSWP": 208,
    "OEQ/FPOP": 70
}

def get_dataset_path(dataset, project_root):
    """Get the path to the dataset JSONL file."""
    question_type, dataset_name = dataset.split('/')
    return os.path.join(project_root, "data", "processed", question_type, dataset_name, "dataset.jsonl")

def count_questions(dataset_path):
    """Count the actual number of questions in a dataset."""
    try:
        with open(dataset_path, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    except Exception as e:
        logger.error(f"Error counting questions in {dataset_path}: {e}")
        return 0

def split_gpus(gpu_str, num_groups):
    """Split GPU IDs into groups."""
    if not gpu_str:
        # Auto-detect GPUs if not specified
        import torch
        num_gpus = torch.cuda.device_count()
        if num_gpus == 0:
            logger.warning("No GPUs detected.")
            return []
        gpu_ids = list(range(num_gpus))
    else:
        gpu_ids = [int(x.strip()) for x in gpu_str.split(',')]

    num_gpus = len(gpu_ids)
    if num_gpus < num_groups:
        logger.warning(f"Requested {num_groups} GPU groups but only {num_gpus} GPUs available. Reducing groups to {num_gpus}.")
        num_groups = num_gpus

    # Calculate GPUs per group
    gpus_per_group = num_gpus // num_groups
    remainder = num_gpus % num_groups

    # Create GPU groups
    gpu_groups = []
    start_idx = 0
    for i in range(num_groups):
        # Add one extra GPU to the first 'remainder' groups
        group_size = gpus_per_group + (1 if i < remainder else 0)
        end_idx = start_idx + group_size
        group = gpu_ids[start_idx:end_idx]
        gpu_groups.append(','.join(str(x) for x in group))
        start_idx = end_idx

    return gpu_groups

def split_datasets(datasets, num_groups, project_root):
    """Split datasets into groups based on question counts."""
    # Get actual question counts
    dataset_counts = {}
    for dataset in datasets:
        dataset_path = get_dataset_path(dataset, project_root)
        count = count_questions(dataset_path)
        if count == 0:
            # Fall back to predefined counts if file can't be read
            count = DATASET_INFO.get(dataset, 0)
            logger.warning(f"Using predefined count for {dataset}: {count}")
        dataset_counts[dataset] = count

    # Sort datasets by count (descending)
    sorted_datasets = sorted(dataset_counts.items(), key=lambda x: x[1], reverse=True)

    # Initialize groups
    groups = [[] for _ in range(num_groups)]
    group_counts = [0] * num_groups

    # Distribute datasets using a greedy approach
    for dataset, count in sorted_datasets:
        # Find the group with the smallest total count
        min_idx = group_counts.index(min(group_counts))
        groups[min_idx].append(dataset)
        group_counts[min_idx] += count

    # Log the distribution
    for i, (group, count) in enumerate(zip(groups, group_counts)):
        logger.info(f"Group {i+1}: {count} questions - {group}")

    return groups

def run_generate_script(args):
    """Run the generate.py script with the given arguments."""
    # Unpack arguments (log_dir is only used for the main script, not passed to child processes)
    gpu_group, datasets, base, model, max_tokens, retries, parallel, log_level, worker_logging, no_fallback, _ = args

    logger.info(f"Processing {len(datasets)} datasets sequentially on GPU group: {gpu_group}")

    # Process each dataset sequentially within this GPU group
    for dataset in datasets:
        question_type, dataset_name = dataset.split('/')

        cmd = [
            "python3", "-m", "src.generate.generate",
            "--base", base,
            "--model", model,
            "--data", dataset_name,
            "--type", question_type,
            "--max-tokens", str(max_tokens),
            "--retries", str(retries),
            "--parallel", str(parallel),
            "--log-level", log_level,
            "--gpu", gpu_group
        ]

        # We don't pass the log directory to child processes
        # They will use their default log paths

        if worker_logging:
            cmd.append("--worker-logging")

        if no_fallback:
            cmd.append("--no-fallback")

        logger.info(f"Starting dataset {dataset} on GPU group {gpu_group}")
        logger.info(f"Running command: {' '.join(cmd)}")

        try:
            # Start the process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            # Add to global list for cleanup
            all_processes.append((process, dataset))

            # Wait for this process to complete before starting the next one
            logger.info(f"Waiting for dataset {dataset} to complete on GPU group {gpu_group}...")
            stdout, stderr = process.communicate()

            # Log the output to our log file
            if stdout:
                logger.debug(f"STDOUT for {dataset} on GPU group {gpu_group}:\n{stdout}")

            if process.returncode != 0:
                logger.error(f"Process for {dataset} failed with code {process.returncode}")
                logger.error(f"STDERR for {dataset} on GPU group {gpu_group}:\n{stderr}")
            else:
                logger.info(f"Process for {dataset} completed successfully on GPU group {gpu_group}")
                if stderr:
                    logger.debug(f"STDERR for {dataset} on GPU group {gpu_group} (non-error):\n{stderr}")

            # Remove from global list since it's completed
            all_processes.remove((process, dataset))

        except Exception as e:
            logger.error(f"Error processing dataset {dataset} on GPU group {gpu_group}: {e}")

    return True

def main():
    # Register signal handlers for graceful termination
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Termination signal

    # Register cleanup function to run at exit
    atexit.register(terminate_all_processes)

    logger.info("Process termination handlers registered. All subprocesses will be terminated if the script exits.")

    parser = argparse.ArgumentParser(description="Run generate.py in parallel with multiple GPU groups for local models. Each GPU group processes its datasets sequentially.")
    parser.add_argument("--base", type=str, default="huggingface", help="Base model type (must be huggingface)")
    parser.add_argument("--model", type=str, required=True, help="Model to use (e.g., Qwen2.5-72B-GeoGPT)")
    parser.add_argument("--datasets", type=str, nargs='+', help="List of datasets to process (e.g., OEQ/PAC MCQ/main_1-10)")
    parser.add_argument("--gpu", type=str, help="GPU device IDs to use (e.g., '0,1,2,3,4,5,6,7'). If not set, use all available GPUs.")
    parser.add_argument("--gpu-parallel", type=int, default=2, help="Number of GPU groups for parallel processing")
    parser.add_argument("--max-tokens", type=int, default=2000, help="Maximum number of tokens in the response")
    parser.add_argument("--retries", type=int, default=0, help="Number of retries if the first attempt fails")
    parser.add_argument("--parallel", type=int, default=4, help="Number of parallel processes to use per GPU group")
    parser.add_argument("--log-level", type=str, default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help="Set the logging level")
    parser.add_argument("--worker-logging", action="store_true", help="Enable logging for worker processes")
    parser.add_argument("--no-fallback", action="store_true", help="Disable fallback to individual processing when batch processing fails")
    parser.add_argument("--log-dir", type=str, default="parallel_log", help="Directory to store logs for this script only (default: parallel_log)")

    args = parser.parse_args()

    # Set up logging with file output
    log_level = getattr(logging, args.log_level)

    # Get absolute path for log directory
    log_dir = args.log_dir
    if not os.path.isabs(log_dir):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(script_dir))
        log_dir = os.path.join(project_root, log_dir)

    logger.info(f"Using log directory: {log_dir}")
    log_file_path = setup_logging(log_dir, log_level)

    if log_file_path:
        logger.info(f"Logs will be saved to: {log_file_path}")

    # Verify that base is huggingface
    if args.base != "huggingface":
        logger.error("This script only works with huggingface models. Please use --base huggingface")
        sys.exit(1)

    # Get the project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))

    # Use all available datasets if none specified
    if not args.datasets:
        args.datasets = list(DATASET_INFO.keys())
        logger.info(f"No datasets specified, using all available: {args.datasets}")

    # Split GPUs into groups
    gpu_groups = split_gpus(args.gpu, args.gpu_parallel)
    if not gpu_groups:
        logger.error("No GPU groups created. Exiting.")
        sys.exit(1)

    logger.info(f"Created {len(gpu_groups)} GPU groups: {gpu_groups}")

    # Split datasets into groups
    dataset_groups = split_datasets(args.datasets, len(gpu_groups), project_root)

    # Prepare arguments for each GPU group
    process_args = []
    for gpu_group, dataset_group in zip(gpu_groups, dataset_groups):
        process_args.append((
            gpu_group,
            dataset_group,
            args.base,
            args.model,
            args.max_tokens,
            args.retries,
            args.parallel,
            args.log_level,
            args.worker_logging,
            args.no_fallback,
            args.log_dir
        ))

    # Run generate.py in parallel for each GPU group
    # Each GPU group will process its datasets sequentially
    start_time = time.time()
    logger.info(f"Starting parallel execution with {len(gpu_groups)} GPU groups")
    logger.info(f"Each GPU group will process its datasets SEQUENTIALLY")

    with ProcessPoolExecutor(max_workers=len(gpu_groups)) as executor:
        list(executor.map(run_generate_script, process_args))

    end_time = time.time()
    total_time = end_time - start_time

    logger.info(f"All processes completed in {total_time:.2f} seconds")

if __name__ == "__main__":
    main()
