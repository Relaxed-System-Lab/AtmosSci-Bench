"""
Utility functions for the evaluate module.
"""

import re
import logging

logger = logging.getLogger(__name__)

def extract_boxed_content(text):
    """
    Extract content from \\boxed{} commands with properly balanced braces.

    Args:
        text (str): LaTeX text containing \\boxed{} commands

    Returns:
        list: List of contents of \\boxed{} commands
    """
    results = []
    i = 0
    while i < len(text):
        # Find the start of a \boxed command
        boxed_start = text.find('\\boxed{', i)
        if boxed_start == -1:
            break

        # Start after the opening brace
        content_start = boxed_start + 7  # len('\\boxed{')

        # Find the matching closing brace
        brace_count = 1
        content_end = content_start

        while content_end < len(text) and brace_count > 0:
            if text[content_end] == '{':
                brace_count += 1
            elif text[content_end] == '}':
                brace_count -= 1
            content_end += 1

        # If we found a matching closing brace
        if brace_count == 0:
            # Extract the content (excluding the closing brace)
            content = text[content_start:content_end-1]
            results.append(content)

        # Move past this \boxed command
        i = content_end

    return results

def extract_subquestions(text):
    """
    Extract subquestions from a problem text.

    Args:
        text (str): Problem text

    Returns:
        list: List of subquestion identifiers (e.g., ['a', 'b', 'c'])
    """
    # Look for common subquestion patterns like (a), a), a., etc.
    patterns = [
        r'\(([a-z])\)',  # (a), (b), etc.
        r'([a-z])\)',    # a), b), etc.
        r'([a-z])\.',    # a., b., etc.
        r'part\s+([a-z])', # part a, part b, etc.
        r'([a-z])\s*\)',  # a ), b ), etc.
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            # Convert to lowercase and remove duplicates while preserving order
            unique_matches = []
            for match in matches:
                match_lower = match.lower()
                if match_lower not in unique_matches:
                    unique_matches.append(match_lower)
            return unique_matches

    # If no subquestions found, return a single item with key 'a' instead of 'main'
    return ['a']

def extract_answers_from_latex(text):
    """
    Extract answers from LaTeX text, looking for common answer patterns.

    Args:
        text (str): LaTeX text containing answers

    Returns:
        dict: Dictionary mapping subquestion identifiers to answers
    """
    answers = {}

    # Try to find labeled answers like "(a) 47 mm, (b) 9.7 mm"
    labeled_answer_pattern = r'\(([a-z])\)\s*([^,(]*(?:\([^)]*\)[^,(]*)*)(?:,|\.|$)'
    labeled_matches = re.findall(labeled_answer_pattern, text, re.IGNORECASE)

    if labeled_matches:
        for subq, answer in labeled_matches:
            answers[subq.lower()] = answer.strip()
        return answers

    # Try to find boxed answers with subquestion labels
    # First find all labeled positions
    label_positions = []
    for match in re.finditer(r'\(([a-z])\)[:\s]*\\boxed{', text, re.IGNORECASE):
        label_positions.append((match.group(1).lower(), match.start(), match.end()))

    # If we found labeled boxed answers
    if label_positions:
        # Extract the content of each labeled boxed expression
        for i, (subq, _, boxed_start) in enumerate(label_positions):
            # Find the end of this boxed expression (or the start of the next one)
            next_start = len(text) if i == len(label_positions) - 1 else label_positions[i+1][1]

            # Extract the substring containing this boxed expression
            substring = text[boxed_start-7:next_start]  # Include '\boxed{' in the substring

            # Extract the boxed content with balanced braces
            boxed_contents = extract_boxed_content(substring)
            if boxed_contents:
                answers[subq] = boxed_contents[0].strip()

        if answers:  # If we successfully extracted any labeled boxed answers
            return answers

    # Try to find boxed answers with subquestion labels using regex (fallback)
    boxed_pattern = r'\(([a-z])\)[:\s]*\\boxed{(.*?)}'
    fallback_matches = re.findall(boxed_pattern, text, re.DOTALL)

    if fallback_matches:
        for subq, answer in fallback_matches:
            answers[subq.lower()] = answer.strip()
        return answers

    # Look for answers in a structured format like "Part (a): ... Part (b): ..."
    part_pattern = r'(?:part|question)\s*\(?([a-z])\)?[:\s]*(.*?)(?=(?:part|question)\s*\(?[a-z]\)?[:\s]|$)'
    part_matches = re.findall(part_pattern, text, re.IGNORECASE | re.DOTALL)

    if part_matches:
        for subq, answer in part_matches:
            answers[subq.lower()] = answer.strip()
        return answers

    # If no structured answers found, look for any boxed answers with properly balanced braces
    boxed_contents = extract_boxed_content(text)

    if boxed_contents:
        # If we have multiple boxed answers, treat them as separate subquestion answers
        for i, answer in enumerate(boxed_contents):
            # Use letters as subquestion IDs (a, b, c, ...)
            subq = chr(97 + i)  # 97 is ASCII for 'a'
            answers[subq] = answer.strip()
        return answers

    # If no boxed answers, look for final_answer sections
    final_answer_match = re.search(r'final_answer:\s*(.*?)(?:\n\n|$)', text, re.DOTALL)
    if final_answer_match:
        answers['a'] = final_answer_match.group(1).strip()
        return answers

    # If all else fails, use the last paragraph as the answer
    paragraphs = text.split('\n\n')
    if paragraphs:
        answers['a'] = paragraphs[-1].strip()

    return answers

def extract_expected_answers(text):
    """
    Extract expected answers from text, focusing on subquestion labels.
    Do NOT extract from \\boxed{} expressions.

    Args:
        text (str): Text containing expected answers

    Returns:
        dict: Dictionary mapping subquestion identifiers to answers
    """
    answers = {}

    # First, try to find answers in a format like "(a) answer (b) answer"
    # This pattern looks for subquestion labels followed by content up to the next subquestion label or end
    combined_pattern = r'\(([a-z])\)\s*(.*?)(?=\s*\([a-z]\)\s*|\s*$)'
    combined_matches = re.findall(combined_pattern, text, re.IGNORECASE | re.DOTALL)

    if combined_matches:
        for subq, answer in combined_matches:
            # Clean up the answer by removing trailing commas, periods, etc.
            clean_answer = re.sub(r'[,.]$', '', answer.strip())
            answers[subq.lower()] = clean_answer
        return answers

    # If the above pattern didn't work, try to find labeled answers like "(a) 47 mm, (b) 9.7 mm"
    labeled_answer_pattern = r'\(([a-z])\)\s*([^,(]*(?:\([^)]*\)[^,(]*)*)(?:,|\.|$)'
    labeled_matches = re.findall(labeled_answer_pattern, text, re.IGNORECASE)

    if labeled_matches:
        for subq, answer in labeled_matches:
            answers[subq.lower()] = answer.strip()
        return answers

    # Look for answers in a structured format like "Part (a): ... Part (b): ..."
    part_pattern = r'(?:part|question)\s*\(?([a-z])\)?[:\s]*(.*?)(?=(?:part|question)\s*\(?[a-z]\)?[:\s]|$)'
    part_matches = re.findall(part_pattern, text, re.IGNORECASE | re.DOTALL)

    if part_matches:
        for subq, answer in part_matches:
            answers[subq.lower()] = answer.strip()
        return answers

    # If no subquestions found, use the whole text as the 'a' answer (instead of 'main')
    if not answers:
        answers['a'] = text.strip()

    return answers

def extract_boxed_answers(response):
    """
    Extract ONLY \\boxed{} expressions from the model's response.

    Args:
        response (str): Model response

    Returns:
        dict: Dictionary mapping subquestion identifiers to answers
    """
    if not response:
        return {'a': ''}

    answers = {}

    # Extract all boxed content with properly balanced braces
    boxed_contents = extract_boxed_content(response)

    if boxed_contents:
        # Try to find labeled boxed answers
        label_positions = []
        for match in re.finditer(r'\(([a-z])\)[:\s]*\\boxed{', response, re.IGNORECASE):
            label_positions.append((match.group(1).lower(), match.end()))

        if label_positions:
            # Match labels with boxed contents
            for i, (subq, _) in enumerate(label_positions):
                if i < len(boxed_contents):
                    answers[subq] = boxed_contents[i].strip()
        else:
            # If no labels, assign sequential labels (a, b, c, ...)
            for i, content in enumerate(boxed_contents):
                subq = chr(97 + i)  # 97 is ASCII for 'a'
                answers[subq] = content.strip()

    # If no answers were found, return an empty dict
    return answers

def deduplicate_expected_answers(expected_answers):
    """
    Deduplicate expected answers by removing redundant entries with the same answer.

    Args:
        expected_answers (dict): Dictionary mapping subquestion IDs to expected answers

    Returns:
        dict: Deduplicated dictionary of expected answers
    """
    if not expected_answers:
        return {}

    # Create a reverse mapping from answers to IDs
    answer_to_ids = {}
    for subq_id, answer in expected_answers.items():
        if answer not in answer_to_ids:
            answer_to_ids[answer] = []
        answer_to_ids[answer].append(subq_id)

    # Create a deduplicated dictionary
    deduplicated = {}

    # Process each unique answer
    for answer, ids in answer_to_ids.items():
        # If there's only one ID for this answer, keep it as is
        if len(ids) == 1:
            deduplicated[ids[0]] = answer
        else:
            # If there are multiple IDs with the same answer, prioritize 'main' or the first alphabetical ID
            if 'main' in ids:
                deduplicated['main'] = answer
            else:
                # Sort IDs alphabetically and keep the first one
                ids.sort()
                deduplicated[ids[0]] = answer

    # If there's only one answer in the deduplicated dictionary and it has the key 'main',
    # change the key to 'a' as requested
    if len(deduplicated) == 1 and 'main' in deduplicated:
        answer = deduplicated.pop('main')
        deduplicated['a'] = answer

    return deduplicated
