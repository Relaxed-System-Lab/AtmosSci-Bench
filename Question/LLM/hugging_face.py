import os
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoModel
import time
import torch
import numpy as np
from transformers.generation import GenerationConfig
from accelerate import Accelerator

# MAX_NEW_TOKEN = 8192
# MAX_NEW_TOKEN = 4096

def hugging_face_prompt(question, options):
    return f"""You are a Earth Science Expert answering multiple-choice questions.
Here is the question: {question}
Here are the options:
{options}

Instructions:
1. Carefully analyze the question and options provided.
2. Please think step by step. Use logical reasoning and critical thinking to generate a detailed explanation or steps leading to the answer.
3. At the end of your response, ensure to provide the correct option (A/B/C/D) on a new line in the following format strictly:
**Final Answer**: \\[ \\boxed{{A/B/C/D}} \\]"""

def hugging_face_init(model_name, gpu, max_new_token):
    # At lease 4 GPU (~80G) is needed.
    os.environ["CUDA_VISIBLE_DEVICES"] = gpu
    
    from accelerate import Accelerator

    # init accelerator
    # accelerator = Accelerator(mixed_precision="fp16") 
    accelerator = Accelerator() 

    if model_name in ["Qwen/Qwen2.5-Math-PRM-7B"]:
        model_class = AutoModel
    else:
        model_class = AutoModelForCausalLM

    # adding padding_side="left" for Decoder-only models
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False, padding_side="left")
    model = model_class.from_pretrained(
        model_name,
        torch_dtype="auto",
        # torch_dtype=torch.bfloat16,
        device_map="auto",  # acceleate will handle the device mapping
        # attn_implementation="flash_attention_2" # FlashAttention-2
    ).eval()
    # model.generation_config = GenerationConfig.from_pretrained(
    #     model_name, trust_remote_code=True
    # )
    # model.generation_config.do_sample = False
    
    if 'Llama' in model_name:
        model.generation_config.pad_token_id = tokenizer.pad_token_id

    if 'deepseek-math' in model_name:
        tokenizer.pad_token = tokenizer.eos_token
        model.generation_config.pad_token_id = tokenizer.pad_token_id
    
    if 'eci-io/climategpt-70b' in model_name:
        tokenizer.pad_token = tokenizer.eos_token
        model.generation_config.pad_token_id = tokenizer.pad_token_id
        # Setting `pad_token_id` to `eos_token_id`:2 for open-end generation.
        # Setting `pad_token_id` to `eos_token_id`:2 for open-end generation.

    return (model, tokenizer, model_name, accelerator, max_new_token)


def hugging_face(llm_config, prompts, question_ids):
    error = ""
    log = ""
    model = llm_config[0]
    tokenizer = llm_config[1]
    model_name = llm_config[2]
    accelerator = llm_config[3]
    max_new_token = llm_config[4]

    messages_list = [
        [
            {"role": "user", "content": prompt}
        ] for prompt in prompts
    ]

    time_start = time.time()
    texts = [tokenizer.apply_chat_template(msg, tokenize=False, add_generation_prompt=True) for msg in messages_list]
    
    model_inputs = tokenizer(texts, return_tensors="pt", padding=True, truncation=True).to(accelerator.device)
    # try:
    #     # Tokenize and move inputs to GPU
    #     model_inputs = tokenizer(texts, return_tensors="pt", padding=True, truncation=True)
    #     # model_inputs = {k: v.to('cuda') for k, v in model_inputs.items()}
    # except Exception as e:
    #     print(f"Error during tokenization: {e}")
    #     print("Input texts:", texts)
    #     print("Tokenized inputs:", tokenizer(texts))

    time_tokenizer = time.time()

    MAX_RETRIES = 0  # Set the maximum number of retries
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

            success = True

            # Release unused GPU memory after running
            # torch.cuda.empty_cache()


        except torch.cuda.OutOfMemoryError:
            # Handle out-of-memory error
            torch.cuda.empty_cache()  # Release GPU memory
            retry_count += 1  # Increment retry count
            if retry_count > MAX_RETRIES:
                responds = "Error"
                error += f"Out of memory error in running question {question_ids} after {MAX_RETRIES} retries, trying to split the input."

        except Exception as e:
            # Handle other unexpected exceptions
            responds = "Error"
            error += f"Unexpected error in running question {question_ids}: {e}"
            break  # Exit the loop for non-OOM errors
    
    if error and success:
        error += f"Question was successfully processed after {MAX_RETRIES} retries."

    time_end = time.time()
    
    log = f"Tokenizer time: {time_tokenizer - time_start}, Inference time: {time_end - time_tokenizer}"

    # Extract a single letter as the correct answer
    # pattern = r"Answer:\s*([A-Da-d])"
    # EXMPLAE:
    # **Final Answer**
    # 
    # \[ \boxed{B} \]
    pattern = r"\\boxed\{([A-D])\}"

    metadata = {
        "infer_time": time_end - time_start,
        "model": model_name,
        "max_new_tokens": max_new_token,
        "CUDA_VISIBLE_DEVICES": os.environ["CUDA_VISIBLE_DEVICES"],
        "error": error,
        "log": log
    }
    
    usage = ["" for _ in range(len(prompts))]
    reasoning_contents = ["" for _ in range(len(prompts))]

    return responds, pattern, metadata, usage, reasoning_contents
