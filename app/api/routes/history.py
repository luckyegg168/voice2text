"""歷史紀錄 API 路由"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.api.models import HistoryItem, HistoryListResponse
from app.core.history_manager import get_history_manager

router = APIRouter(prefix="/history", tags=["history"])


@router.get("", response_model=HistoryListResponse)
async def list_history(
    search: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
) -> HistoryListResponse:
    """列出歷史紀錄"""
    manager = get_history_manager()
    items, total = await manager.list(
        search=search,
        limit=limit,
        offset=offset,
    )

    return HistoryListResponse(
        items=[HistoryItem(**item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{record_id}", response_model=HistoryItem)
async def get_history(record_id: int) -> HistoryItem:
    """取得單筆歷史紀錄"""
    manager = get_history_manager()
    item = await manager.get(record_id)

    if item is None:
        raise HTTPException(status_code=404, detail="Record not found")

    return HistoryItem(**item)


@router.delete("/{record_id}")
async def delete_history(record_id: int) -> dict:
    """刪除歷史紀錄"""
    manager = get_history_manager()
    deleted = await manager.delete(record_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Record not found")

    return {"message": "Deleted successfully"}


@router.put("/{record_id}/translate")
async def update_translation(
    record_id: int,
    translated_text: str,
) -> dict:
    """更新翻譯文字"""
    manager = get_history_manager()
    item = await manager.get(record_id)

    if item is None:
        raise HTTPException(status_code=404, detail="Record not found")

    await manager.update_translated_text(record_id, translated_text)

    return {"message": "Updated successfully"}
