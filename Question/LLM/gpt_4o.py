from openai import OpenAI
import os
import ray
import time


# MAX_NEW_TOKEN = 8192
# MODEL = "gpt-4o"
MODEL = "gpt-4o-mini"

def gpt4o_init(model_name, max_new_token):
    print("Initializing Ray...")
    ray.init(ignore_reinit_error=True)
    print("Ray initialized.")

    return (model_name, max_new_token)

def gpt4o_prompt(question, options):
    return f"""You are a Earth Science Expert answering multiple-choice questions.
Here is the question: {question}
Here are the options:
{options}

Instructions:
1. Carefully analyze the question and options provided.
2. Please think step by step. Use logical reasoning and critical thinking to generate a detailed explanation or steps leading to the answer.
3. At the end of your response, ensure to provide the correct option (A/B/C/D) on a new line in the following format strictly:
Answer: [Correct Option(A/B/C/D)]"""

def fetch_response(prompt, model_name, max_new_token):
    from dotenv import load_dotenv
    load_dotenv()

    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),  # This is the default and can be omitted
    )

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=model_name
        # max_completion_tokens=max_new_token
    )

    usages = {
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens
    }

    respond =  response.choices[0].message.content
    # reasoning_content = chat_completion.choices[0].message.reasoning_content
    reasoning_content = ""

    return (respond, reasoning_content, usages)



def gpt4o(llm_config, prompts, question_ids):
    model_name = llm_config[0]
    max_new_token = llm_config[1]
    time_start = time.time()

    futures = [ray.remote(fetch_response).remote(prompt, model_name, max_new_token) for prompt in prompts]
    ray_responses = ray.get(futures)
    
    # print("ray_responses: ", ray_responses)

    time_end = time.time()

    responses = [res[0] for res in ray_responses]
    reasoning_contents = [res[1] for res in ray_responses]
    usages = [res[2] for res in ray_responses]

    # Extract a single letter as the correct answer
    pattern = r"Answer:\s*([A-Da-d])"

    metadata = {
        "model": model_name,
        "infer_time": time_end - time_start,
        "max_new_tokens": max_new_token,
    }

    return responses, pattern, metadata, usages, reasoning_contents
