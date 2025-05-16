
import re

GENERAL_RE_PATTERNS = [
    r"[A,a][N,n][S,s][W,w][E,e][R,r]:?\s*[\*\[\{]*:?\s*([A-Da-d])[\*\[\}]*",  # Matches 'Answer: A', 'Answer: *A*'
    r"\\boxed\{([A-Da-d])\}",  # Matches '\boxed{C}'
    r"[O,o][P,p][T,t][I,i][O,o][N,n][S,s]?:?\s*[\*\[\{]*:?\s*([A-Da-d])[\*\[\}]*"
]


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
    print("NoAnswer:", respond[-20:])
    return "NoAnswer"

def get_original_precision_granularity(num):
    """
    get precision as same as the original questions.
    Calculate the granularity of a given number. Granularity is defined as the closest power 
    of 10 representing the number's magnitude. If the first digit of the number is less than 5, 
    the granularity is adjusted to granularity / 10.

    Examples:
        get_granularity(90)    -> 10   (Magnitude is 10^1, first digit is 9, no adjustment needed)
        get_granularity(3)     -> 0.1  (Magnitude is 10^0, first digit is 3, adjustment applied)
        get_granularity(1500)  -> 100 (Magnitude is 10^3, first digit is 1.5, no adjustment needed)
        get_granularity(0.5)   -> 0.1  (Magnitude is 10^-1, first digit is 5, no adjustment needed)
        get_granularity(0.05)  -> 0.01 (Magnitude is 10^-2, first digit is 5, no adjustment needed)
        get_granularity(0.1)  -> 0.01 (Magnitude is 10^-2, first digit is 5, no adjustment needed)

    Args:
        num (float or int): The input number.

    Returns:
        float: The granularity of the input number.
    """
    if num == 0:
        return 0  # Special case: 0 does not have a clear granularity.

    from math import floor, log10

    # Calculate the base granularity (10^magnitude)
    magnitude = floor(log10(abs(num)))
    granularity = 10 ** magnitude

    # Adjust if the first digit is less than 5
    first_digit = abs(num) / granularity
    if first_digit < 2:
        granularity /= 10

    return granularity
