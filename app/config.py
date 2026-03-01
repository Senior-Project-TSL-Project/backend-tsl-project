"""
Application Configuration
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import torch
from dataclasses import dataclass
from typing import Literal

# Load environment variables from .env file
load_dotenv()

# Model Configuration
# Path(__file__).parent.parent / "model" , HomieZ09/TSL-mt5
MODEL_PATH = Path(__file__).parent.parent / "model"
PREFIX_TEXT = "translate Thai to TSL "
MAX_LENGTH = 32

# Device Configuration
DEVICE = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"

# API Configuration
API_TITLE = "Thai Sign Language API"
API_DESCRIPTION = "API for converting Thai text to sign language glosses using MT5 model"
API_VERSION = "1.2.1"

# Dify LLM API Configuration
DIFY_API_URL = os.getenv("DIFY_API_URL", "https://api.dify.ai/v1")
DIFY_API_KEY = os.getenv("DIFY_API_KEY", "")


# Model Registry Configuration
@dataclass
class ModelConfig:
    """Configuration for each model."""
    id: str
    name: str
    type: Literal["mt5", "llm"]
    service_name: str  # "model_service" or "llm_service"
    supports_streaming: bool = False
    description: str = ""


# Model Registry - Add new models here
MODEL_REGISTRY = {
    "mt5-tsl": ModelConfig(
        id="mt5-tsl",
        name="TSL (mT5)",
        type="mt5",
        service_name="model_service",
        supports_streaming=False,
        description="mT5-based Thai Sign Language translation model"
    ),
    "llm-gemini-2.5-pro": ModelConfig(
        id="llm-gemini-2.5-pro",
        name="TSL (Gemini 2.5 Pro LLM)",
        type="llm",
        service_name="llm_service",
        supports_streaming=True,
        description="LLM-based Thai Sign Language translation using Gemini 2.5 Pro"
    ),
    # Future models can be added here:
    # "llm-gemini-3": ModelConfig(
    #     id="llm-gemini-3",
    #     name="TSL (Gemini 3.0)",
    #     type="llm",
    #     service_name="llm_service_v2",
    #     supports_streaming=True,
    #     description="Next generation LLM model"
    # ),
    # "mt5-esl": ModelConfig(
    #     id="mt5-esl",
    #     name="ESL (mT5)",
    #     type="mt5",
    #     service_name="model_service_english",
    #     supports_streaming=False,
    #     description="mT5-based English Sign Language translation model"
    # ),
}


def get_available_models() -> list[str]:
    """Get list of available model IDs."""
    return list(MODEL_REGISTRY.keys())


def get_model_config(model_id: str) -> ModelConfig:
    """Get configuration for a specific model."""
    if model_id not in MODEL_REGISTRY:
        raise ValueError(f"Invalid model ID: {model_id}. Available models: {', '.join(get_available_models())}")
    return MODEL_REGISTRY[model_id]
