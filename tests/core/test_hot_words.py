"""測試熱詞管理"""

import json
import tempfile
from pathlib import Path

import pytest


def test_hotwords_manager():
    """測試熱詞管理"""
    from app.core.hot_words import HotWordsManager

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write('{"groups": []}')
        temp_path = Path(f.name)

    try:
        manager = HotWordsManager(config_path=temp_path)

        manager.add_group("test")
        assert "test" in manager.get_groups()

        manager.add_word("test", "PySide6", 2.0)
        words = manager.get_words("test")
        assert len(words) == 1
        assert words[0]["text"] == "PySide6"

        manager.remove_word("test", "PySide6")
        assert len(manager.get_words("test")) == 0

        manager.remove_group("test")
        assert "test" not in manager.get_groups()

    finally:
        temp_path.unlink(missing_ok=True)
