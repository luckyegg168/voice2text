"""麥克風錄音命令"""

import asyncio
import tempfile
from pathlib import Path

import typer

from app.core import audio_processor, history_manager, qwen3_asr
from app.core.config import get_settings

app = typer.Typer(help="從麥克風錄音並轉寫")


@app.command()
def main(
    duration: float = typer.Option(10.0, "--duration", "-d", help="錄音時長（秒）"),
    language: str = typer.Option("auto", "--language", "-l", help="語言"),
    model: str = typer.Option(None, "--model", "-m", help="模型 ID"),
    save: bool = typer.Option(False, "--save", "-s", help="儲存到歷史"),
):
    """錄音並轉寫"""
    settings = get_settings()
    model_id = model or settings.default_model

    typer.echo(f"錄音時長: {duration} 秒")
    typer.echo(f"使用模型: {model_id}")
    typer.echo(f"語言: {language}")
    typer.echo("")

    processor = audio_processor.AudioProcessor(
        sample_rate=settings.sample_rate,
        channels=settings.channels,
    )

    typer.echo("開始錄音...")
    audio_data = processor.record(duration=duration)
    typer.echo(f"錄音完成，長度: {len(audio_data) / settings.sample_rate:.2f} 秒")
    typer.echo("")

    typer.echo("轉寫中...")
    text, detected_lang = qwen3_asr.transcribe(
        audio_input=audio_data,
        model_id=model_id,
        language=None if language == "auto" else language,
    )

    typer.echo("")
    typer.echo("=" * 50)
    typer.echo(f"語言: {detected_lang}")
    typer.echo(f"轉寫: {text}")
    typer.echo("=" * 50)

    if save:
        asyncio.run(_save_history(text, detected_lang, model_id, audio_data, settings))


async def _save_history(
    text: str,
    language: str,
    model: str,
    audio_data,
    settings,
):
    """儲存到歷史"""
    recordings_dir = settings.recordings_dir
    recordings_dir.mkdir(parents=True, exist_ok=True)

    timestamp = Path(tempfile.mktemp(suffix=".wav", dir=recordings_dir))
    audio_processor.AudioProcessor.save_wav(str(timestamp), audio_data, settings.sample_rate)

    history_mgr = history_manager.get_history_manager()
    duration = len(audio_data) / settings.sample_rate
    await history_mgr.add(
        text=text,
        language=language,
        model=model,
        audio_path=str(timestamp),
        duration=duration,
    )

    typer.echo(f"已儲存到歷史 (ID: {timestamp.stem})")
