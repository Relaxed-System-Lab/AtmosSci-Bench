from openai import OpenAI
import os
import ray
import time


# MAX_NEW_TOKEN = 30000
# MAX_NEW_TOKEN = 8192

# https://ai.google.dev/gemini-api/docs/thinking-mode

def gemini_init(max_new_token):
    ray.init(ignore_reinit_error=True)

    return (max_new_token)

def gemini_prompt(question, options):
    return f"""You are a Earth Science Expert answering multiple-choice questions.
Here is the question: {question}
Here are the options:
{options}

Instructions:
1. Carefully analyze the question and options provided.
2. Please think step by step. Use logical reasoning and critical thinking to generate a detailed explanation or steps leading to the answer.
3. At the end of your response, ensure to provide the correct option (A/B/C/D) on a new line in the following format strictly:
Answer: [Correct Option(A/B/C/D)]"""
def fetch_response(prompt, max_new_token):
    from dotenv import load_dotenv
    load_dotenv()

    # client = OpenAI(
    #     api_key=os.environ.get("OPENAI_API_KEY"),  # This is the default and can be omitted
    # )

    # MAX_NEW_TOKEN = 8192
    # chat_completion = client.chat.completions.create(
    #     messages=[{"role": "user", "content": prompt}],
    #     model="gemini",
    #     max_completion_tokens=MAX_NEW_TOKEN
    # )

    # default 8k token output limit
    MODEL = "gemini-2.0-flash-thinking-exp-01-21"
    # MODEL = "gemini-2.0-flash-thinking-exp"
        # gemini-2.0-flash-thinking-exp
        # gemini-2.0-flash-thinking-exp-01-21
        # gemini-2.0-flash-exp


    if MODEL == "gemini-2.0-flash-thinking-exp-01-21" or MODEL == "gemini-2.0-flash-thinking-exp":
        import google.generativeai as genai
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-thinking-exp-01-21",
            generation_config={
                # "temperature": 0.7,
                # "top_p": 0.95,
                # "top_k": 64,
                "max_output_tokens": max_new_token,
                "response_mime_type": "text/plain",
                }
        )
        response = model.generate_content(prompt)
        respond = response.text
        thought = ""
        usages = response.usage_metadata
    else:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"), http_options={'api_version':'v1alpha'})
        response = client.models.generate_content(
            model=MODEL, contents=prompt,
            config=types.GenerateContentConfig(
                # temperature=0,
                # top_p=0.95,
                # top_k=20,
                # candidate_count=1,
                # seed=5,
                max_output_tokens=max_new_token,
                # stop_sequences=["STOP!"],
                # presence_penalty=0.0,
                # frequency_penalty=0.0,
            )
        )
        # "max_output_tokens": 65536,

        usages = {
            "prompt_tokens": response.usage_metadata.prompt_token_count,
            "completion_tokens": response.usage_metadata.candidates_token_count,
            "total_tokens": response.usage_metadata.total_token_count
        }

        respond = ""
        thought = ""
        if response.candidates:
            for part in response.candidates[0].content.parts:
                if part.thought == True:
                    # print(f"Model Thought:\n{part.text}\n")
                    # respond += f"Model Thought:\n{part.text}\n"
                    thought = part.text
                else:
                    # print(f"\nModel Response:\n{part.text}\n")
                    # ret += f"\nModel Response:\n{part.text}\n"
                    respond = part.text
        else:
            respond = ""

    return (respond, thought, usages)


def gemini(llm_config, prompts, question_ids):
    max_new_token = llm_config[0]
    time_start = time.time()

    futures = [ray.remote(fetch_response).remote(prompt, max_new_token) for prompt in prompts]
    ray_responses = ray.get(futures)

    time_end = time.time()

    # Extract a single letter as the correct answer
    pattern = r"Answer:\s*\*?([A-Da-d])\*?"

    responses = [res[0] for res in ray_responses]
    reasoning_contents = [res[1] for res in ray_responses]
    usages = [res[2] for res in ray_responses]

    # wait for 1 minute to avoid rate limit
    infer_time = time_end - time_start
    if infer_time < 60:
        time.sleep(70 - infer_time)

    metadata = {
        "model": "gemini-2.0-flash-thinking-exp-01-21",
        "infer_time": time_end - time_start,
        "MAX_NEW_TOKEN": max_new_token
    }

    return responses, pattern, metadata, usages, reasoning_contents
