"""
Models module for generating responses to physics problems.

This module contains implementations for different LLM models.
"""

# Import base models
from .api_base import APIBaseModel
from .local_base import LocalBaseModel

# Import API-based models
from .openai_base import (
    OpenAIBaseModel,
    GPT4oModel,
    GPT4oMiniModel,
    GPT35TurboModel,
    O3MiniModel,
    O1Model
)
from .together_base import (
    TogetherBaseModel,
    LlamaModel,
    MistralModel,
    ClaudeModel,
    DeepSeekR1DistillLlama70BModel,
    QwQ32BPreviewModel,
    Qwen2572BInstructTurboModel,
    Llama31405BInstructTurboModel,
    Qwen3235BA22BFp8TputModel,
    Llama3370BInstructModel_Togehter,
    Qwen257BInstructModel_Togehter
)
from .deepseek_base import (
    DeepSeekBaseModel,
    DeepSeekR1Model,
    DeepSeekV3Model
)
from .google_base import (
    GoogleBaseModel,
    GeminiModel,
    GeminiFlashExpModel
)

# Import local models
from .huggingface_base import (
    HuggingFaceBaseModel,
    LlamaLocalModel,
    MistralLocalModel,
    PhiLocalModel,
    QwenMathModel,
    DeepSeekMathModel,
    DeepSeekMathRLModel,
    ClimateGPT70BModel,
    ClimateGPT7BModel,
    Qwen2532BInstructModel,
    Qwen253BInstructModel,
    Qwen257BInstructModel,
    Qwen25Coder32BInstructModel,
    Qwen25Math15BInstructModel,
    Qwen25Math72BInstructModel,
    Qwen25Math7BInstructModel,
    Gemma227BITModel,
    Gemma29BITModel,
    Llama3370BInstructModel,
    Qwen2572BGeoGPTModel,
)



# Dictionary mapping base names to their model registries
BASE_REGISTRY = {
    # API-based models
    "openai": {
        "gpt4o": GPT4oModel,
        "gpt4o-mini": GPT4oMiniModel,
        "gpt35-turbo": GPT35TurboModel,
        "o3-mini": O3MiniModel,
        "o1": O1Model,
        "gpto1": O1Model,  # Alias for o1
    },
    "together": {
        "llama": LlamaModel,
        "mistral": MistralModel,
        "claude": ClaudeModel,
        "DeepSeek-R1-Distill-Llama-70B": DeepSeekR1DistillLlama70BModel,
        "QwQ-32B-Preview": QwQ32BPreviewModel,
        "Qwen2.5-72B-Instruct-Turbo": Qwen2572BInstructTurboModel,
        "Llama-3.1-405B-Instruct-Turbo": Llama31405BInstructTurboModel,
        "Qwen3-235B-A22B-fp8-tput": Qwen3235BA22BFp8TputModel,
        "Llama-3.3-70B-Instruct": Llama3370BInstructModel_Togehter,
        "Qwen2.5-7B-Instruct-Turbo": Qwen257BInstructModel_Togehter
    },
    "deepseek": {
        "r1": DeepSeekR1Model,
        "v3": DeepSeekV3Model,
    },
    "google": {
        "gemini-2.0-flash-thinking-exp-01-21": GeminiModel,
        "gemini-2.0-flash-exp": GeminiFlashExpModel,
    },
    # Local models
    "huggingface": {
        "llama": LlamaLocalModel,
        "mistral": MistralLocalModel,
        "phi": PhiLocalModel,
        "qwen-math": QwenMathModel,
        "deepseek-math-7b-instruct": DeepSeekMathModel,
        "deepseek-math-7b-rl": DeepSeekMathRLModel,
        "climategpt-70b": ClimateGPT70BModel,
        "climategpt-7b": ClimateGPT7BModel,
        "Qwen2.5-32B-Instruct": Qwen2532BInstructModel,
        "Qwen2.5-3B-Instruct": Qwen253BInstructModel,
        "Qwen2.5-7B-Instruct": Qwen257BInstructModel,
        "Qwen2.5-Coder-32B-Instruct": Qwen25Coder32BInstructModel,
        "Qwen2.5-Math-1.5B-Instruct": Qwen25Math15BInstructModel,
        "Qwen2.5-Math-72B-Instruct": Qwen25Math72BInstructModel,
        "Qwen2.5-Math-7B-Instruct": Qwen25Math7BInstructModel,
        "gemma-2-27b-it": Gemma227BITModel,
        "gemma-2-9b-it": Gemma29BITModel,
        "Llama-3.3-70B-Instruct": Llama3370BInstructModel,
        "Qwen2.5-72B-GeoGPT": Qwen2572BGeoGPTModel,
    },

}

def get_model(model_name, base_name):
    """
    Get the model implementation for the given model name and base.

    Args:
        model_name (str): Name of the model
        base_name (str): Name of the base model type

    Returns:
        Model class: The model implementation

    Raises:
        ValueError: If the model or base is not supported
    """
    if base_name not in BASE_REGISTRY:
        raise ValueError(f"Base {base_name} is not supported. Supported bases: {list(BASE_REGISTRY.keys())}")

    base_models = BASE_REGISTRY[base_name]
    if model_name not in base_models:
        raise ValueError(f"Model {model_name} is not supported for base {base_name}. Supported models: {list(base_models.keys())}")

    return base_models[model_name]
