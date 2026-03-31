"""音訊檔案轉寫命令"""

import asyncio
import tempfile
from pathlib import Path

import typer

from app.core import audio_processor, history_manager, qwen3_asr
from app.core.config import get_settings

app = typer.Typer(help="轉寫音訊檔案")


@app.command()
def main(
    audio_path: str = typer.Argument(..., help="音訊檔案路徑"),
    language: str = typer.Option("auto", "--language", "-l", help="語言"),
    model: str = typer.Option(None, "--model", "-m", help="模型 ID"),
    save: bool = typer.Option(False, "--save", "-s", help="儲存到歷史"),
):
    """轉寫音訊檔案"""
    settings = get_settings()
    model_id = model or settings.default_model
    audio_file = Path(audio_path)

    if not audio_file.exists():
        typer.echo(f"錯誤：找不到檔案 {audio_path}", err=True)
        raise typer.Exit(1)

    typer.echo(f"檔案: {audio_path}")
    typer.echo(f"使用模型: {model_id}")
    typer.echo(f"語言: {language}")
    typer.echo("")

    data, sr = audio_processor.AudioProcessor.load_wav(str(audio_file))
    audio_16k = audio_processor.AudioProcessor.convert_to_16kmono(data, sr)

    typer.echo("轉寫中...")
    text, detected_lang = qwen3_asr.transcribe(
        audio_input=audio_16k,
        model_id=model_id,
        language=None if language == "auto" else language,
    )

    typer.echo("")
    typer.echo("=" * 50)
    typer.echo(f"語言: {detected_lang}")
    typer.echo(f"轉寫: {text}")
    typer.echo("=" * 50)

    if save:
        asyncio.run(
            _save_history(text, detected_lang, model_id, str(audio_file), audio_16k, sr, settings)
        )


async def _save_history(
    text: str,
    language: str,
    model: str,
    original_path: str,
    audio_data,
    sample_rate: int,
    settings,
):
    """儲存到歷史"""
    recordings_dir = settings.recordings_dir
    recordings_dir.mkdir(parents=True, exist_ok=True)

    timestamp = Path(tempfile.mktemp(suffix=".wav", dir=recordings_dir))
    audio_processor.AudioProcessor.save_wav(str(timestamp), audio_data, sample_rate)

    history_mgr = history_manager.get_history_manager()
    duration = len(audio_data) / sample_rate
    await history_mgr.add(
        text=text,
        language=language,
        model=model,
        audio_path=str(timestamp),
        duration=duration,
    )

    typer.echo(f"已儲存到歷史 (ID: {timestamp.stem})")
