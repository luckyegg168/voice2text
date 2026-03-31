"""歷史紀錄管理模組"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import aiosqlite

from app.core.config import get_settings


class HistoryManager:
    """歷史紀錄管理器"""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or get_settings().db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._db_initialized = False

    async def _ensure_db(self) -> None:
        """確保資料庫已初始化"""
        if self._db_initialized:
            return

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS transcriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    language VARCHAR(50),
                    model VARCHAR(100),
                    audio_path VARCHAR(500),
                    duration REAL,
                    translated_text TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()

        self._db_initialized = True

    async def add(
        self,
        text: str,
        language: str,
        model: str,
        audio_path: Optional[str] = None,
        duration: Optional[float] = None,
        translated_text: Optional[str] = None,
    ) -> int:
        """新增紀錄

        Returns:
            新紀錄 ID
        """
        await self._ensure_db()

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO transcriptions 
                (text, language, model, audio_path, duration, translated_text, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    text,
                    language,
                    model,
                    audio_path,
                    duration,
                    translated_text,
                    datetime.now().isoformat(),
                ),
            )
            await db.commit()
            return cursor.lastrowid

    async def get(self, id: int) -> Optional[dict]:
        """取得單筆紀錄"""
        await self._ensure_db()

        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM transcriptions WHERE id = ?", (id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
        return None

    async def list(
        self,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict], int]:
        """列出紀錄

        Returns:
            (紀錄列表, 總數)
        """
        await self._ensure_db()

        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row

            where_clause = ""
            params = []
            if search:
                where_clause = "WHERE text LIKE ?"
                params.append(f"%{search}%")

            async with db.execute(
                f"SELECT COUNT(*) FROM transcriptions {where_clause}",
                params,
            ) as cursor:
                total = (await cursor.fetchone())[0]

            async with db.execute(
                f"""
                SELECT * FROM transcriptions 
                {where_clause}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                params + [limit, offset],
            ) as cursor:
                rows = await cursor.fetchall()
                items = [dict(row) for row in rows]

            return items, total

    async def update_translated_text(self, id: int, translated_text: str) -> None:
        """更新翻譯文字"""
        await self._ensure_db()

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE transcriptions SET translated_text = ? WHERE id = ?",
                (translated_text, id),
            )
            await db.commit()

    async def delete(self, id: int) -> bool:
        """刪除紀錄"""
        await self._ensure_db()

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("DELETE FROM transcriptions WHERE id = ?", (id,))
            await db.commit()
            return cursor.rowcount > 0

    async def delete_all(self) -> None:
        """刪除所有紀錄"""
        await self._ensure_db()

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM transcriptions")
            await db.commit()

    async def get_audio_path(self, id: int) -> Optional[str]:
        """取得音訊檔案路徑"""
        record = await self.get(id)
        return record.get("audio_path") if record else None


_default_manager: Optional[HistoryManager] = None


def get_history_manager() -> HistoryManager:
    """取得歷史記錄管理器單例"""
    global _default_manager
    if _default_manager is None:
        _default_manager = HistoryManager()
    return _default_manager
