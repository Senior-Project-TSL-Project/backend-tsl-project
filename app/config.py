"""
Application Configuration
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import torch

# Load environment variables from .env file
load_dotenv()

# Model Configuration
MODEL_PATH = Path(__file__).parent.parent / "model"
PREFIX_TEXT = "translate Thai to TSL "
MAX_LENGTH = 32

# Device Configuration
DEVICE = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"

# API Configuration
API_TITLE = "Thai Sign Language API"
API_DESCRIPTION = "API for converting Thai text to sign language glosses using MT5 model"
API_VERSION = "1.0.0"

# Dify LLM API Configuration
DIFY_API_URL = os.getenv("DIFY_API_URL", "https://api.dify.ai/v1")
DIFY_API_KEY = os.getenv("DIFY_API_KEY", "")
