"""常數定義"""

from enum import Enum


class OpenCCMode(str, Enum):
    """OpenCC 轉換模式"""

    S2T = "s2t"  # 簡體→繁體
    T2S = "t2s"  # 繁體→簡體
    S2TW = "s2tw"  # 簡體→臺灣正體
    TW2S = "tw2s"  # 臺灣正體→簡體
    S2HK = "s2hk"  # 簡體→香港繁體
    HK2S = "hk2s"  # 香港繁體→簡體


class Device(str, Enum):
    """運算設備"""

    CUDA = "cuda"
    CPU = "cpu"


class DType(str, Enum):
    """資料精度"""

    FLOAT16 = "float16"
    BFLOAT16 = "bfloat16"
    FLOAT32 = "float32"


SUPPORTED_LANGUAGES = [
    "auto",
    "Chinese",
    "English",
    "Cantonese",
    "Japanese",
    "Korean",
    "French",
    "German",
    "Spanish",
    "Portuguese",
    "Italian",
    "Russian",
    "Arabic",
    "Thai",
    "Vietnamese",
    "Indonesian",
    "Turkish",
    "Hindi",
]

TRANSLATION_TARGET_LANGUAGES = [
    "中文",
    "英文",
    "日文",
    "韓文",
    "法文",
    "德文",
    "西班牙文",
    "葡萄牙文",
    "義大利文",
    "俄文",
    "阿拉伯文",
    "泰文",
    "越南文",
    "印尼文",
    "土耳其文",
    "印地文",
]
