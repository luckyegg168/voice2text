"""簡繁轉換命令"""

import typer

from app.core.opencc_engine import opencc_engine

app = typer.Typer(help="簡繁轉換")


@app.command()
def main(
    text: str = typer.Argument(..., help="要轉換的文字"),
    mode: str = typer.Option("s2t", "--mode", "-m", help="轉換模式"),
):
    """簡繁轉換"""
    result = opencc_engine.convert(text, mode)

    typer.echo(f"模式: {mode}")
    typer.echo(f"輸入: {text}")
    typer.echo(f"輸出: {result}")


@app.command("modes")
def list_modes():
    """列出所有可用模式"""
    modes = opencc_engine.get_available_modes()

    typer.echo("可用轉換模式：")
    for m in modes:
        typer.echo(f"  {m['mode']:8} - {m['name']:20} ({m['description']})")
