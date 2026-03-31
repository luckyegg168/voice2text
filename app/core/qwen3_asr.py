"""Qwen3-ASR 模型封裝"""

import gc
from typing import Optional

import numpy as np

from app.core.config import get_settings

# ── Truly-lazy imports ───────────────────────────────────────────────────────
# torch / qwen_asr are imported only when first needed so that a bare
# ``import app.core.qwen3_asr`` never loads heavy C extensions into the
# process.  This prevents PySide6/shiboken's update_mapping() from
# encountering partially-initialised pandas/sklearn during GUI startup,
# which causes the fatal "_pandas_datetime_CAPI" crash.

_torch_mod = None   # cached: torch module, or False if unavailable
_qwen_cls  = None   # cached: Qwen3ASRModel class, or False if unavailable


def _torch():
    """Return the torch module, or None when not installed."""
    global _torch_mod
    if _torch_mod is None:
        try:
            import torch as _t  # noqa: PLC0415
            _torch_mod = _t
        except ImportError:
            _torch_mod = False
    return _torch_mod if _torch_mod is not False else None


def _qwen3_cls():
    """Return Qwen3ASRModel class, or None when not installed."""
    global _qwen_cls
    if _qwen_cls is None:
        try:
            from qwen_asr import Qwen3ASRModel as _cls  # noqa: PLC0415
            _qwen_cls = _cls
        except ImportError:
            _qwen_cls = False
    return _qwen_cls if _qwen_cls is not False else None


_settings = get_settings()

_model_cache: Optional[object] = None
_current_model_id: Optional[str] = None


def is_available() -> bool:
    """回傳 torch 和 qwen-asr 是否均已安裝"""
    return _torch() is not None and _qwen3_cls() is not None


def _get_dtype():
    """取得 torch dtype"""
    t = _torch()
    if t is None:
        return None
    dtype_map = {
        "float16": t.float16,
        "bfloat16": t.bfloat16,
        "float32": t.float32,
    }
    return dtype_map.get(_settings.dtype, t.float16)


def _get_device() -> str:
    """取得設備"""
    t = _torch()
    if t is None:
        return "cpu"
    if _settings.device == "cuda" and t.cuda.is_available():
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
    t = _torch()
    if t is None:
        raise RuntimeError(
            "torch 未安裝。請執行：01setup.ps1 重新安裝依賴，或手動：pip install torch"
        )
    Qwen3ASRModel = _qwen3_cls()
    if Qwen3ASRModel is None:
        raise RuntimeError(
            "qwen-asr 未安裝。請執行：01setup.ps1 重新安裝依賴，或手動：pip install qwen-asr"
        )

    global _model_cache, _current_model_id

    if _model_cache is not None and _current_model_id == model_id:
        return _model_cache

    if _model_cache is not None:
        del _model_cache
        gc.collect()
        if t.cuda.is_available():
            t.cuda.empty_cache()

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
        t = _torch()
        if t is not None and t.cuda.is_available():
            t.cuda.empty_cache()


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
