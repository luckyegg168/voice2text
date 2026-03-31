"""翻譯 API 路由"""

from fastapi import APIRouter, HTTPException

from app.api.models import TranslationRequest, TranslationResponse
from app.core.translation_service import get_translation_service

router = APIRouter(prefix="", tags=["translation"])


@router.post("/translate", response_model=TranslationResponse)
async def translate(request: TranslationRequest) -> TranslationResponse:
    """翻譯文字"""
    try:
        service = get_translation_service()

        translated_text = await service.translate(
            text=request.text,
            target_language=request.target_language,
            source_language=request.source_language,
        )

        return TranslationResponse(
            text=translated_text,
            source_language=request.source_language or "auto",
            target_language=request.target_language,
            model=service.model,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
