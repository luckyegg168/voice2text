"""API Server 命令"""

import uvicorn

import typer
from app.core.config import get_settings

app = typer.Typer(help="啟動 API Server")


@app.command()
def main(
    host: str = typer.Option(None, "--host", "-h", help="主機"),
    port: int = typer.Option(None, "--port", "-p", help="連接埠"),
    reload: bool = typer.Option(False, "--reload", "-r", help="熱重載"),
):
    """啟動 API Server"""
    settings = get_settings()

    host = host or settings.api_host
    port = port or settings.api_port

    typer.echo("啟動 Voice2Text API Server...")
    typer.echo(f"  Host: {host}")
    typer.echo(f"  Port: {port}")
    typer.echo(f"  Docs: http://{host}:{port}/docs")
    typer.echo("")

    uvicorn.run(
        "app.api.main:app",
        host=host,
        port=port,
        reload=reload,
        factory=False,
    )
