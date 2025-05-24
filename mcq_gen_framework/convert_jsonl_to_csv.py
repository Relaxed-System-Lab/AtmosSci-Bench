#!/usr/bin/env python3
"""
Convert all JSONL files in data/harvard directory to CSV format.

This script reads all JSONL files in the data/harvard directory,
converts them to CSV format, and saves them with the same name
but with a .csv extension.
"""

import os
import json
import csv
import argparse
from pathlib import Path


def jsonl_to_csv(input_file, output_file):
    """
    Convert a JSONL file to CSV format.
    
    Args:
        input_file (str): Path to the input JSONL file
        output_file (str): Path to the output CSV file
    """
    print(f"Converting {input_file} to {output_file}...")
    
    # Read JSONL file
    data = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data.append(json.loads(line.strip()))
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON in {input_file}: {e}")
                continue
    
    if not data:
        print(f"No valid data found in {input_file}")
        return
    
    # Get all unique keys from all records
    fieldnames = set()
    for record in data:
        fieldnames.update(record.keys())
    
    # Sort fieldnames to ensure consistent column order
    fieldnames = sorted(fieldnames)
    
    # Write CSV file
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"Successfully converted {len(data)} records to {output_file}")


def convert_all_jsonl_files(input_dir, output_dir=None):
    """
    Convert all JSONL files in a directory to CSV format.
    
    Args:
        input_dir (str): Path to the directory containing JSONL files
        output_dir (str, optional): Path to the directory to save CSV files.
                                   If None, CSV files will be saved in the same directory.
    """
    # Create output directory if it doesn't exist
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Find all JSONL files in the input directory
    jsonl_files = list(Path(input_dir).glob('*.jsonl'))
    
    if not jsonl_files:
        print(f"No JSONL files found in {input_dir}")
        return
    
    print(f"Found {len(jsonl_files)} JSONL files in {input_dir}")
    
    # Convert each JSONL file to CSV
    for jsonl_file in jsonl_files:
        # Determine output file path
        if output_dir:
            output_file = os.path.join(output_dir, f"{jsonl_file.stem}.csv")
        else:
            output_file = os.path.join(input_dir, f"{jsonl_file.stem}.csv")
        
        # Convert JSONL to CSV
        jsonl_to_csv(str(jsonl_file), output_file)


def main():
    parser = argparse.ArgumentParser(description='Convert JSONL files to CSV format')
    parser.add_argument('--input-dir', default='output',
                        help='Directory containing JSONL files (default: output)')
    parser.add_argument('--output-dir', default=None,
                        help='Directory to save CSV files (default: same as input directory)')
    args = parser.parse_args()

    convert_all_jsonl_files(args.input_dir, args.output_dir)


if __name__ == "__main__":
    main()
