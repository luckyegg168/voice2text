"""轉寫 API 路由"""

import base64
from io import BytesIO

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from scipy.io import wavfile

from app.api.models import ASRRequest, ASRResponse, TranscriptionResponse
from app.core import audio_processor, qwen3_asr

router = APIRouter(prefix="/v1/audio", tags=["transcription"])


@router.post("/transcriptions", response_model=TranscriptionResponse)
async def transcribe_file(
    file: UploadFile = File(...),
    model: str = Form(default="Qwen/Qwen3-ASR-0.6B"),
    language: str = Form(default=None),
) -> TranscriptionResponse:
    """轉寫音訊檔案（OpenAI-compatible endpoint）"""
    try:
        audio_bytes = await file.read()

        try:
            sr, data = wavfile.read(BytesIO(audio_bytes))
            if data.dtype != float:
                data = data.astype(float) / 32768.0
            if data.ndim > 1:
                data = data[:, 0]
            audio_input = (data, sr)
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Invalid audio file format. Please upload a WAV file.",
            )

        text, detected_language = qwen3_asr.transcribe(
            audio_input=audio_input,
            model_id=model,
            language=language,
        )

        return TranscriptionResponse(
            text=text,
            language=detected_language or language or "unknown",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/asr", response_model=ASRResponse)
async def asr_endpoint(request: ASRRequest) -> ASRResponse:
    """ASR 原生 endpoint"""
    try:
        audio_bytes = base64.b64decode(request.audio)

        sr, data = wavfile.read(BytesIO(audio_bytes))
        if data.dtype != float:
            data = data.astype(float) / 32768.0
        if data.ndim > 1:
            data = data[:, 0]
        audio_input = (data, sr)

        text, language = qwen3_asr.transcribe(
            audio_input=audio_input,
            model_id=request.model,
            language=request.language,
        )

        return ASRResponse(
            text=text,
            language=language or "unknown",
            chunks=None,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
