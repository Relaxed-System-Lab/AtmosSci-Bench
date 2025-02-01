# ATMOSSCI-BENCH


## Introduction
A comprehensive MCQ(Multi-choices Question) benchmark framework of Atmospheric Science for evaluating for LLMs(Large Language Models).

This is repository for Paper "AtmosSci-Bench: Evaluating the Recent Advance of Large Language Model for Atmospheric Science".

## Getting Started
### Prerequisites
+ Python 3.10.9
+ Dependencies listed in `requirements.txt`

## Installation
1. Clone this repository.
2. Run `setup.sh`.
3. Manually install any missing dependencies from `requirements.txt`, if necessary.


# Dataset Generation
You can skip this section if you do not need to customize the dataset. The pre-generated dataset is available in Question/generated_datasets.

### Generate Datasets
1. Add new Question Templates in `Question/Questions`.
2. Add all the Question Templates that you want to output in `Question/question_collection.py`.
3. Set `BATCH_SIZE` which output how many question instances for each Question Templates in `Question/question_collection.py`.
4. Set `PRECISION` at the top of `Question/Questions/question.py`
5. Run `Question/save_to_csv.py` to generate the datasets.
6. All the datasets are saved in `Question/generated_datasets`

### Visualize Questions
1. Run `streamlit run Question/visualize_all.py`



# Evaluation Experiment
You can follow the example below to start your evaluation.

To test with a customized number of test cases in a single run, modify the parameters `--instance_start 1 --instance_end 10`, where `10` represents the total number of test cases. (Note: A dataset ending with `_i50` indicates that only 50 test cases are included.)

To test with an alternative precision level, set the `--dataset` parameter to one of the following:
+ `question_collection_low_precision_i50.csv`
+ `question_collection_high_precision_i50.csv`

Please `cd` to the `Script` folder and run following command:

## Local Models
### Hugging face model:

This is an example of running `Qwen/Qwen2.5-32B-Instruct`:
```
huggingface-cli login
python3 ../Question/evaluation.py --model hugging_face --specific_model "Qwen/Qwen2.5-32B-Instruct"  --dataset question_collection_i50.csv --batch_size 8 --instance_start 1 --instance_end 10 --gpu="0,1,2,3,4,5,6,7" --max_new_token 8192
```

### QwQ

```
python3 ../Question/evaluation.py --model qwq --dataset question_collection_i50.csv --batch_size 8 --instance_start 1 --instance_end 10 --max_new_token 30000 --gpu="0,1,2,3,4,5,6,7"
```


## Calling APIs
In API calls, the `batch_size` parameter specifies the number of processes invoking the API endpoint concurrently.

Please create `.env` and put your API_KEY:
```
DeepSeek_API_KEY = ""
OPENAI_API_KEY = ""
TOGETHER_API_KEY = ""
FIREWORKS_API_KEY=""
GEMINI_API_KEY=""
```



### Deepseek_R1 model:
```
python3 ../Question/evaluation.py --model deepseek_reasoner --dataset question_collection_i50.csv --batch_size 8 --instance_start 1 --instance_end 10 --max_new_token 30000
```


### Deepseek_V3 model:
```
python3 ../Question/evaluation.py --model deepseek_v3 --dataset question_collection_i50.csv --batch_size 8 --instance_start 1 --instance_end 10 --max_new_token 30000
```


### Fireworks:
```
python3 ../Question/evaluation.py --model fireworks --specific_model "accounts/fireworks/models/deepseek-r1" --dataset question_collection_i50.csv --batch_size 8 --instance_start 1 --instance_end 10 --max_new_token 30000
```

### gemini-2.0-flash-thinking-exp-01-21:
```
python3 ../Question/evaluation.py --model gemini --dataset question_collection_i50 --dataset question_collection_i50.csv --batch_size 8 --instance_start 1 --instance_end 10 --max_new_token 30000
```


### gpt-4o and gpt-4o-mini:
```
python3 ../Question/evaluation.py --model gpt-4o --specific_model "gpt-4o" --dataset question_collection_i50.csv --batch_size 8 --instance_start 1 --instance_end 10 --max_new_token 30000
```
```
python3 ../Question/evaluation.py --model gpt-4o --specific_model "gpt-4o-mini" --dataset question_collection_i50.csv --batch_size 8 --instance_start 1 --instance_end 10 --max_new_token 30000
```

### gpt-o1:
```
python3 ../Question/evaluation.py --model o1 --dataset question_collection_i50.csv --batch_size 8 --instance_start 1 --instance_end 10 --max_new_token 30000
```

### together:
```
python3 ../Question/evaluation.py --model together --specific_model "Qwen/QwQ-32B-Preview" --dataset question_collection_i50.csv --batch_size 8 --instance_start 1 --instance_end 10 --max_new_token 30000
```

### together with ray:
```
python3 ../Question/evaluation.py --model together_ray --specific_model "Qwen/QwQ-32B-Preview" --dataset question_collection_i50.csv --batch_size 8 --instance_start 1 --instance_end 10 --max_new_token 30000
```

