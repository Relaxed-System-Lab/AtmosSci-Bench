# from openai import OpenAI
import os
import ray
import time
import json
# from together import Together
import requests
# import json
# import os


# MAX_NEW_TOKEN = 8192
# MAX_NEW_TOKEN = 30000
# MAX_NEW_TOKEN = 7300


def fireworks_ray_init(model_name, max_new_token):
    ray.init(ignore_reinit_error=True)

    return (model_name, max_new_token)

def fireworks_ray_prompt(question, options):
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

    url = "https://api.fireworks.ai/inference/v1/chat/completions"
    payload = {
        "model": model_name,
        "max_tokens": max_new_token,
        # "top_p": 1,
        # "top_k": 40,
        # "presence_penalty": 0,
        # "frequency_penalty": 0,
        # "temperature": 0.6,
        "messages": [
            {
            "role": "user",
            "content": prompt
            }
        ]
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ.get('FIREWORKS_API_KEY')}"
    }


    while respond == "" and try_count < 1:
        # print("try_count: ", try_count)
        try_count += 1

        res = requests.request("POST", url, headers=headers, data=json.dumps(payload))

        # print(res.text)

        response = json.loads(res.text)
        code = response.get("code", 0)

        if code != 0:
            print("Error: ", response.get("message", "Unknown error"))
            break

        usages = {
            "prompt_tokens": response["usage"]["prompt_tokens"],
            "completion_tokens": response["usage"]["completion_tokens"],
            "total_tokens": response["usage"]["total_tokens"]
        }

        respond = response["choices"][0]["message"]["content"]

        # {"id":"7629bdc1-47ae-4c2b-91c7-0506546310fa","object":"chat.completion","created":1738230849,"model":"accounts/fireworks/models/deepseek-r1","choices":[{"index":0,"message":{"role":"assistant","content":"<think>\n\n</think>\n\nHello! I'm just a virtual assistant, so I don't have feelings, but I'm here and ready to help you with whatever you need. How are you doing? 😊"},"finish_reason":"stop"}],"usage":{"prompt_tokens":9,"total_tokens":51,"completion_tokens":42}}

        # respond = response.choices[0].message.content
        # reasoning_content = chat_completion.choices[0].message.reasoning_content


    return (respond, "", usages)


def fireworks_ray(llm_config, prompts, question_ids):
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
