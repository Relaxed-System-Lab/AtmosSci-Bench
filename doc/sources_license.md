# Sources and Licenses

## Model and Library Usage Licenses

Following table list the models and software assets used in this work, along with their respective sources and licensing terms. All API-based models are accessed through official platforms under standard usage policies, while open-source models are released under community-accepted licenses (Apache, MIT, etc.).

| Model / Library                                                          | Source / Access Method                                | License / Terms of Use                            |
| ------------------------------------------------------------------------ | ----------------------------------------------------- | ------------------------------------------------- |
| GPT-4o, GPT-4o-mini, GPT-o1, GPT-o3-mini                                 | OpenAI API                                            | OpenAI API Terms of Use                           |
| Gemini-2.0-Flash-Exp, Gemini-2.0-Flash-Thinking-Exp (01-21)              | Google API (Vertex AI)                                | Google Cloud Terms of Service                     |
| DeepSeek-V3, DeepSeek-R1, DeepSeek-Math-7B-Instruct, DeepSeek-Math-7B-RL | Deepseek API                                          | Deepseek Public API Terms                         |
| Qwen2.5-Instruct (3B, 7B, 32B, 72B)                                      | HuggingFace / Together AI                             | Apache License 2.0                                |
| Qwen2.5-Math (1.5B, 7B, 72B)                                             | HuggingFace / Together AI                             | Apache License 2.0                                |
| QwQ-32B-Preview                                                          | HuggingFace (based on Qwen2.5-32B)                    | Apache License 2.0                                |
| Qwen3-235B-A22B-FP8-Throughput                                           | HuggingFace                                           | Apache License 2.0                                |
| Gemma-2-9B-it, Gemma-2-27B-it                                            | HuggingFace (Google)                                  | CC BY-NC 4.0 / Google Research Terms              |
| Llama-3.3-70B-Instruct, Llama-3.1-405B-Instruct-Turbo                    | HuggingFace (Meta AI)                                 | Meta Llama 3 Community License Agreement          |
| ClimateGPT, GeoGPT                                                       | HuggingFace                                           | License provided in original repo (research only) |
| HuggingFace Transformers                                                 | [GitHub](https://github.com/huggingface/transformers) | Apache License 2.0                                |
| Accelerate                                                               | [GitHub](https://github.com/huggingface/accelerate)   | Apache License 2.0                                |
| Ray                                                                      | [GitHub](https://github.com/ray-project/ray)          | Apache License 2.0                                |
| NumPy, SciPy, Pandas                                                     | PyPI / open-source                                    | BSD / MIT Licenses                                |


## Data Source and Usage Statement

The benchmark dataset introduced in this paper was independently constructed by the authors. All questions and materials were derived and reformulated from our available university-level content in atmospheric science-related courses. These materials include lecture notes, problem sets, and instructional examples used for teaching at our institution.

No proprietary, copyrighted, or scraped content was included in the dataset. The resulting benchmark is intended solely for academic research and educational use. We confirm that the dataset does not contain any personal information, and sensitive data that may negatively impact society.

To the best of our knowledge, this benchmark complies with relevant institutional and academic usage policies, and poses no legal or ethical risk for public release.


## Broader Impact

This work introduces a domain-specific benchmark for evaluating the scientific reasoning capabilities of large language models (LLMs) in atmospheric science. By promoting rigorous, skill-oriented evaluation across both multiple-choice and open-ended formats, our benchmark contributes positively to the development of more trustworthy AI systems in climate-related research, education, and decision-support.

On the positive side, this benchmark can help researchers and developers identify reasoning gaps in current LLMs, accelerate the creation of more robust models, and inform responsible applications of LLMs in science communication and environmental analysis. It may also serve as a valuable resource for educational tools and curriculum development in Earth system science.

However, we acknowledge potential risks. Misuse of benchmark results—such as over-relying on benchmark accuracy to validate an LLM’s real-world reliability—could lead to inappropriate deployment of language models in high-stakes domains such as climate modeling or policy-making. Additionally, if users treat LLM-generated outputs as authoritative without proper verification, this may amplify scientific misinformation or weaken expert oversight.

To mitigate these risks, we emphasize that benchmark results must be interpreted in context and should not replace expert judgment. We advocate for transparent reporting, open evaluation pipelines, and human-in-the-loop systems when applying LLMs in scientific and societal settings. Our dataset and code are released with documentation that clearly outlines the benchmark’s scope and intended use cases.

