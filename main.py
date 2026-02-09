"""
FastAPI Backend for Thai Sign Language Gloss Prediction

This API provides endpoints for converting Thai text to sign language glosses
using a fine-tuned MT5 model.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import API_TITLE, API_DESCRIPTION, API_VERSION
from app.routes import router
from app.services.model_service import model_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for loading and cleaning up model resources.
    """
    try:
        model_service.load_model()
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        raise e
    
    yield
    
    model_service.unload_model()


app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
