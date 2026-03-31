"""OpenCC 簡繁轉換引擎"""

from typing import Optional

import opencc

from app.core.constants import OpenCCMode


class OpenCCEngine:
    """OpenCC 簡繁轉換引擎"""

    _instance: Optional["OpenCCEngine"] = None
    _converter: Optional[opencc.OpenCC] = None
    _current_mode: Optional[str] = None

    def __new__(cls) -> "OpenCCEngine":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _get_converter(self, mode: str) -> opencc.OpenCC:
        """取得轉換器"""
        if self._converter is None or self._current_mode != mode:
            self._converter = opencc.OpenCC(mode)
            self._current_mode = mode
        return self._converter

    def convert(self, text: str, mode: str = "s2t") -> str:
        """轉換文字

        Args:
            text: 原始文字
            mode: 轉換模式 (s2t, t2s, s2tw, tw2s, s2hk, hk2s)

        Returns:
            轉換後文字
        """
        if not text:
            return text

        converter = self._get_converter(mode)
        return converter.convert(text)

    def s2t(self, text: str) -> str:
        """簡體→繁體"""
        return self.convert(text, "s2t")

    def t2s(self, text: str) -> str:
        """繁體→簡體"""
        return self.convert(text, "t2s")

    def s2tw(self, text: str) -> str:
        """簡體→臺灣正體"""
        return self.convert(text, "s2tw")

    def tw2s(self, text: str) -> str:
        """臺灣正體→簡體"""
        return self.convert(text, "tw2s")

    def s2hk(self, text: str) -> str:
        """簡體→香港繁體"""
        return self.convert(text, "s2hk")

    def hk2s(self, text: str) -> str:
        """香港繁體→簡體"""
        return self.convert(text, "hk2s")

    @staticmethod
    def get_available_modes() -> list[dict[str, str]]:
        """取得可用的轉換模式"""
        return [
            {"mode": "s2t", "name": "簡體→繁體", "description": "中國大陸簡體到繁體"},
            {"mode": "t2s", "name": "繁體→簡體", "description": "繁體到中國大陸簡體"},
            {"mode": "s2tw", "name": "簡體→臺灣正體", "description": "簡體到臺灣正體"},
            {"mode": "tw2s", "name": "臺灣正體→簡體", "description": "臺灣正體到簡體"},
            {"mode": "s2hk", "name": "簡體→香港繁體", "description": "簡體到香港繁體"},
            {"mode": "hk2s", "name": "香港繁體→簡體", "description": "香港繁體到簡體"},
        ]


opencc_engine = OpenCCEngine()
