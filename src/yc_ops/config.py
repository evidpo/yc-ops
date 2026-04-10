"""Configuration management for yc-ops."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

CONFIG_DIR = Path(os.environ.get("YC_OPS_CONFIG_DIR", "~/.config/yc-ops")).expanduser()
GLOBAL_CONFIG_FILE = CONFIG_DIR / "config.yaml"
LOCAL_CONFIG_NAME = "yc-ops.yaml"

DEFAULT_CONFIG: dict[str, Any] = {
    "yc_path": "~/.yandex-cloud/bin/yc",
    "resources": [],
}


def _find_config_file() -> Path:
    """Return local yc-ops.yaml if it exists in cwd, otherwise global config."""
    local = Path.cwd() / LOCAL_CONFIG_NAME
    if local.exists():
        return local
    return GLOBAL_CONFIG_FILE

RESOURCE_TYPES = {
    "compute": {
        "start": "compute instance start {name}",
        "stop": "compute instance stop {name}",
        "status": "compute instance get {name} --format json",
    },
    "managed-postgresql": {
        "start": "managed-postgresql cluster start {name} --async",
        "stop": "managed-postgresql cluster stop {name}",
        "status": "managed-postgresql cluster get {name} --format json",
    },
    "managed-mysql": {
        "start": "managed-mysql cluster start {name} --async",
        "stop": "managed-mysql cluster stop {name}",
        "status": "managed-mysql cluster get {name} --format json",
    },
    "managed-clickhouse": {
        "start": "managed-clickhouse cluster start {name} --async",
        "stop": "managed-clickhouse cluster stop {name}",
        "status": "managed-clickhouse cluster get {name} --format json",
    },
    "managed-redis": {
        "start": "managed-redis cluster start {name} --async",
        "stop": "managed-redis cluster stop {name}",
        "status": "managed-redis cluster get {name} --format json",
    },
}


def load_config() -> tuple[dict[str, Any], Path]:
    """Load config. Returns (config_dict, config_path)."""
    path = _find_config_file()
    if not path.exists():
        return DEFAULT_CONFIG.copy(), path
    with open(path) as f:
        cfg = yaml.safe_load(f) or DEFAULT_CONFIG.copy()
    return cfg, path


def save_config(cfg: dict[str, Any], path: Path | None = None) -> Path:
    """Save config to path. If path is None, saves to detected location."""
    if path is None:
        path = _find_config_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        yaml.dump(cfg, f, default_flow_style=False, allow_unicode=True)
    return path


def get_yc_path(cfg: dict[str, Any]) -> str:
    return str(Path(cfg.get("yc_path", "~/.yandex-cloud/bin/yc")).expanduser())
