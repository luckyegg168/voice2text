"""熱詞管理模組"""

import json
from pathlib import Path
from typing import Optional

from app.core.config import get_settings


class HotWordsManager:
    """熱詞管理器"""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or get_settings().hotwords_file
        self._data: dict = {"groups": []}
        self.load()

    def load(self) -> None:
        """從檔案載入熱詞"""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except json.JSONDecodeError:
                self._data = {"groups": []}

    def save(self) -> None:
        """儲存熱詞到檔案"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def get_groups(self) -> list[str]:
        """取得所有群組名稱"""
        return [g["name"] for g in self._data.get("groups", [])]

    def add_group(self, name: str) -> None:
        """新增群組"""
        if not any(g["name"] == name for g in self._data["groups"]):
            self._data["groups"].append({"name": name, "words": []})
            self.save()

    def remove_group(self, name: str) -> None:
        """刪除群組"""
        self._data["groups"] = [g for g in self._data["groups"] if g["name"] != name]
        self.save()

    def rename_group(self, old_name: str, new_name: str) -> None:
        """重新命名群組"""
        for group in self._data["groups"]:
            if group["name"] == old_name:
                group["name"] = new_name
                break
        self.save()

    def get_words(self, group_name: str) -> list[dict]:
        """取得群組內所有熱詞"""
        for group in self._data["groups"]:
            if group["name"] == group_name:
                return group.get("words", [])
        return []

    def add_word(self, group_name: str, word: str, weight: float = 1.0) -> None:
        """新增熱詞"""
        for group in self._data["groups"]:
            if group["name"] == group_name:
                if not any(w["text"] == word for w in group.get("words", [])):
                    group.setdefault("words", []).append({"text": word, "weight": weight})
                    self.save()
                return

    def remove_word(self, group_name: str, word: str) -> None:
        """刪除熱詞"""
        for group in self._data["groups"]:
            if group["name"] == group_name:
                group["words"] = [w for w in group.get("words", []) if w["text"] != word]
                self.save()
                return

    def update_word_weight(self, group_name: str, word: str, weight: float) -> None:
        """更新熱詞權重"""
        for group in self._data["groups"]:
            if group["name"] == group_name:
                for w in group.get("words", []):
                    if w["text"] == word:
                        w["weight"] = weight
                        self.save()
                        return
                return

    def get_all_words_flat(self, group_name: str) -> list[tuple[str, float]]:
        """取得群組內所有熱詞（扁平化）"""
        words = []
        for group in self._data["groups"]:
            if group["name"] == group_name:
                for w in group.get("words", []):
                    words.append((w["text"], w.get("weight", 1.0)))
                break
        return words

    def apply_hotwords(self, text: str, group_name: str) -> str:
        """對文字應用熱詞增強

        Note: Qwen3-ASR 目前不支援直接傳入熱詞，
        此方法預留為未來擴展使用
        """
        return text


_default_manager: Optional[HotWordsManager] = None


def get_hotwords_manager() -> HotWordsManager:
    """取得熱詞管理器單例"""
    global _default_manager
    if _default_manager is None:
        _default_manager = HotWordsManager()
    return _default_manager
