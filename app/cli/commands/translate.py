"""翻譯命令"""

import asyncio

import typer

from app.core.translation_service import get_translation_service

app = typer.Typer(help="翻譯文字")


@app.command()
def main(
    text: str = typer.Argument(..., help="要翻譯的文字"),
    target_lang: str = typer.Option(..., "--target", "-t", help="目標語言"),
    source_lang: str = typer.Option(None, "--source", "-s", help="來源語言"),
):
    """翻譯文字"""
    service = get_translation_service()

    typer.echo(f"來源文字: {text}")
    typer.echo(f"目標語言: {target_lang}")
    if source_lang:
        typer.echo(f"來源語言: {source_lang}")
    typer.echo("")
    typer.echo("翻譯中...")

    result = asyncio.run(
        service.translate(
            text=text,
            target_language=target_lang,
            source_language=source_lang,
        )
    )

    typer.echo("")
    typer.echo("=" * 50)
    typer.echo(f"翻譯: {result}")
    typer.echo("=" * 50)


@app.command("check")
def check_connection():
    """檢查翻譯 API 連線"""
    service = get_translation_service()

    typer.echo(f"API URL: {service.api_url}")
    typer.echo("檢查連線...")

    if asyncio.run(service.check_connection()):
        typer.echo("連線成功！", err=True)
    else:
        typer.echo("連線失敗！", err=True)
        raise typer.Exit(1)
