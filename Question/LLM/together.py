from openai import OpenAI
import os
# import ray
import time
import json
from together import Together
import os, asyncio
from together import AsyncTogether


# MAX_NEW_TOKEN = 8192
# MAX_NEW_TOKEN = 16384
# MAX_NEW_TOKEN = 30000
# MAX_NEW_TOKEN = 7300
MAX_NEW_TOKEN = 30000
# MAX_NEW_TOKEN = 4096

# QWQ:
# MAX_NEW_TOKEN = 30000
#  {"message": "Input validation error: `inputs` tokens + `max_new_tokens` must be <= 32769. Given: 364 `inputs` tokens and 32768 `max_new_tokens`", "type_": "invalid_request_error"}.

def together_init(model_name, max_new_token):
    # ray.init(ignore_reinit_error=True)
    from dotenv import load_dotenv
    load_dotenv()

    async_client = AsyncTogether(api_key=os.environ.get("TOGETHER_API_KEY"))

    return (model_name, async_client, max_new_token)

def together_prompt(question, options):
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

# def fetch_response(prompt, model_name):
#     from dotenv import load_dotenv
#     load_dotenv()

#     respond = ""
#     try_count = 0

#     # for backward compatibility, you can still use `https://api.deepseek.com/v1` as `base_url`.
#     # client = Together(api_key=os.environ.get("TOGETHER_API_KEY"))

#     while respond == "" and try_count < 10:
#         try_count += 1

#         if "gemma" in model_name:
#             # `inputs` tokens + `max_new_tokens` must be <= 8193
#             response = client.chat.completions.create(
#                 model=model_name,
#                 messages=[{"role": "user", "content": prompt}],
#                 max_tokens = 6000
#             )
#         else:
#             response = client.chat.completions.create(
#                 model=model_name,
#                 messages=[{"role": "user", "content": prompt}],
#                 max_tokens=MAX_NEW_TOKEN,
#             )

#         # print(response.choices[0].message.content)
#         usages = {
#             "prompt_tokens": response.usage.prompt_tokens,
#             "completion_tokens": response.usage.completion_tokens,
#             "total_tokens": response.usage.total_tokens
#         }

#         respond = response.choices[0].message.content
#         # reasoning_content = chat_completion.choices[0].message.reasoning_content


#     return (respond, "", usages)


def together(llm_config, prompts, question_ids):
    model_name = llm_config[0]
    async_client = llm_config[1]
    max_new_token = llm_config[2]

    time_start = time.time()
    error = ""

    async def async_chat_completion(messages, max_new_token):
        tasks = [
            async_client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": message}],
                max_tokens=max_new_token,
            )
            for message in messages
        ]
        responses = await asyncio.gather(*tasks)

        respond_list = []
        reasoning_contents_list = []
        usages_list = []
        for response in responses:
            respond = response.choices[0].message.content
            usages = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            reasoning_content = ""
            # print(response.choices[0].message.content)
            respond_list.append(respond)
            reasoning_contents_list.append(reasoning_content)
            usages_list.append(usages)
        return respond_list, reasoning_contents_list, usages_list

    retry = 0
    success = False
    responses =""
    while retry < 2 and not success:
        try:
            time_s1 = time.time()
            responses, reasoning_contents, usages = asyncio.run(async_chat_completion(prompts, max_new_token))
            time_s2 = time.time()
            success = True
        except Exception as e:
            time_s2 = time.time()
            retry += 1
            if time_s2 - time_s1 < 60:
                time.sleep(60 - (time_s2 - time_s1) + 20)
            print(f"Error: {e}. Retrying {retry}/2...")

    # futures = [ray.remote(fetch_response).remote(prompt, model_name) for prompt in prompts]
    # ray_responses = ray.get(futures)

    time_end = time.time()

    infer_time = time_end - time_start
    if infer_time < 60:
        time.sleep(60 - infer_time + 20)


    # Extract a single letter as the correct answer
    pattern = r"Answer:\s*([A-Da-d])"

    # err_list = []
    # for res, id in zip(ray_responses, question_ids):
    #     if res[0] == "":
    #         err_list.append(id)

    # responses = [res[0] for res in ray_responses]
    # reasoning_contents = [res[1] for res in ray_responses]
    # usages = [res[2] for res in ray_responses]

    # if err_list:
    #     error = f"Error: Get empty responds in question ids: {err_list}"

    metadata = {
        "model": "together",
        "infer_time": time_end - time_start,
        "error": error,
        "max_new_tokens": max_new_token
    }

    return responses, pattern, metadata, usages, reasoning_contents
