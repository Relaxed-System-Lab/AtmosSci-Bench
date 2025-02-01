import pandas as pd
import os
import re
import numpy as np
from tqdm import tqdm
from datetime import datetime

from collections import defaultdict
import traceback
import json
import time
from itertools import islice

from question_collection import question_collection, INSTANCE_SIZE

import argparse

from utils import GENERAL_RE_PATTERNS, extract_option


def run_eval(model, dataset_path, batch_size, specific_model, instance_start, instance_end, gpu, max_new_token):
    # ========== SETTINGS ==========

    # Set to True if using the question collection from question_collection.py
    USING_QUESTION_COLLECTION = False
    # TODO: USING_QUESTION_COLLECTION = True not working yet

    # If don't use the question collection, specify the path to the dataset
    # current_file_directory = os.path.dirname(os.path.abspath(__file__))
    # DATASET_PATH = "question_collection_i1.csv"
    # DATASET_FINAL_PATH = os.path.join(current_file_directory, "generated_datasets", DATASET_PATH)


    # SET Batch Size
    # BATCH_SIZE = 2

    # ===== Helper function =====
    def get_output_directory(using_question_collection, model, instance_size, dataset_path, instance_start, instance_end, specific_model, max_new_token):
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        if using_question_collection:
            # return os.path.join("Evaluation", f"{current_time}_{model}_i{instance_size}")
            # TBD
            return None
        else:
            dataset_name = dataset_path.split(".")[0].split("_")[-1]
            if dataset_name == "test":
                instance_name = "test"
            else:
                instance_name = f"i{instance_start}-{instance_end}"

            # if model == "hugging_face" or model == "together":
            #     model_name = specific_model.split("/")[-1]
            # else:
            #     model_name = model

            if specific_model:
                model_name = model + "_" + specific_model.split("/")[-1]
            else:
                model_name = model

            if "high-precision" in dataset_path:
                return os.path.join("Evaluation", f"{current_time}_{model_name}_{instance_name}_{max_new_token}_high_precision")
            elif "low-precision" in dataset_path:
                return os.path.join("Evaluation", f"{current_time}_{model_name}_{instance_name}_{max_new_token}_low_precision")

            return os.path.join("Evaluation", f"{current_time}_{model_name}_{instance_name}_{max_new_token}")

    def append_to_csv(file_path, data):
        """Append data to a CSV file. Creates file if it doesn't exist."""
        # print(f"Appending to {file_path}")
        df = pd.DataFrame(data)
        mode = 'a' if os.path.exists(file_path) else 'w'
        header = not os.path.exists(file_path)
        df.to_csv(file_path, mode=mode, index=False, header=header)

    def append_to_log(file_path, messages):
        """Append messages to a log file. Creates file if it doesn't exist."""
        with open(file_path, "a") as f:
            f.writelines(f"{msg}\n" for msg in messages)

    def write_to_log(file_path, message):
        """Write a message to a log file. Creates file if it doesn't exist."""
        with open(file_path, "w") as f:
            f.write(message)

    # ===== Setup paths =====
    current_file_directory = os.path.dirname(os.path.abspath(__file__))
    output_dir = get_output_directory(USING_QUESTION_COLLECTION, model, INSTANCE_SIZE, dataset_path, instance_start, instance_end, specific_model, max_new_token)
    output_dir = os.path.join(current_file_directory, output_dir)
    os.makedirs(output_dir, exist_ok=True)
    results_path = os.path.join(output_dir, "llm_results.csv")
    log_path = os.path.join(output_dir, "log.txt")
    error_log_path = os.path.join(output_dir, "error_log.txt")
    meta_log_path = os.path.join(output_dir, "metadata.txt")


    # ===== Get Batches =====
    def get_batches(dataset, batch_size):
        """Generate batches from the dataset."""
        dataset_iter = enumerate(dataset) if isinstance(dataset, list) else dataset.iterrows()
        while True:
            batch = list(islice(dataset_iter, batch_size))
            if not batch:  # Stop when no more data
                break
            yield batch


    # ========== LLM Initilaization ==========
    append_to_log(log_path, [f"Initializing Model..."])
    if model == "gpt-4o":
        from LLM.gpt_4o import gpt4o, gpt4o_prompt, gpt4o_init
        call_LLM = gpt4o
        LLM_prompt = gpt4o_prompt
        LLM_config = gpt4o_init(specific_model, max_new_token)

    if model == "qwq":
        from LLM.qwq import qwq, qwq_prompt, qwq_init
        call_LLM = qwq
        LLM_prompt = qwq_prompt
        LLM_config = qwq_init(gpu, max_new_token)

    if model == "hugging_face":
        from LLM.hugging_face import hugging_face, hugging_face_init, hugging_face_prompt
        call_LLM = hugging_face
        LLM_prompt = hugging_face_prompt
        LLM_config = hugging_face_init(specific_model, gpu, max_new_token)

    if model == "deepseek_v3":
        from LLM.deepseek_v3 import deepseek_v3, deepseek_v3_prompt, deepseek_v3_init
        call_LLM = deepseek_v3
        LLM_prompt = deepseek_v3_prompt
        LLM_config = deepseek_v3_init(max_new_token)

    if model == "o1":
        from LLM.o1 import o1, o1_prompt, o1_init
        call_LLM = o1
        LLM_prompt = o1_prompt
        LLM_config = o1_init(max_new_token)

    # if model == "qwen_math_prm":
    #     from LLM.qwen_math_prm import qwen_math_prm, qwen_math_prm_prompt, qwen_math_prm_init
    #     call_LLM = qwen_math_prm
    #     LLM_prompt = qwen_math_prm_prompt
    #     LLM_config = qwen_math_prm_init(specific_model, gpu)

    if model =="gemini":
        from LLM.gemini import gemini, gemini_prompt, gemini_init
        call_LLM = gemini
        LLM_prompt = gemini_prompt
        LLM_config = gemini_init(max_new_token)

    if model == "deepseek_reasoner":
        from LLM.deepseek_reasoner import deepseek_reasoner, deepseek_reasoner_prompt, deepseek_reasoner_init
        call_LLM = deepseek_reasoner
        LLM_prompt = deepseek_reasoner_prompt
        LLM_config = deepseek_reasoner_init(max_new_token)

    if model == "together":
        from LLM.together import together, together_prompt, together_init
        call_LLM = together
        LLM_prompt = together_prompt
        LLM_config = together_init(specific_model, max_new_token)

    if model == "together_ray":
        from LLM.together_ray import together_ray, together_ray_prompt, together_ray_init
        call_LLM = together_ray
        LLM_prompt = together_ray_prompt
        LLM_config = together_ray_init(specific_model, max_new_token)

    if model == "fireworks":
        from LLM.fireworks import fireworks_ray, fireworks_ray_prompt, fireworks_ray_init
        call_LLM = fireworks_ray
        LLM_prompt = fireworks_ray_prompt
        LLM_config = fireworks_ray_init(specific_model, max_new_token)


    append_to_log(log_path, [f"Model Initialization Completed."])

    # ============== Call LLM ================
    def get_answer(questions, options, question_ids):
        """
        Extracts the correct option from the GPT output.
        """

        prompts = [LLM_prompt(questions, options) for questions, options in zip(questions, options)]
        # 3. Accept minor margin of error in the response. If unable to provide an answer, respond with "NoAnswer".

        try:
            # Call LLM
            responds, pattern, metadata, usage, reasoning_contents = call_LLM(LLM_config, prompts, question_ids)
            
            # print("responds111", responds)

            answers = [extract_option(respond, GENERAL_RE_PATTERNS) for respond in responds]
            
            # print("answers111", answers)

            return answers, responds, prompts, metadata, usage, reasoning_contents
        except Exception as e:
            # print(f"## Error:\n {e}")
            append_to_log(error_log_path, [f"""Error: {e}\n{traceback.format_exc()}"""])
            return ["Error" for _ in prompts], ["Error" for _ in prompts], ["Error" for _ in prompts], {}, ["Error" for _ in prompts], ["Error" for _ in prompts]

    # ===== Run Evaluation =====
    results = []  # To store results temporarily
    error_log = []  # To store errors temporarily
    metadata_log = {}

    start_time = time.time()
    try:
        if USING_QUESTION_COLLECTION:
            # dataset = question_collection
            pass
        else:
            dataset = pd.read_csv(dataset_path)
        
        # ===== filter dataset ====
        # Filter the rows based on the range of instance ids (instance_start - instance_end)
        append_to_log(log_path, [f"Filtering dataset..."])
        dataset['instance_id'] = dataset['id'].apply(lambda x: int(x.split('_')[1]))
        dataset = dataset[(dataset['instance_id'] >= instance_start) & (dataset['instance_id'] <= instance_end)]


        append_to_log(log_path, [f"Evaluating..."])
        # Process dataset with progress bar
        dataset_len = len(dataset)
        batch_total_len = (len(dataset) + batch_size - 1) // batch_size
        question_completed = 0
        total_infer_time = 0

        print("Start processing questions..., total questions:", dataset_len)

        for index, batch in tqdm(enumerate(get_batches(dataset, batch_size)), desc="Processing Questions", total=batch_total_len):
            try:
                # Extract question and options
                if USING_QUESTION_COLLECTION:
                    question_texts = [question_obj.question() for question_obj in batch]
                    options_texts = [question_obj.options_md() for question_obj in batch]
                    correct_options = [question_obj.correct_option() for question_obj in batch]
                    options = [question_obj.options_str_list() for question_obj in batch]
                else:
                    question_texts = [question_obj[1]["question"] for question_obj in batch]
                    options_texts = [question_obj[1]["options_text"] for question_obj in batch]
                    correct_options = [question_obj[1]["correct_option"] for question_obj in batch]
                    options = [question_obj[1]["options"] for question_obj in batch]
                question_ids = [question_obj[1]["id"] if not USING_QUESTION_COLLECTION else question_obj.id for question_obj in batch]


                # Get the LLM answer
                llm_answers, llm_responds, llm_prompts, llm_meta, llm_usages, llm_reasoning_contents = get_answer(question_texts, options_texts, question_ids)

                # print("get_answer", llm_answers)

                # add infer time
                infer_time = 0
                question_completed += len(llm_prompts)
                append_to_log(log_path, [f"Batch {index}/{batch_total_len} completed. Questions {question_completed}/{dataset_len} completed."])
                if "infer_time" in llm_meta:
                    infer_time = llm_meta["infer_time"]
                    total_infer_time += infer_time
                    metadata_log["total_infer_time"] = total_infer_time
                    append_to_log(log_path, [f"Time taken: {infer_time} seconds."])
                if "error" in llm_meta and llm_meta["error"]:
                    append_to_log(error_log_path, [llm_meta["error"]])
                if "log" in llm_meta:
                    append_to_log(log_path, [llm_meta["log"]])

                # update metadata
                filtered_llm_meta = {k: v for k, v in llm_meta.items() if k != "infer_time" and k != "error" and k != "log"}
                metadata_log.update(filtered_llm_meta)
                metadata_log.update({"Batch Number": index + 1})
                metadata_log.update({"Batch Size": batch_size})

                # Append results for this question
                def get_result(question_id, question_obj, llm_prompt, llm_answer, llm_respond, question_text, opts, correct_option, options_text, llm_usage, llm_reasoning_content):
                    result = {
                        "id": question_id,
                        "seed": question_obj[1]["seed"] if not USING_QUESTION_COLLECTION else question_obj.seed,
                        "type": question_obj[1]["type"] if not USING_QUESTION_COLLECTION else question_obj.type,
                        "generation_method": "Original" if (question_obj[1]["id"] if not USING_QUESTION_COLLECTION else question_obj.id).split("_")[1] == "1" else "Symbolic Extension",
                        "variables": question_obj[1]["variables"] if not USING_QUESTION_COLLECTION else question_obj.variables,
                        "question": question_text,
                        "answer": question_obj[1]["answer"] if not USING_QUESTION_COLLECTION else question_obj.answer(),
                        "options": opts,
                        "options_text": options_text,
                        "correct_option": correct_option,
                        "options_types_str": question_obj[1]["options_types_str"] if not USING_QUESTION_COLLECTION else question_obj.options_types_str(),
                        "llm_prompt": llm_prompt,
                        "llm_answer": llm_answer,
                        "llm_infer_len": len(llm_respond),
                        "correct": llm_answer == correct_option,
                        "llm_respond": llm_respond,
                        "NoAnswer": llm_answer == "NoAnswer",
                        "Usage": llm_usage,
                        "llm_reasoning_content": llm_reasoning_content,
                        "Error": (llm_respond == "Error") or (llm_respond == "E") or (llm_respond == "r") or (llm_respond == "o") or (llm_respond == "e") or (len(llm_respond) < 10 and llm_answer == "NoAnswer")
                        # "infer_time": infer_time
                    }
                    return result

                # print("llm_answers", llm_answers)
                # # Append results for this question
                # print("len question_ids", len(question_ids))
                # print("len batch", len(batch))
                # print("len llm_prompts", len(llm_prompts))
                # print("len llm_answers", len(llm_answers))
                # print("len llm_responds", len(llm_responds))
                # print("len question_texts", len(question_texts))
                # print("len options", len(options))
                # print("len correct_options", len(correct_options))
                # print("len options_texts", len(options_texts))
                # print("len llm_usages", len(llm_usages))
                # print("len llm_reasoning_contents", len(llm_reasoning_contents))
                
                
                for question_id, question_obj, llm_prompt, llm_answer, llm_respond, question_text, opts, correct_option, options_text, llm_usage, llm_reasoning_content in zip(question_ids, batch, llm_prompts, llm_answers, llm_responds, question_texts, options, correct_options, options_texts, llm_usages, llm_reasoning_contents):
                    result = get_result(question_id, question_obj, llm_prompt, llm_answer, llm_respond, question_text, opts, correct_option, options_text, llm_usage, llm_reasoning_content)
                    # print("result", result)
                    results.append(result)

                # print("results lemgtj", results)
                # print("results length", len(results))
                # Periodically append results to CSV
                if len(results) >= 1:  # Save every 1 results
                    # print("append to csv")
                    append_to_csv(results_path, results)
                    write_to_log(meta_log_path, json.dumps(metadata_log, indent=4))
                    results.clear()

            except Exception as e:
                error_log.append(f"Error processing batch {index}: {e}\n{traceback.format_exc()}")

                # Append error logs immediately
                append_to_log(error_log_path, error_log)
                error_log.clear()

        # Final save for any remaining results
        if results:
            append_to_csv(results_path, results)
        if error_log:
            append_to_log(error_log_path, error_log)

    except Exception as e:
        error_log.append(f"Critical Error: {e}\n{traceback.format_exc()}")
        if error_log:
            append_to_log(error_log_path, error_log)

    finally:
        # Record end time and calculate total duration
        end_time = time.time()
        total_time = end_time - start_time
        metadata_log.update({"total_time": total_time})
        metadata_log.update({"Batch Size": batch_size})
        write_to_log(meta_log_path, json.dumps(metadata_log, indent=4))
        # time_message = f"Total processing time: {total_time:.2f} seconds ({total_time / 60:.2f} minutes)"
        # time_message += f"\nTotal inference time: {total_infer_time:.2f} seconds ({total_infer_time / 60:.2f} minutes)"
        # append_to_log(meta_log_path, [time_message])

    append_to_log(log_path, [f"Evaluation Completed."])

    append_to_log(log_path, [f"Runing Analysis..."])
    # ===== Run Analysis script =====
    import subprocess

    main_path = os.path.dirname(current_file_directory)
    instance_analysis_path = os.path.join(main_path, "Evaluation/instance_analysis.py")
    generate_accuracy_path =  os.path.join(main_path, "Evaluation/generate_accuracy.py")

    subprocess.run(["python", instance_analysis_path, output_dir])
    subprocess.run(["python", generate_accuracy_path, output_dir])

    append_to_log(log_path, [f"Analysis Completed."])

    print("Processing completed with errors logged where applicable.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--model', type=str, help="Model name", default="qwq")
    parser.add_argument('-d', '--dataset', type=str, help="Dataset name", default="question_collection_itest.csv")
    parser.add_argument('-b', '--batch_size', type=int, default=8, help="Batch size")
    parser.add_argument('-s', '--instance_start', type=int, default=1, help="The index of the first instance to process.")
    parser.add_argument('-e', '--instance_end', type=int, default=1, help="The index of the last instance to process.")
    parser.add_argument('-hm', '--specific_model', type=str, default="", help="The name of specific_model to use. Only when set model to hugging_face.")
    parser.add_argument("--gpu", type=str, default="0", help="Specify GPUs to use, e.g., '0,1,2,3'")
    parser.add_argument("--max_new_token", type=str, default="8192", help="Specify the maximum number of new tokens to generate")
    args = parser.parse_args()

    if args.model in ["hugging_face", "together", "together_ray", "fireworks", "gpt-4o"] and args.specific_model == "":
        parser.error("You have to specify the specific_model name when using {args.model} model.")

    current_file_directory = os.path.dirname(os.path.abspath(__file__))
    data_name = args.dataset
    dataset_path = os.path.join(current_file_directory, "generated_datasets", data_name)

    run_eval(args.model, dataset_path, args.batch_size, args.specific_model, args.instance_start, args.instance_end, args.gpu, args.max_new_token)
