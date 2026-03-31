"""Qwen3-ASR 模型封裝"""

import gc
from typing import Optional

import numpy as np

from app.core.config import get_settings

# 延遲匯入 torch / qwen_asr，讓 GUI 在未安裝模型時仍能啟動
try:
    import torch
    _TORCH_AVAILABLE = True
except ImportError:
    _TORCH_AVAILABLE = False
    torch = None  # type: ignore[assignment]

try:
    from qwen_asr import Qwen3ASRModel
    _QWEN_ASR_AVAILABLE = True
except ImportError:
    _QWEN_ASR_AVAILABLE = False
    Qwen3ASRModel = None  # type: ignore[assignment,misc]

_settings = get_settings()

_model_cache: Optional["Qwen3ASRModel"] = None  # type: ignore[type-arg]
_current_model_id: Optional[str] = None


def is_available() -> bool:
    """回傳 torch 和 qwen-asr 是否均已安裝"""
    return _TORCH_AVAILABLE and _QWEN_ASR_AVAILABLE


def _get_dtype():
    """取得 torch dtype"""
    if not _TORCH_AVAILABLE:
        return None
    dtype_map = {
        "float16": torch.float16,
        "bfloat16": torch.bfloat16,
        "float32": torch.float32,
    }
    return dtype_map.get(_settings.dtype, torch.float16)


def _get_device() -> str:
    """取得設備"""
    if not _TORCH_AVAILABLE:
        return "cpu"
    if _settings.device == "cuda" and torch.cuda.is_available():
        return "cuda:0"
    return "cpu"


def load_model(model_id: str = "Qwen/Qwen3-ASR-0.6B"):
    """載入模型（帶快取）

    Args:
        model_id: 模型 ID

    Returns:
        Qwen3ASRModel 實例

    Raises:
        RuntimeError: 若 torch / qwen-asr 未安裝
    """
    if not _TORCH_AVAILABLE:
        raise RuntimeError(
            "torch 未安裝。請執行：01setup.ps1 重新安裝依賴，或手動：pip install torch"
        )
    if not _QWEN_ASR_AVAILABLE:
        raise RuntimeError(
            "qwen-asr 未安裝。請執行：01setup.ps1 重新安裝依賴，或手動：pip install qwen-asr"
        )

    global _model_cache, _current_model_id

    if _model_cache is not None and _current_model_id == model_id:
        return _model_cache

    if _model_cache is not None:
        del _model_cache
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    _model_cache = Qwen3ASRModel.from_pretrained(
        model_id,
        dtype=_get_dtype(),
        device_map=_get_device(),
        max_inference_batch_size=32,
        max_new_tokens=256,
    )
    _current_model_id = model_id
    return _model_cache


def unload_model() -> None:
    """卸載模型"""
    global _model_cache, _current_model_id

    if _model_cache is not None:
        del _model_cache
        _model_cache = None
        _current_model_id = None
        gc.collect()
        if _TORCH_AVAILABLE and torch.cuda.is_available():
            torch.cuda.empty_cache()


def is_model_loaded() -> bool:
    """檢查模型是否已載入"""
    return _model_cache is not None


def get_loaded_model_id() -> Optional[str]:
    """取得已載入的模型 ID"""
    return _current_model_id


def transcribe(
    audio_input: bytes | np.ndarray,
    model_id: Optional[str] = None,
    language: Optional[str] = None,
    device: Optional[str] = None,
    return_segments: bool = False,
) -> tuple[str, str]:
    """轉寫音訊

    Args:
        audio_input: 音訊資料（bytes WAV 或 np.ndarray）
        model_id: 模型 ID（預設使用 settings 中的預設模型）
        language: 語言（None = 自動偵測）
        device: 設備（會忽略，使用 settings 中的設定）
        return_segments: 是否回傳分段

    Returns:
        (文字, 語言)
    """
    effective_model_id = model_id or _settings.default_model

    model = load_model(effective_model_id)

    if isinstance(audio_input, bytes):
        audio_io = __import__("io").BytesIO(audio_input)
        from scipy.io import wavfile

        sr, data = wavfile.read(audio_io)
        if data.dtype != np.float32:
            data = data.astype(np.float32) / 32768.0
        if data.ndim > 1:
            data = data[:, 0]
        audio_input = (data, sr)

    results = model.transcribe(
        audio=audio_input,
        language=language,
    )

    if not results:
        return "", "unknown"

    return results[0].text, results[0].language
