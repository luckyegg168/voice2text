"""音訊處理模組 - 錄音、格式轉換"""

import io
import threading
from typing import Callable, Optional

import numpy as np
import sounddevice as sd
from scipy.io import wavfile
from scipy.signal import resample_poly


class AudioProcessor:
    """音訊處理器"""

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        dtype: np.dtype = np.float32,
    ):
        self.sample_rate = sample_rate
        self.channels = channels
        self.dtype = dtype
        self._stop_event = threading.Event()

    def stop(self) -> None:
        """停止錄音"""
        self._stop_event.set()

    def record(
        self,
        duration: float,
        callback: Optional[Callable[[float], None]] = None,
    ) -> np.ndarray:
        """錄製音訊

        Args:
            duration: 最大錄製時長（秒）
            callback: 即時回調，接收 rms level (float)

        Returns:
            音訊資料 (numpy array)
        """
        self._stop_event.clear()
        recording = []

        def audio_callback(indata: np.ndarray, frames: int, time, status) -> None:
            if status:
                print(f"錄音狀態: {status}")
            recording.append(indata.copy())
            if callback is not None:
                rms = float(np.sqrt(np.mean(indata[:, 0] ** 2)))
                callback(rms)

        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype=self.dtype,
            callback=audio_callback,
        ):
            elapsed = 0.0
            while elapsed < duration:
                if self._stop_event.wait(timeout=0.1):
                    break
                elapsed += 0.1

        if not recording:
            return np.zeros(0, dtype=np.float32)

        audio_data = np.concatenate(recording, axis=0)
        if audio_data.ndim > 1:
            audio_data = audio_data[:, 0]

        return audio_data

    def record_until_silence(
        self,
        max_duration: float = 30.0,
        silence_threshold: float = 0.01,
        silence_duration: float = 1.0,
        callback: Optional[Callable[[np.ndarray], None]] = None,
    ) -> np.ndarray:
        """錄製音訊直到靜音

        Args:
            max_duration: 最大錄製時長（秒）
            silence_threshold: 靜音閾值
            silence_duration: 視為靜音的持續時間（秒）
            callback: 即時回調

        Returns:
            音訊資料
        """
        recording = []
        silence_frames = 0
        frame_rate = self.sample_rate
        silence_frames_threshold = int(silence_duration * frame_rate)

        def audio_callback(indata: np.ndarray, frames: int, time, status) -> None:
            nonlocal silence_frames
            if status:
                print(f"錄音狀態: {status}")

            audio = indata[:, 0]
            recording.append(audio)

            rms = np.sqrt(np.mean(audio**2))
            if rms < silence_threshold:
                silence_frames += frames
            else:
                silence_frames = 0

            if callback is not None:
                callback(rms)

        stream = sd.InputStream(
            samplerate=frame_rate,
            channels=self.channels,
            dtype=self.dtype,
            callback=audio_callback,
        )

        with stream:
            start_time = sd.get_stream().time
            while True:
                sd.sleep(100)
                current_time = sd.get_stream().time
                if current_time - start_time > max_duration:
                    break
                if silence_frames >= silence_frames_threshold and len(recording) > 1:
                    break

        audio_data = np.concatenate(recording, axis=0)
        return audio_data

    @staticmethod
    def load_wav(file_path: str) -> tuple[np.ndarray, int]:
        """載入 WAV 檔案

        Args:
            file_path: 檔案路徑

        Returns:
            (音訊資料, 取樣率)
        """
        sr, data = wavfile.read(file_path)
        if data.dtype != np.float32:
            data = data.astype(np.float32) / 32768.0
        return data, sr

    @staticmethod
    def save_wav(file_path: str, audio_data: np.ndarray, sample_rate: int) -> None:
        """儲存 WAV 檔案

        Args:
            file_path: 檔案路徑
            audio_data: 音訊資料
            sample_rate: 取樣率
        """
        wavfile.write(file_path, sample_rate, (audio_data * 32768).astype(np.int16))

    @staticmethod
    def convert_to_16kmono(audio_data: np.ndarray, source_sr: int) -> np.ndarray:
        """轉換為 16kHz mono

        Args:
            audio_data: 原始音訊
            source_sr: 原始取樣率

        Returns:
            轉換後音訊
        """
        target_sr = 16000

        if audio_data.ndim > 1:
            audio_data = audio_data[:, 0]

        if source_sr != target_sr:
            gcd = np.gcd(target_sr, source_sr)
            audio_data = resample_poly(audio_data, target_sr // gcd, source_sr // gcd)

        return audio_data.astype(np.float32)

    @staticmethod
    def bytes_to_audio(audio_bytes: bytes, source_sr: int = 16000) -> np.ndarray:
        """將位元組轉換為音訊資料

        Args:
            audio_bytes: WAV 位元組
            source_sr: 取樣率

        Returns:
            音訊資料
        """
        audio_io = io.BytesIO(audio_bytes)
        sr, data = wavfile.read(audio_io)
        if data.dtype != np.float32:
            data = data.astype(np.float32) / 32768.0
        if data.ndim > 1:
            data = data[:, 0]
        return data

    @staticmethod
    def audio_to_bytes(audio_data: np.ndarray, sample_rate: int = 16000) -> bytes:
        """將音訊資料轉換為 WAV 位元組

        Args:
            audio_data: 音訊資料
            sample_rate: 取樣率

        Returns:
            WAV 位元組
        """
        buffer = io.BytesIO()
        wavfile.write(buffer, sample_rate, (audio_data * 32768).astype(np.int16))
        buffer.seek(0)
        return buffer.read()
