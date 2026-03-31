"""API Request/Response Models"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ASRRequest(BaseModel):
    """ASR 請求"""

    audio: str = Field(..., description="Base64 encoded WAV audio")
    model: str = Field(default="Qwen/Qwen3-ASR-0.6B", description="Model ID")
    language: Optional[str] = Field(default=None, description="Language code")
    return_time_stamps: bool = Field(default=False)
    hotwords_group: Optional[str] = Field(default=None)


class ASRResponse(BaseModel):
    """ASR 回應"""

    text: str
    language: str
    chunks: Optional[list[dict]] = None


class TranscriptionRequest(BaseModel):
    """轉寫請求（OpenAI-compatible）"""

    file: bytes = Field(..., description="Audio file binary")
    model: str = Field(default="Qwen/Qwen3-ASR-0.6B")
    language: Optional[str] = Field(default=None)


class TranscriptionResponse(BaseModel):
    """轉寫回應"""

    text: str
    language: str
    duration: Optional[float] = None


class TranslationRequest(BaseModel):
    """翻譯請求"""

    text: str = Field(..., description="Text to translate")
    target_language: str = Field(..., description="Target language")
    source_language: Optional[str] = Field(default=None)


class TranslationResponse(BaseModel):
    """翻譯回應"""

    text: str
    source_language: str
    target_language: str
    model: str


class ConversionRequest(BaseModel):
    """轉換請求"""

    text: str = Field(..., description="Text to convert")
    mode: str = Field(default="s2t", description="Conversion mode")


class ConversionResponse(BaseModel):
    """轉換回應"""

    text: str
    mode: str


class HistoryItem(BaseModel):
    """歷史紀錄項目"""

    id: int
    text: str
    language: Optional[str] = None
    model: Optional[str] = None
    audio_path: Optional[str] = None
    duration: Optional[float] = None
    translated_text: Optional[str] = None
    created_at: datetime


class HistoryListResponse(BaseModel):
    """歷史紀錄列表回應"""

    items: list[HistoryItem]
    total: int
    limit: int
    offset: int


class HealthResponse(BaseModel):
    """健康檢查回應"""

    status: str
    model_loaded: bool
    model_name: Optional[str] = None
    translation_api: str = "unknown"
