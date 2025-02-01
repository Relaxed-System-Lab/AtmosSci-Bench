from openai import OpenAI
import os
import ray
import time
import json

# MAX_NEW_TOKEN = 8192
# MAX_NEW_TOKEN = 1024


def deepseek_reasoner_init(max_new_token):
    ray.init(ignore_reinit_error=True)

    return (max_new_token)

def deepseek_reasoner_prompt(question, options):
    return f"""
You are a Earth Science Expert answering multiple-choice questions.
Here is the question: {question}
Here are the options:
{options}

Instructions:
1. Carefully analyze the question and options provided.
2. Please think step by step. Use logical reasoning and critical thinking to generate a detailed explanation or steps leading to the answer.
3. At the end of your response, ensure to provide the correct option (A/B/C/D) on a new line in the following format strictly:
Answer: [Correct Option(A/B/C/D)]
    """
def fetch_response(prompt, max_new_token):
    from dotenv import load_dotenv
    load_dotenv()

    respond = ""
    try_count = 0

    # for backward compatibility, you can still use `https://api.deepseek.com/v1` as `base_url`.
    client = OpenAI(
        api_key=os.environ.get("DeepSeek_API_KEY"),
        base_url="https://api.deepseek.com"
    )

    time.sleep(60)

    while respond == "" and try_count < 1:
        try_count += 1
        chat_completion = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=[{"role": "user", "content": prompt}],
            stream=False,
            max_tokens=max_new_token
            # temperature=0.7
        )
        # max_tokens (max output tokens) Default: 4K 4096 (https://api-docs.deepseek.com/zh-cn/quick_start/pricing)
        # temperature: default 1

        respond = chat_completion.choices[0].message.content
        reasoning_content = chat_completion.choices[0].message.reasoning_content

        prompt_tokens = chat_completion.usage.prompt_tokens
        completion_tokens = chat_completion.usage.completion_tokens
        reasoning_tokens = chat_completion.usage.completion_tokens_details.reasoning_tokens
        total_tokens = chat_completion.usage.total_tokens
        usages = {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "reasoning_tokens": reasoning_tokens,
            "total_tokens": total_tokens
        }

    return (respond, reasoning_content, usages)


def deepseek_reasoner(llm_config, prompts, question_ids):
    max_new_token = llm_config[0]
    time_start = time.time()
    error = ""

    futures = [ray.remote(fetch_response).remote(prompt, max_new_token) for prompt in prompts]
    ray_responses = ray.get(futures)

    time_end = time.time()

    # Extract a single letter as the correct answer
    pattern = r"Answer:\s*([A-Da-d])"

    err_list = []
    for res, id in zip(ray_responses, question_ids):
        if res[0] == "":
            err_list.append(id)

    responses = [res[0] for res in ray_responses]
    reasoning_contents = [res[1] for res in ray_responses]
    usages = [res[2] for res in ray_responses]

    if err_list:
        error = f"Error: Get empty responds in question ids: {err_list}"

    metadata = {
        "model": "deepseek_reasoner",
        "infer_time": time_end - time_start,
        "error": error,
        "max_new_tokens": max_new_token,
        "usages": usages
    }

    return responses, pattern, metadata, usages, reasoning_contents
