from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

pytestmark = [
    pytest.mark.sim,
    pytest.mark.skipif(
        os.environ.get("RUN_SIM_TESTS") != "1",
        reason="set RUN_SIM_TESTS=1 on the rented GPU machine to run Isaac Lab validation",
    ),
]


def test_isaaclab_validation_script_runs() -> None:
    isaaclab_path = os.environ.get("ISAACLAB_PATH")
    assert isaaclab_path, "ISAACLAB_PATH must point to the IsaacLab checkout"
    assert Path(isaaclab_path, "isaaclab.sh").exists()

    subprocess.run(
        ["bash", "scripts/validate_runtime_isaaclab.sh"],
        check=True,
        timeout=600,
    )
