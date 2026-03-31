"""CLI 主程式"""

from typing import Optional

import typer

from app.cli.commands import (
    convert,
    file,
    history,
    hotwords,
    mic,
    serve,
    translate,
)

app = typer.Typer(
    name="voice2text",
    help="Voice2Text - 語音辨識發送文字系統",
    add_completion=False,
)

app.add_typer(mic.app, name="mic", help="從麥克風錄音並轉寫")
app.add_typer(file.app, name="file", help="轉寫音訊檔案")
app.add_typer(convert.app, name="convert", help="簡繁轉換")
app.add_typer(translate.app, name="translate", help="翻譯文字")
app.add_typer(history.app, name="history", help="歷史紀錄管理")
app.add_typer(hotwords.app, name="hotwords", help="熱詞管理")
app.add_typer(serve.app, name="serve", help="啟動 API Server")


@app.callback()
def main_callback(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "--verbose", "-v", help="詳細輸出"),
):
    """全域選項"""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose


@app.command()
def version():
    """顯示版本"""
    from app import __version__

    typer.echo(f"Voice2Text v{__version__}")


if __name__ == "__main__":
    app()
