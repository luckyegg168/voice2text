"""簡繁轉換 API 路由"""

from fastapi import APIRouter

from app.api.models import ConversionRequest, ConversionResponse
from app.core.opencc_engine import opencc_engine

router = APIRouter(prefix="", tags=["conversion"])


@router.post("/convert", response_model=ConversionResponse)
async def convert(request: ConversionRequest) -> ConversionResponse:
    """簡繁轉換"""
    text = opencc_engine.convert(request.text, request.mode)

    return ConversionResponse(
        text=text,
        mode=request.mode,
    )
