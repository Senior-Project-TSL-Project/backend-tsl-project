"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, Field


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
        default="mt5",
        description="Model to use for prediction",
        examples=["mt5", "llm"]
    )


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


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str
    model_loaded: bool
    device: str
