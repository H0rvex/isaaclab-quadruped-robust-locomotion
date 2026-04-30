"""Pure-Python helpers for reading and writing experiment artifacts."""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

PathLike = str | Path


def read_json(path: PathLike) -> dict[str, Any]:
    """Read a JSON object from disk."""
    input_path = Path(path)
    with input_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {input_path}")
    return data


def write_json(path: PathLike, data: dict[str, Any]) -> None:
    """Write a JSON object with stable formatting."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")


def read_yaml(path: PathLike) -> dict[str, Any]:
    """Read a YAML mapping from disk."""
    input_path = Path(path)
    with input_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected YAML mapping in {input_path}")
    return data


def iter_json_files(directory: PathLike) -> Iterable[Path]:
    """Yield JSON files below a directory in stable order."""
    root = Path(directory)
    if not root.exists():
        return []
    return sorted(path for path in root.rglob("*.json") if path.is_file())


def read_table(path: PathLike) -> pd.DataFrame:
    """Read a CSV or JSON table artifact."""
    input_path = Path(path)
    suffix = input_path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(input_path)
    if suffix == ".json":
        return pd.read_json(input_path)
    raise ValueError(f"Unsupported table extension: {input_path.suffix}")


def write_table(path: PathLike, frame: pd.DataFrame) -> None:
    """Write a table artifact as CSV or JSON records."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    suffix = output_path.suffix.lower()
    if suffix == ".csv":
        frame.to_csv(output_path, index=False)
        return
    if suffix == ".json":
        output_path.write_text(
            frame.to_json(orient="records", indent=2) + "\n",
            encoding="utf-8",
        )
        return
    raise ValueError(f"Unsupported table extension: {output_path.suffix}")
