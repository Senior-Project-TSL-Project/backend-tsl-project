"""
API Routes
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from .schemas import PredictRequest, PredictResponse, HealthResponse, ModelInfo, ModelResponse
from .services.model_service import model_service
from .services.llm_service import llm_service
from .config import DEVICE, MODEL_REGISTRY, get_model_config, get_available_models, API_VERSION
from .auth import verify_api_key

router = APIRouter()


def get_service(service_name: str):
    """Get the appropriate service instance based on service name."""
    services = {
        "model_service": model_service,
        "llm_service": llm_service,
        # Add new services here as needed
    }
    return services.get(service_name)

@router.get("/", tags=["Root"])
async def root():
    return {
        "message": "Thai Sign Language API",
        "version": API_VERSION,
        "docs": "/docs"
    }


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    '''Health check endpoint to verify API and model status.'''
    # Build models dict from registry
    models = {}
    for model_id, config in MODEL_REGISTRY.items():
        service = get_service(config.service_name)
        models[model_id] = ModelInfo(
            id=config.id,
            model=config.name,
            disabled=not service.is_loaded if service else False
        )
    
    return HealthResponse(
        status="healthy",
        models=models,
        device=DEVICE
    )


@router.post("/predict", response_model=PredictResponse, tags=["Prediction"])
async def predict(request: PredictRequest, api_key: str = Depends(verify_api_key)):
    # Validate model ID
    try:
        model_config = get_model_config(request.model)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    
    # Get the appropriate service
    service = get_service(model_config.service_name)
    if not service:
        raise HTTPException(
            status_code=500,
            detail=f"Service '{model_config.service_name}' not found"
        )
    
    # Check if service is loaded
    if not service.is_loaded:
        raise HTTPException(
            status_code=503,
            detail=f"Model '{model_config.name}' not loaded. Please try again later."
        )
    
    # Execute prediction
    try:
        # Check if service has async predict_gloss
        if model_config.type == "llm":
            gloss, confidence = await service.predict_gloss(request.text)
        else:
            gloss, confidence = service.predict_gloss(request.text)
        
        return PredictResponse(
            input_text=request.text,
            gloss=gloss,
            confidence=round(confidence, 2)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


@router.post("/predict/stream", tags=["Prediction"])
async def predict_stream(request: PredictRequest, api_key: str = Depends(verify_api_key)):
    """
    Streaming prediction endpoint - returns text chunks as Server-Sent Events.
    Only supports models with streaming capability.
    """
    # Validate model ID
    try:
        model_config = get_model_config(request.model)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    
    # Check if model supports streaming
    if not model_config.supports_streaming:
        raise HTTPException(
            status_code=400,
            detail=f"Model '{model_config.name}' does not support streaming. Available streaming models: {[k for k, v in MODEL_REGISTRY.items() if v.supports_streaming]}"
        )
    
    # Get the appropriate service
    service = get_service(model_config.service_name)
    if not service:
        raise HTTPException(
            status_code=500,
            detail=f"Service '{model_config.service_name}' not found"
        )
    
    # Check if service is loaded
    if not service.is_loaded:
        raise HTTPException(
            status_code=503,
            detail=f"Model '{model_config.name}' not loaded. Please try again later."
        )
    
    async def generate():
        try:
            async for chunk in service.predict_gloss_stream(request.text):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@router.get("/models", response_model=ModelResponse, tags=["Models"])
async def models(api_key: str = Depends(verify_api_key)):
    """Get list of available models with their configurations."""
    return {
        "models": [get_model_config(model_id) for model_id in get_available_models()]
    }

@router.get("/models-dropdown", response_model=list[ModelInfo], tags=["Models"])
async def models_dropdown(api_key: str = Depends(verify_api_key)):
    """Get list of available models for dropdown selection."""
    models = []
    for model_id, config in MODEL_REGISTRY.items():
        service = get_service(config.service_name)
        models.append(ModelInfo(
            id=config.id,
            model=config.name,
            disabled=not service.is_loaded if service else False
        ))
    
    return models