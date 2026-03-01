"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from .config import ModelConfig


class PredictRequest(BaseModel):
    """Request model for prediction endpoint."""
    text: str = Field(
        ...,
        description="Thai text to convert to sign language gloss",
        min_length=1,
        max_length=512,
        examples=["สวัสดีครับ"]
    )
    model: str = Field(
        default="mt5-tsl",
        description="Model to use for prediction. Available: mt5-tsl, llm-gemini-2.5-pro",
        examples=["mt5-tsl", "llm-gemini-2.5-pro"]
    )
    
    @field_validator('model')
    @classmethod
    def validate_model(cls, v: str) -> str:
        """Validate model ID exists in registry."""
        from .config import get_available_models
        available = get_available_models()
        if v not in available:
            raise ValueError(f"Invalid model. Available models: {', '.join(available)}")
        return v


class PredictResponse(BaseModel):
    """Response model for prediction endpoint."""
    input_text: str = Field(..., description="Original input text")
    gloss: str = Field(..., description="Predicted sign language gloss")
    confidence: float = Field(
        ..., 
        description="Confidence score (0-100%), If model is mt5, confidence is estimated based on token-level probabilities, If model is llm, confidence is estimated based on model's output scores.",
        ge=0,
        le=100
    )


class ModelInfo(BaseModel):
    id: str
    model: str
    disabled: bool

class HealthResponse(BaseModel):
    status: str
    models: dict[str, ModelInfo]
    device: str
 
class ModelResponse(BaseModel):
    models: list[ModelConfig]