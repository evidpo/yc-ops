"""Configuration management for yc-ops."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

CONFIG_DIR = Path(os.environ.get("YC_OPS_CONFIG_DIR", "~/.config/yc-ops")).expanduser()
CONFIG_FILE = CONFIG_DIR / "config.yaml"

DEFAULT_CONFIG: dict[str, Any] = {
    "yc_path": "~/.yandex-cloud/bin/yc",
    "resources": [],
}

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


def load_config() -> dict[str, Any]:
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy()
    with open(CONFIG_FILE) as f:
        return yaml.safe_load(f) or DEFAULT_CONFIG.copy()


def save_config(cfg: dict[str, Any]) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        yaml.dump(cfg, f, default_flow_style=False, allow_unicode=True)


def get_yc_path(cfg: dict[str, Any]) -> str:
    return str(Path(cfg.get("yc_path", "~/.yandex-cloud/bin/yc")).expanduser())
