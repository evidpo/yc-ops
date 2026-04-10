"""CLI entry point for yc-ops."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from yc_ops.config import LOCAL_CONFIG_NAME, RESOURCE_TYPES, get_yc_path, load_config, save_config
from yc_ops.runner import get_resource_status, start_resource, stop_resource

app = typer.Typer(help="Manage Yandex Cloud resources (VMs, databases, storage).")
console = Console()


@app.command()
def init(
    local: bool = typer.Option(False, "--local", "-l", help="Save config as yc-ops.yaml in current directory"),
) -> None:
    """Interactive setup: configure yc path and register resources."""
    cfg, detected_path = load_config()
    save_path = Path.cwd() / LOCAL_CONFIG_NAME if local else detected_path

    # yc binary
    default_yc = cfg.get("yc_path", "~/.yandex-cloud/bin/yc")
    yc_path = typer.prompt("Path to yc binary", default=default_yc)
    resolved = str(Path(yc_path).expanduser())
    if not shutil.which(resolved) and not Path(resolved).exists():
        console.print(f"[yellow]Warning: {resolved} not found. Install: curl -sSL https://storage.yandexcloud.net/yandexcloud-yc/install.sh | bash[/yellow]")
    cfg["yc_path"] = yc_path

    # resources
    console.print("\n[bold]Register resources[/bold] (empty name to finish):")
    console.print(f"  Supported types: {', '.join(RESOURCE_TYPES.keys())}")
    resources: list[dict[str, str]] = cfg.get("resources", [])
    existing_names = {r["name"] for r in resources}

    while True:
        name = typer.prompt("\nResource name", default="")
        if not name:
            break
        if name in existing_names:
            console.print(f"  [yellow]{name} already registered[/yellow]")
            continue
        rtype = typer.prompt("Resource type", default="compute")
        if rtype not in RESOURCE_TYPES:
            console.print(f"  [red]Unknown type: {rtype}. Use one of: {', '.join(RESOURCE_TYPES.keys())}[/red]")
            continue
        resources.append({"name": name, "type": rtype})
        existing_names.add(name)
        console.print(f"  [green]+[/green] {rtype}/{name}")

    cfg["resources"] = resources
    save_config(cfg, save_path)
    console.print(f"\n[green]Config saved:[/green] {save_path}")


@app.command()
def start(name: Optional[str] = typer.Argument(None, help="Resource name (all if omitted)")) -> None:
    """Start resources."""
    cfg, path = load_config()
    resources = _filter_resources(cfg, name)
    if not resources:
        return
    console.print(f"[dim]Config: {path}[/dim]")
    console.print("[bold]Starting resources...[/bold]")
    for r in resources:
        start_resource(cfg, r)


@app.command()
def stop(name: Optional[str] = typer.Argument(None, help="Resource name (all if omitted)")) -> None:
    """Stop resources."""
    cfg, path = load_config()
    resources = _filter_resources(cfg, name)
    if not resources:
        return
    console.print(f"[dim]Config: {path}[/dim]")
    console.print("[bold]Stopping resources...[/bold]")
    for r in resources:
        stop_resource(cfg, r)


@app.command()
def status() -> None:
    """Show status of all registered resources."""
    cfg, path = load_config()
    resources = cfg.get("resources", [])
    if not resources:
        console.print("[yellow]No resources registered. Run: yc-ops init[/yellow]")
        return

    table = Table(title=f"Yandex Cloud Resources ({path.name})")
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="dim")
    table.add_column("Status")

    for r in resources:
        info = get_resource_status(cfg, r)
        st = info["status"]
        if "RUNNING" in st:
            style = "green"
        elif "STOPPED" in st:
            style = "yellow"
        else:
            style = "red"
        table.add_row(info["name"], info["type"], f"[{style}]{st}[/{style}]")

    console.print(table)


@app.command()
def config() -> None:
    """Show current configuration."""
    cfg, path = load_config()
    console.print(f"[bold]Config file:[/bold] {path}")
    console.print(f"[bold]Source:[/bold] {'local (yc-ops.yaml)' if path.name == LOCAL_CONFIG_NAME else 'global (~/.config/yc-ops/)'}")
    console.print(f"[bold]yc path:[/bold] {get_yc_path(cfg)}")
    resources = cfg.get("resources", [])
    if resources:
        console.print(f"[bold]Resources ({len(resources)}):[/bold]")
        for r in resources:
            console.print(f"  {r['type']}/{r['name']}")
    else:
        console.print("[yellow]No resources registered.[/yellow]")


@app.command()
def remove(name: str = typer.Argument(..., help="Resource name to remove")) -> None:
    """Remove a resource from config."""
    cfg, path = load_config()
    resources = cfg.get("resources", [])
    before = len(resources)
    cfg["resources"] = [r for r in resources if r["name"] != name]
    if len(cfg["resources"]) == before:
        console.print(f"[yellow]Resource '{name}' not found[/yellow]")
        return
    save_config(cfg, path)
    console.print(f"[green]Removed {name}[/green]")


def _filter_resources(cfg: dict, name: str | None) -> list[dict[str, str]]:
    resources = cfg.get("resources", [])
    if not resources:
        console.print("[yellow]No resources registered. Run: yc-ops init[/yellow]")
        return []
    if name:
        matched = [r for r in resources if r["name"] == name]
        if not matched:
            console.print(f"[red]Resource '{name}' not found[/red]")
            return []
        return matched
    return resources


if __name__ == "__main__":
    app()
