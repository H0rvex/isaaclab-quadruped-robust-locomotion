"""Pure-Python export manifest helpers.

The manifest records the interface metadata expected beside an exported policy
artifact. It is local-only bookkeeping and does not import Isaac Lab, Torch, or
ONNX runtime packages.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PathLike = str | Path

SUPPORTED_EXPORT_FORMATS = {"torchscript", "onnx"}


@dataclass(frozen=True)
class ExportManifest:
    """Metadata contract written beside a policy export artifact."""

    env_id: str
    checkpoint_path: str
    export_format: str
    observation_dimension: int
    action_dimension: int
    normalization_info: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    git_commit: str | None = None

    def validate(self) -> None:
        if not self.env_id:
            raise ValueError("env_id must not be empty")
        if not self.checkpoint_path:
            raise ValueError("checkpoint_path must not be empty")
        if self.export_format not in SUPPORTED_EXPORT_FORMATS:
            allowed = ", ".join(sorted(SUPPORTED_EXPORT_FORMATS))
            raise ValueError(f"export_format must be one of: {allowed}")
        if self.observation_dimension <= 0:
            raise ValueError("observation_dimension must be positive")
        if self.action_dimension <= 0:
            raise ValueError("action_dimension must be positive")
        if not isinstance(self.normalization_info, dict):
            raise ValueError("normalization_info must be a JSON object")
        parse_timestamp(self.timestamp)

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)


def parse_timestamp(value: str) -> datetime:
    """Parse an ISO-8601 timestamp from a manifest."""

    if not value:
        raise ValueError("timestamp must not be empty")
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"timestamp must be ISO-8601: {value}") from exc


def get_git_commit(repo_root: PathLike = ".") -> str | None:
    """Return the current git commit hash when available."""

    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=Path(repo_root),
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    commit = result.stdout.strip()
    return commit or None


def write_manifest(path: PathLike, manifest: ExportManifest) -> None:
    """Write a manifest JSON file with stable formatting."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest.to_dict(), handle, indent=2, sort_keys=True)
        handle.write("\n")


def read_manifest(path: PathLike) -> ExportManifest:
    """Read and validate a manifest JSON file."""

    input_path = Path(path)
    with input_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {input_path}")
    manifest = ExportManifest(
        env_id=str(data.get("env_id", "")),
        checkpoint_path=str(data.get("checkpoint_path", "")),
        export_format=str(data.get("export_format", "")),
        observation_dimension=int(data.get("observation_dimension", 0)),
        action_dimension=int(data.get("action_dimension", 0)),
        normalization_info=data.get("normalization_info", {}),
        timestamp=str(data.get("timestamp", "")),
        git_commit=data.get("git_commit"),
    )
    manifest.validate()
    return manifest


def create_manifest(
    *,
    env_id: str,
    checkpoint_path: str,
    export_format: str,
    observation_dimension: int,
    action_dimension: int,
    normalization_info: dict[str, Any] | None = None,
    repo_root: PathLike = ".",
) -> ExportManifest:
    """Create a manifest and attach the current git commit when available."""

    manifest = ExportManifest(
        env_id=env_id,
        checkpoint_path=checkpoint_path,
        export_format=export_format,
        observation_dimension=observation_dimension,
        action_dimension=action_dimension,
        normalization_info=normalization_info or {},
        git_commit=get_git_commit(repo_root),
    )
    manifest.validate()
    return manifest
