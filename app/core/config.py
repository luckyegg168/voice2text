"""設定管理 - 從 .env 載入設定"""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """應用程式設定"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Model Settings
    default_model: str = Field(default="Qwen/Qwen3-ASR-0.6B", alias="DEFAULT_MODEL")
    device: str = Field(default="cuda", alias="DEVICE")
    dtype: str = Field(default="float16", alias="DTYPE")

    # Audio Settings
    sample_rate: int = Field(default=16000, alias="SAMPLE_RATE")
    channels: int = Field(default=1, alias="CHANNELS")
    vad_enabled: bool = Field(default=True, alias="VAD_ENABLED")

    # Translation API
    translation_api_url: str = Field(
        default="http://localhost:11434/v1/chat/completions",
        alias="TRANSLATION_API_URL",
    )
    translation_api_key: str = Field(default="", alias="TRANSLATION_API_KEY")
    translation_model: str = Field(default="llama3.2", alias="TRANSLATION_MODEL")

    # API Server
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")

    # History Storage
    data_dir: Path = Field(default=Path("./data"), alias="DATA_DIR")
    recordings_dir: Path = Field(default=Path("./data/recordings"), alias="RECORDINGS_DIR")
    database_url: str = Field(
        default="sqlite+aiosqlite:///./data/voice2text.db",
        alias="DATABASE_URL",
    )
    max_history_items: int = Field(default=1000, alias="MAX_HISTORY_ITEMS")

    # OpenCC
    opencc_mode: str = Field(default="s2t", alias="OPENCC_MODE")

    # Hot Words
    hotwords_file: Path = Field(
        default=Path("./data/hotwords.json"),
        alias="HOTWORDS_FILE",
    )
    default_hotwords_group: str = Field(
        default="default",
        alias="DEFAULT_HOTWORDS_GROUP",
    )

    # GUI Settings
    gui_language: str = Field(default="zh-TW", alias="GUI_LANGUAGE")

    # HuggingFace Cache
    hf_home: Path = Field(default=Path("./models/.hf_cache"), alias="HF_HOME")
    transformers_cache: Path = Field(
        default=Path("./models/.transformers_cache"),
        alias="TRANSFORMERS_CACHE",
    )

    def ensure_directories(self) -> None:
        """確保必要目錄存在"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.recordings_dir.mkdir(parents=True, exist_ok=True)
        self.hf_home.mkdir(parents=True, exist_ok=True)
        self.transformers_cache.mkdir(parents=True, exist_ok=True)

    @property
    def db_path(self) -> Path:
        """取得資料庫路徑"""
        return self.data_dir / "voice2text.db"


@lru_cache
def get_settings() -> Config:
    """取得設定單例"""
    return Config()
