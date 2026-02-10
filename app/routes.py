"""
API Routes
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from .schemas import PredictRequest, PredictResponse, HealthResponse
from .services.model_service import model_service
from .services.llm_service import llm_service
from .config import DEVICE
from .auth import verify_api_key

router = APIRouter()

@router.get("/", tags=["Root"])
async def root():
    return {
        "message": "Thai Sign Language API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    '''Health check endpoint to verify API and model status.'''
    return HealthResponse(
        status="healthy",
        model_loaded=model_service.is_loaded,
        device=DEVICE
    )


@router.post("/predict", response_model=PredictResponse, tags=["Prediction"])
async def predict(request: PredictRequest, api_key: str = Depends(verify_api_key)):
    if request.model == "mt5":
        if not model_service.is_loaded:
            raise HTTPException(
                status_code=503,
                detail="Model not loaded. Please try again later."
            )
        try:
            gloss, confidence = model_service.predict_gloss(request.text)
            
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
    elif request.model == "llm":
        try:
            gloss, confidence = await llm_service.predict_gloss(request.text)
            
            return PredictResponse(
                input_text=request.text,
                gloss=gloss,
                confidence=round(confidence, 2)
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"LLM prediction failed: {str(e)}"
            )
    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid model specified. Please use 'mt5' or 'llm'."
        )


@router.post("/predict/stream", tags=["Prediction"])
async def predict_stream(request: PredictRequest, api_key: str = Depends(verify_api_key)):
    """
    Streaming prediction endpoint - returns text chunks as Server-Sent Events.
    Only supports LLM model.
    """
    if request.model != "llm":
        raise HTTPException(
            status_code=400,
            detail="Streaming only supports 'llm' model."
        )
    
    async def generate():
        try:
            async for chunk in llm_service.predict_gloss_stream(request.text):
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