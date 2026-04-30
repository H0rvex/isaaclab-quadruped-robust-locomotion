"""Pure-Python experiment schemas.

These dataclasses define local metadata contracts only. Simulator-specific
objects belong in GPU-only modules and should not be imported here.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

TARGET_STACK = {
    "isaac_lab": "2.3.2",
    "isaac_sim": "5.1.0",
    "python": "3.11",
    "pytorch": "2.7.0+cu128",
    "rsl_rl": "required",
    "os": "Ubuntu 22.04/24.04",
}


@dataclass(frozen=True)
class RuntimeStack:
    """Runtime versions captured for a result-producing run."""

    isaac_lab: str
    isaac_sim: str
    python: str
    pytorch: str
    cuda: str
    rsl_rl: str
    os: str
    gpu: str
    driver: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RunMetadata:
    """Metadata required to audit one training or evaluation run."""

    run_id: str
    task_id: str
    robot: str
    seed: int
    config_path: str
    command: str
    results_dir: str
    runtime: RuntimeStack
    checkpoint_path: str | None = None
    notes: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EvaluationSummary:
    """Evaluation summary intended for JSON artifacts and result tables."""

    policy: str
    task_id: str
    seed: int
    evaluation_seed: int
    episodes: int
    mean_return: float
    std_return: float
    mean_episode_length: float
    checkpoint_path: str
    terrain: str | None = None
    randomization: str | None = None
    fall_rate: float | None = None
    per_episode_returns: list[float] = field(default_factory=list)
    per_episode_lengths: list[float] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
