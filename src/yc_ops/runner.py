"""Execute yc commands for resources."""

from __future__ import annotations

import json
import subprocess
from typing import Any

from rich.console import Console

from yc_ops.config import RESOURCE_TYPES, get_yc_path

console = Console()


def run_yc(yc_path: str, args: str, capture: bool = False) -> subprocess.CompletedProcess[str]:
    cmd = f"{yc_path} {args}"
    return subprocess.run(cmd, shell=True, capture_output=capture, text=True)


def start_resource(cfg: dict[str, Any], resource: dict[str, Any]) -> bool:
    yc = get_yc_path(cfg)
    rtype = resource["type"]
    name = resource["name"]
    templates = RESOURCE_TYPES.get(rtype)
    if not templates:
        console.print(f"  [red]Unknown resource type: {rtype}[/red]")
        return False

    cmd = templates["start"].format(name=name)
    result = run_yc(yc, cmd, capture=True)
    if result.returncode == 0:
        console.print(f"  [green]OK[/green] {rtype}/{name} started")
        return True
    if "already" in result.stderr.lower() or "running" in result.stderr.lower():
        console.print(f"  [yellow]--[/yellow] {rtype}/{name} already running")
        return True
    console.print(f"  [red]FAIL[/red] {rtype}/{name}: {result.stderr.strip()}")
    return False


def stop_resource(cfg: dict[str, Any], resource: dict[str, Any]) -> bool:
    yc = get_yc_path(cfg)
    rtype = resource["type"]
    name = resource["name"]
    templates = RESOURCE_TYPES.get(rtype)
    if not templates:
        console.print(f"  [red]Unknown resource type: {rtype}[/red]")
        return False

    cmd = templates["stop"].format(name=name)
    result = run_yc(yc, cmd, capture=True)
    if result.returncode == 0:
        console.print(f"  [green]OK[/green] {rtype}/{name} stopped")
        return True
    if "already" in result.stderr.lower() or "stopped" in result.stderr.lower():
        console.print(f"  [yellow]--[/yellow] {rtype}/{name} already stopped")
        return True
    console.print(f"  [red]FAIL[/red] {rtype}/{name}: {result.stderr.strip()}")
    return False


def get_resource_status(cfg: dict[str, Any], resource: dict[str, Any]) -> dict[str, str]:
    yc = get_yc_path(cfg)
    rtype = resource["type"]
    name = resource["name"]
    templates = RESOURCE_TYPES.get(rtype)
    if not templates:
        return {"name": name, "type": rtype, "status": "UNKNOWN_TYPE"}

    cmd = templates["status"].format(name=name)
    result = run_yc(yc, cmd, capture=True)
    if result.returncode != 0:
        return {"name": name, "type": rtype, "status": "NOT_FOUND"}

    try:
        data = json.loads(result.stdout)
        status = data.get("status", "UNKNOWN")
        health = data.get("health", "")
        label = f"{status} ({health})" if health else status
        return {"name": name, "type": rtype, "status": label}
    except json.JSONDecodeError:
        return {"name": name, "type": rtype, "status": "PARSE_ERROR"}
