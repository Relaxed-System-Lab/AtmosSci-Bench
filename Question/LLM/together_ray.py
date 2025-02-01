from openai import OpenAI
import os
import ray
import time
import json
from together import Together



# MAX_NEW_TOKEN = 8192
# MAX_NEW_TOKEN = 30000
# MAX_NEW_TOKEN = 7300


def together_ray_init(model_name, max_new_token):
    ray.init(ignore_reinit_error=True)

    return (model_name, max_new_token)

def together_ray_prompt(question, options):
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
def fetch_response(prompt, model_name, max_new_token):
    from dotenv import load_dotenv
    load_dotenv()

    respond = ""
    try_count = 0

    # for backward compatibility, you can still use `https://api.deepseek.com/v1` as `base_url`.
    client = Together(api_key=os.environ.get("TOGETHER_API_KEY"))

    while respond == "" and try_count < 1:
        try_count += 1

        if "gemma" in model_name:
            # `inputs` tokens + `max_new_tokens` must be <= 8193
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens = 6000
            )
        else:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_new_token,
            )

        # print(response.choices[0].message.content)
        usages = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        }

        respond = response.choices[0].message.content
        print("len(respond):", len(respond))
        # reasoning_content = chat_completion.choices[0].message.reasoning_content


    return (respond, "", usages)


def together_ray(llm_config, prompts, question_ids):
    model_name = llm_config[0]
    max_new_token = llm_config[1]

    time_start = time.time()
    error = ""

    futures = [ray.remote(fetch_response).remote(prompt, model_name, max_new_token) for prompt in prompts]
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
        "model": model_name,
        "infer_time": time_end - time_start,
        "error": error,
        "max_new_tokens": max_new_token,
        "usages": usages
    }

    return responses, pattern, metadata, usages, reasoning_contents
