"""歷史紀錄命令"""

import asyncio
from datetime import datetime

import typer

from app.core.history_manager import get_history_manager

app = typer.Typer(help="歷史紀錄管理")


@app.command("list")
def list_history(
    limit: int = typer.Option(10, "--limit", "-l", help="顯示筆數"),
    search: str = typer.Option(None, "--search", "-s", help="搜尋關鍵字"),
):
    """列出歷史紀錄"""
    manager = get_history_manager()

    items, total = asyncio.run(manager.list(search=search, limit=limit))

    if not items:
        typer.echo("沒有歷史紀錄")
        return

    typer.echo(f"共 {total} 筆紀錄，顯示 {len(items)} 筆：")
    typer.echo("")

    for item in items:
        created = datetime.fromisoformat(item["created_at"])
        typer.echo(f"[{item['id']}] {created.strftime('%Y-%m-%d %H:%M:%S')}")
        typer.echo(f"    {item['text'][:80]}...")
        typer.echo(f"    語言: {item.get('language', 'N/A')} | 模型: {item.get('model', 'N/A')}")
        typer.echo("")


@app.command("get")
def get_record(record_id: int):
    """取得單筆紀錄"""
    manager = get_history_manager()

    item = asyncio.run(manager.get(record_id))

    if not item:
        typer.echo(f"找不到紀錄 #{record_id}")
        raise typer.Exit(1)

    created = datetime.fromisoformat(item["created_at"])

    typer.echo(f"ID: {item['id']}")
    typer.echo(f"時間: {created.strftime('%Y-%m-%d %H:%M:%S')}")
    typer.echo(f"語言: {item.get('language', 'N/A')}")
    typer.echo(f"模型: {item.get('model', 'N/A')}")
    typer.echo(f"長度: {item.get('duration', 'N/A')} 秒")
    typer.echo(f"音訊: {item.get('audio_path', 'N/A')}")
    typer.echo("")
    typer.echo("轉寫文字：")
    typer.echo(item["text"])

    if item.get("translated_text"):
        typer.echo("")
        typer.echo("翻譯文字：")
        typer.echo(item["translated_text"])


@app.command("delete")
def delete_record(
    record_id: int,
    force: bool = typer.Option(False, "--force", "-f", help="強制刪除"),
):
    """刪除紀錄"""
    if not force:
        confirm = typer.confirm(f"確定要刪除紀錄 #{record_id} 嗎？")
        if not confirm:
            return

    manager = get_history_manager()
    deleted = asyncio.run(manager.delete(record_id))

    if deleted:
        typer.echo(f"已刪除紀錄 #{record_id}")
    else:
        typer.echo(f"找不到紀錄 #{record_id}")


@app.command("clear")
def clear_all(
    force: bool = typer.Option(False, "--force", "-f", help="強制刪除"),
):
    """清除所有歷史"""
    if not force:
        confirm = typer.confirm("確定要刪除所有歷史紀錄嗎？此操作不可復原！")
        if not confirm:
            return

    manager = get_history_manager()
    asyncio.run(manager.delete_all())

    typer.echo("已清除所有歷史紀錄")
