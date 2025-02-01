import re
import pandas as pd
import sys

# from ..Question.utils import GENERAL_RE_PATTERNS, extract_option


def extract_option(respond, patterns):
    """
    Extract the last answer in the reply based on multiple patterns.

    Parameters:
        respond (str): The response string to extract the answer from.
        patterns (list of str): List of regex patterns to match possible answers.

    Returns:
        str: The extracted answer (A-D) or 'NoAnswer' if no match is found.
    """
    for pattern in patterns:
        matches = list(re.finditer(pattern, respond))
        if matches:
            last_match = matches[-1]
            answer = last_match.group(1).strip()
            return answer.upper()
    return "NoAnswer"

def check_and_update_answers(input_file, output_file):
    """
    Reads a CSV file, checks and updates LLM responses, and saves the results to a new file.

    Parameters:
        input_file (str): Path to the input CSV file.
        output_file (str): Path to the output CSV file.
    """
    # Load the CSV file
    df = pd.read_csv(input_file)

    GENERAL_RE_PATTERNS = [
        r"[A,a][N,n][S,s][W,w][E,e][R,r]:?\s*[\*\[\{]*:?\s*([A-Da-d])[\*\[\}]*",  # Matches 'Answer: A', 'Answer: *A*'
        r"\\boxed\{([A-Da-d])\}",  # Matches '\boxed{C}'
        r"[O,o][P,p][T,t][I,i][O,o][N,n][S,s]?:?\s*[\*\[\{]*:?\s*([A-Da-d])[\*\[\}]*"
    ]

    # Iterate through the dataframe and update fields
    for index, row in df.iterrows():
        llm_respond = row.get("llm_respond", "")
        llm_answer = extract_option(llm_respond, GENERAL_RE_PATTERNS)

        # Update llm_answer and NoAnswer
        df.at[index, "llm_answer"] = llm_answer
        df.at[index, "NoAnswer"] = llm_answer == "NoAnswer"
        # (llm_answer == "Error") or
        df.at[index, "Error"] = (llm_respond == "Error") or (llm_respond == "E") or (llm_respond == "r") or (llm_respond == "o") or (llm_respond == "e") or (len(llm_respond) < 10 and llm_answer == "NoAnswer")
        # respond < 8 but llm_answer may be correct; for example, "Answer: A"

        # Update correct if llm_answer is not NoAnswer
        if llm_answer != "NoAnswer" and llm_answer != "Error":
            df.at[index, "correct"] = llm_answer == row.get("correct_option", "")

    # Save the updated dataframe to a new file
    df.to_csv(output_file, index=False)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python check_answers.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    check_and_update_answers(input_file, output_file)
