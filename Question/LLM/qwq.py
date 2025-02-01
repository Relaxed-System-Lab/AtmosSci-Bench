import os
from transformers import AutoModelForCausalLM, AutoTokenizer
import time
import torch


# MAX_NEW_TOKEN = 8192
# MAX_NEW_TOKEN = 4096
MODEL_NAME = "Qwen/QwQ-32B-Preview"

def qwq_prompt(question, options):
    return f"""You are a Earth Science Expert answering multiple-choice questions.
Here is the question: {question}
Here are the options:
{options}

Instructions:
1. Carefully analyze the question and options provided.
2. Please think step by step. Use logical reasoning and critical thinking to generate a detailed explanation or steps leading to the answer.
3. At the end of your response, ensure to provide the correct option (A/B/C/D) on a new line in the following format strictly:
**Final Answer**: \\[ \\boxed{{A/B/C/D}} \\]"""

def qwq_init(gpu, max_new_token):
    # At lease 4 GPU (~80G) is needed.
    os.environ["CUDA_VISIBLE_DEVICES"] = gpu
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype="auto",
        device_map="auto"
    ).eval()

    # adding padding_side="left" for Decoder-only models
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=False, padding_side="left")
    
    return (model, tokenizer, max_new_token)


def qwq(llm_config, prompts, question_ids):
    error = ""
    model = llm_config[0]
    tokenizer = llm_config[1]
    max_new_token = llm_config[2]

    messages_list = [
        [
            {"role": "user", "content": prompt}
        ] for prompt in prompts
    ]

    time_start = time.time()
    texts = [tokenizer.apply_chat_template(msg, tokenize=False, add_generation_prompt=True) for msg in messages_list]
    model_inputs = tokenizer(texts, return_tensors="pt", padding=True, truncation=True).to('cuda')
    # text = tokenizer.apply_chat_template(
    #     messages,
    #     tokenize=False,
    #     add_generation_prompt=True
    # )
    # model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
    # model_inputs = tokenizer([text], return_tensors="pt").to("cuda")


    MAX_RETRIES = 2  # Set the maximum number of retries
    retry_count = 0  # Current retry count
    success = False  # Flag to indicate whether the operation was successful

    while not success and retry_count <= MAX_RETRIES:
        try:
            # Release unused GPU memory before running
            # torch.cuda.empty_cache()

            with torch.no_grad():
                # Generate outputs with the model
                generated_ids = model.generate(
                    **model_inputs,
                    max_new_tokens=max_new_token
                )

                # Remove input tokens from output to get generated tokens only
                generated_ids = [
                    output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
                ]

            # Decode generated tokens into human-readable text
            responds = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
            
            # Mark as successful and exit the loop
            success = True

            # Release unused GPU memory after running
            # torch.cuda.empty_cache()

        except torch.cuda.OutOfMemoryError:
            # Handle out-of-memory error
            torch.cuda.empty_cache()  # Release GPU memory
            retry_count += 1  # Increment retry count
            if retry_count > MAX_RETRIES:
                responds = f"Out of memory error in running question {question_ids} after {MAX_RETRIES} retries."
                error = responds

        except Exception as e:
            # Handle other unexpected exceptions
            responds = f"Unexpected error in running question {question_ids}: {e}"
            error = responds
            break  # Exit the loop for non-OOM errors


    time_end = time.time()

    # Extract a single letter as the correct answer
    # pattern = r"Answer:\s*([A-Da-d])"
    # EXMPLAE:
    # **Final Answer**
    # 
    # \[ \boxed{B} \]
    pattern = r"\\boxed\{([A-D])\}"

    metadata = {
        "infer_time": time_end - time_start,
        "model": MODEL_NAME,
        "max_new_tokens": max_new_token,
        "CUDA_VISIBLE_DEVICES": os.environ["CUDA_VISIBLE_DEVICES"],
        "error": error
    }

    usages = ["" for _ in range(len(prompts))]
    reasoning_contents = ["" for _ in range(len(prompts))]
    return responds, pattern, metadata, usages, reasoning_contents
