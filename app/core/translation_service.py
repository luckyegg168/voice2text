"""翻譯服務模組"""

from typing import Optional

import httpx

from app.core.config import get_settings


class TranslationService:
    """翻譯服務"""

    def __init__(
        self,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        settings = get_settings()
        self.api_url = api_url or settings.translation_api_url
        self.api_key = api_key or settings.translation_api_key
        self.model = model or settings.translation_model

    async def translate(
        self,
        text: str,
        target_language: str,
        source_language: Optional[str] = None,
    ) -> str:
        """翻譯文字

        Args:
            text: 原始文字
            target_language: 目標語言
            source_language: 來源語言（可選）

        Returns:
            翻譯後文字
        """
        if not text:
            return ""

        prompt = self._build_prompt(text, target_language, source_language)

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 2000,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                self.api_url,
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            result = response.json()

            return result["choices"][0]["message"]["content"].strip()

    def _build_prompt(
        self, text: str, target_language: str, source_language: Optional[str] = None
    ) -> str:
        """建構翻譯提示"""
        if source_language:
            return f"Translate the following {source_language} text to {target_language}. Only output the translated text, nothing else.\n\n{text}"
        else:
            return f"Translate the following text to {target_language}. Only output the translated text, nothing else.\n\n{text}"

    async def check_connection(self) -> bool:
        """檢查 API 連線"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    self.api_url.replace("/chat/completions", "/models"),
                    headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {},
                )
                return response.status_code == 200
        except Exception:
            return False


_default_service: Optional[TranslationService] = None


def get_translation_service() -> TranslationService:
    """取得翻譯服務單例"""
    global _default_service
    if _default_service is None:
        _default_service = TranslationService()
    return _default_service
