"""測試音訊處理模組"""

import numpy as np
import pytest


def test_audio_processor_creation():
    """測試 AudioProcessor 建立"""
    from app.core.audio_processor import AudioProcessor

    processor = AudioProcessor(sample_rate=16000, channels=1)
    assert processor.sample_rate == 16000
    assert processor.channels == 1


def test_convert_to_16kmono():
    """測試轉換為 16kHz mono"""
    from app.core.audio_processor import AudioProcessor

    audio = np.random.randn(32000).astype(np.float32)
    result = AudioProcessor.convert_to_16kmono(audio, 32000)

    assert len(result) == 16000
    assert result.dtype == np.float32


def test_audio_bytes_conversion():
    """測試音訊位元組轉換"""
    from app.core.audio_processor import AudioProcessor

    audio = np.zeros(16000, dtype=np.float32)
    audio_bytes = AudioProcessor.audio_to_bytes(audio, 16000)

    assert isinstance(audio_bytes, bytes)
    assert len(audio_bytes) > 0
