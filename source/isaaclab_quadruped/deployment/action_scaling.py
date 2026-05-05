"""Action scaling contracts for deployment targets.

The helpers in this file convert normalized policy actions into joint position
targets using plain Python data. They define an interface boundary only; they
do not command actuators or talk to a robot.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class ActionScaling:
    """Scale normalized actions around nominal joint positions."""

    joint_names: tuple[str, ...]
    scale: float
    default_joint_positions: tuple[float, ...]

    @property
    def action_dim(self) -> int:
        return len(self.joint_names)

    def validate(self) -> None:
        if not self.joint_names:
            raise ValueError("joint_names must not be empty")
        if len(set(self.joint_names)) != len(self.joint_names):
            raise ValueError("joint_names must be unique")
        if self.scale <= 0.0:
            raise ValueError("action scale must be positive")
        if len(self.default_joint_positions) != self.action_dim:
            raise ValueError(
                "default_joint_positions length must match action dimension "
                f"({len(self.default_joint_positions)} != {self.action_dim})"
            )

    def scale_action(self, action: tuple[float, ...] | list[float]) -> tuple[float, ...]:
        """Return joint targets for one normalized action vector."""

        self.validate()
        if len(action) != self.action_dim:
            raise ValueError(f"action dimension mismatch: {len(action)} != {self.action_dim}")
        return tuple(
            default + self.scale * float(value)
            for default, value in zip(self.default_joint_positions, action, strict=True)
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def ensure_action_scale(scale: float) -> None:
    """Validate a scalar action scale used by policy deployment configs."""

    if scale <= 0.0:
        raise ValueError("action scale must be positive")
