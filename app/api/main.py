"""FastAPI 主程式"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.models import HealthResponse
from app.api.routes import conversion, history, transcription, translation
from app.core import qwen3_asr

app = FastAPI(
    title="Voice2Text API",
    description="語音辨識發送文字系統 API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transcription.router)
app.include_router(translation.router)
app.include_router(conversion.router)
app.include_router(history.router)


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """健康檢查"""
    return HealthResponse(
        status="healthy",
        model_loaded=qwen3_asr.is_model_loaded(),
        model_name=qwen3_asr.get_loaded_model_id(),
        translation_api="unknown",
    )


@app.get("/")
async def root() -> dict:
    """根路由"""
    return {
        "name": "Voice2Text API",
        "version": "0.1.0",
        "docs": "/docs",
    }
