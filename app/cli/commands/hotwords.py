"""熱詞管理命令"""

import typer

from app.core.hot_words import get_hotwords_manager

app = typer.Typer(help="熱詞管理")


@app.command("list")
def list_groups():
    """列出所有熱詞群組"""
    manager = get_hotwords_manager()

    groups = manager.get_groups()

    if not groups:
        typer.echo("沒有熱詞群組")
        return

    typer.echo("熱詞群組：")
    for group in groups:
        words = manager.get_words(group)
        typer.echo(f"  [{group}] ({len(words)} 個熱詞)")
        for w in words[:5]:
            typer.echo(f"    - {w['text']} (weight: {w.get('weight', 1.0)})")
        if len(words) > 5:
            typer.echo(f"    ... 還有 {len(words) - 5} 個")


@app.command("words")
def list_words(group_name: str):
    """列出群組內所有熱詞"""
    manager = get_hotwords_manager()

    words = manager.get_words(group_name)

    if not words:
        typer.echo(f"群組 [{group_name}] 沒有熱詞")
        return

    typer.echo(f"群組 [{group_name}] 熱詞：")
    for w in words:
        typer.echo(f"  - {w['text']} (weight: {w.get('weight', 1.0)})")


@app.command("add-group")
def add_group(name: str):
    """新增熱詞群組"""
    manager = get_hotwords_manager()

    if name in manager.get_groups():
        typer.echo(f"群組 [{name}] 已存在")
        return

    manager.add_group(name)
    typer.echo(f"已新增群組 [{name}]")


@app.command("add")
def add_word(
    group_name: str,
    word: str,
    weight: float = typer.Option(1.0, "--weight", "-w", help="權重"),
):
    """新增熱詞"""
    manager = get_hotwords_manager()

    if group_name not in manager.get_groups():
        manager.add_group(group_name)

    manager.add_word(group_name, word, weight)
    typer.echo(f"已新增熱詞 [{word}] 到群組 [{group_name}] (weight: {weight})")


@app.command("remove")
def remove_word(
    group_name: str,
    word: str,
):
    """移除熱詞"""
    manager = get_hotwords_manager()

    manager.remove_word(group_name, word)
    typer.echo(f"已移除熱詞 [{word}]")


@app.command("remove-group")
def remove_group(name: str):
    """移除熱詞群組"""
    manager = get_hotwords_manager()

    if name not in manager.get_groups():
        typer.echo(f"群組 [{name}] 不存在")
        return

    manager.remove_group(name)
    typer.echo(f"已移除群組 [{name}]")


@app.command("weight")
def update_weight(
    group_name: str,
    word: str,
    weight: float,
):
    """更新熱詞權重"""
    manager = get_hotwords_manager()

    manager.update_word_weight(group_name, word, weight)
    typer.echo(f"已更新熱詞 [{word}] 權重為 {weight}")
