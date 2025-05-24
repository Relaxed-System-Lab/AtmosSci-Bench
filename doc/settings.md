# Settings

## Hyperparameters

To ensure fair comparison and consistent evaluation, we standardize the inference-time hyperparameters across all models in accordance with their capabilities and design constraints.

For **reasoning-optimized models**, we use a maximum context length of **32K tokens**. This decision is motivated by the fact that *DeepSeek-R1* has a fixed 32K context window that cannot be modified. To maintain fairness, we adopt the same 32K limit for all reasoning models, including *GPT-o1*, *QwQ-32B-Preview*, and *Gemini-2.0-Flash-Thinking-Exp (01-21)*. This configuration provides sufficient space for long-form reasoning and multi-step inference, ensuring that reasoning performance is not artificially constrained by token limits.

Additionally, most reasoning models—such as *GPT-o1* and *DeepSeek-R1*—do not support customized decoding parameters like `temperature`, `top_p`, or `repetition_penalty`. Therefore, we use default hyperparameters for all models across all categories to ensure evaluation consistency and reproducibility.

For **instruction-tuned**, **math-augmented**, and **domain-specific models**, we set the maximum token limit to **8K**, which provides ample context for solving our benchmark tasks given the typical response lengths of these models.

---

## Experimental Compute Resources

We categorize LLM inference into two groups based on deployment method: **API-based** and **local-based**.

* **API-based**: Models in this category are hosted by providers such as OpenAI, Google, Deepseek, and TogetherAI. We access these models via public inference APIs. To accelerate large-scale evaluation, we utilize parallel execution using the `Ray` Python library, which enables concurrent API requests. Total inference time varies depending on the model and the infrastructure provider's throughput.

* **Local-based**: These models are available through HuggingFace and executed locally using the HuggingFace `transformers` library, with acceleration enabled via `Accelerate` .
  We run evaluations on two hardware setups:

  1. A single machine with 8×NVIDIA RTX 4090 GPUs
  2. Two separate nodes, each equipped with 4×NVIDIA A800 GPUs

  For a 70B non-reasoning model, a full evaluation run requires approximately **90 hours** with a batch size of 4. In contrast, a 7B model can be evaluated in about **6 hours** using a batch size of 64.
