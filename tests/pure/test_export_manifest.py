from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from isaaclab_quadruped.deployment.export_manifest import (
    ExportManifest,
    create_manifest,
    get_git_commit,
    read_manifest,
    write_manifest,
)


def test_export_manifest_round_trip(tmp_path: Path) -> None:
    manifest = ExportManifest(
        env_id="Isaac-Velocity-Rough-Unitree-Go2-v0",
        checkpoint_path="runs/go2/model_1000.pt",
        export_format="torchscript",
        observation_dimension=45,
        action_dimension=12,
        normalization_info={"type": "running_mean_std", "frozen": True},
        timestamp=datetime(2026, 1, 1, tzinfo=UTC).isoformat(),
        git_commit="abc123",
    )
    path = tmp_path / "export_manifest.json"

    write_manifest(path, manifest)
    loaded = read_manifest(path)

    assert loaded == manifest
    assert path.read_text(encoding="utf-8").endswith("\n")


def test_export_manifest_rejects_invalid_values() -> None:
    manifest = ExportManifest(
        env_id="",
        checkpoint_path="checkpoint.pt",
        export_format="torchscript",
        observation_dimension=45,
        action_dimension=12,
        normalization_info={},
        timestamp=datetime.now(UTC).isoformat(),
    )

    with pytest.raises(ValueError, match="env_id"):
        manifest.validate()

    bad_format = ExportManifest(
        env_id="task",
        checkpoint_path="checkpoint.pt",
        export_format="pickle",
        observation_dimension=45,
        action_dimension=12,
        normalization_info={},
        timestamp=datetime.now(UTC).isoformat(),
    )
    with pytest.raises(ValueError, match="export_format"):
        bad_format.validate()


def test_create_manifest_attaches_git_commit_when_available() -> None:
    manifest = create_manifest(
        env_id="task",
        checkpoint_path="checkpoint.pt",
        export_format="onnx",
        observation_dimension=45,
        action_dimension=12,
        normalization_info={"type": "none"},
        repo_root=".",
    )

    assert manifest.env_id == "task"
    assert manifest.export_format == "onnx"
    assert manifest.git_commit == get_git_commit(".")


def test_read_manifest_requires_json_object(tmp_path: Path) -> None:
    path = tmp_path / "export_manifest.json"
    path.write_text("[]\n", encoding="utf-8")

    with pytest.raises(ValueError, match="JSON object"):
        read_manifest(path)
