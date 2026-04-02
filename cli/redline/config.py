"""Configuration loading and defaults for Redline CLI."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


DEFAULT_CONFIG: dict[str, Any] = {
    "regulations": ["bsa-aml"],
    "document_types": {},
    "output": {
        "format": "json",
        "directory": ".redline/reports",
    },
    "ai": {
        "enabled": False,
        "model": "claude-sonnet-4-20250514",
        "confidence_threshold": 0.7,
    },
}


@dataclass(frozen=True)
class RedlineConfig:
    """Immutable configuration for a Redline run."""

    regulations: list[str]
    document_types: dict[str, str]
    output_format: str
    output_directory: str
    ai_enabled: bool
    ai_model: str
    confidence_threshold: float


def load_config(config_path: Path) -> RedlineConfig:
    """Load config from YAML file, merging with defaults."""
    user_config: dict[str, Any] = {}
    if config_path.exists():
        raw = yaml.safe_load(config_path.read_text())
        if raw:
            user_config = raw

    merged = _deep_merge(DEFAULT_CONFIG, user_config)

    return RedlineConfig(
        regulations=merged["regulations"],
        document_types=merged.get("document_types", {}),
        output_format=merged["output"]["format"],
        output_directory=merged["output"]["directory"],
        ai_enabled=merged["ai"]["enabled"],
        ai_model=merged["ai"]["model"],
        confidence_threshold=merged["ai"]["confidence_threshold"],
    )


def _deep_merge(
    base: dict[str, Any], override: dict[str, Any]
) -> dict[str, Any]:
    """Merge override into base, preferring override values."""
    result = dict(base)
    for key, value in override.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result
