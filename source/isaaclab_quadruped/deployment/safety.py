"""Local safety contracts for policy deployment interfaces.

This file validates limits, timeouts, and command freshness using pure Python
data structures. It is not a real robot safety controller.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from isaaclab_quadruped.deployment.observation_schema import validate_joint_names


@dataclass(frozen=True)
class SafetyLimits:
    """Action and command safety bounds expected by the bridge layer."""

    joint_names: tuple[str, ...]
    action_lower: tuple[float, ...]
    action_upper: tuple[float, ...]
    command_timeout_s: float
    max_linear_velocity_mps: float
    max_angular_velocity_radps: float

    @property
    def action_dim(self) -> int:
        return len(self.joint_names)

    def validate(self) -> None:
        validate_joint_names(self.joint_names)
        if len(self.action_lower) != self.action_dim:
            raise ValueError("action_lower length must match action dimension")
        if len(self.action_upper) != self.action_dim:
            raise ValueError("action_upper length must match action dimension")
        for index, (lower, upper) in enumerate(
            zip(self.action_lower, self.action_upper, strict=True)
        ):
            if lower >= upper:
                raise ValueError(f"invalid action limit at index {index}: {lower} >= {upper}")
        if self.command_timeout_s <= 0.0:
            raise ValueError("command_timeout_s must be positive")
        if self.max_linear_velocity_mps <= 0.0:
            raise ValueError("max_linear_velocity_mps must be positive")
        if self.max_angular_velocity_radps <= 0.0:
            raise ValueError("max_angular_velocity_radps must be positive")

    def validate_action(self, action: tuple[float, ...] | list[float]) -> None:
        """Validate one normalized action vector against configured limits."""

        self.validate()
        if len(action) != self.action_dim:
            raise ValueError(f"action dimension mismatch: {len(action)} != {self.action_dim}")
        for index, (value, lower, upper) in enumerate(
            zip(action, self.action_lower, self.action_upper, strict=True)
        ):
            if float(value) < lower or float(value) > upper:
                raise ValueError(
                    f"action value at index {index} is outside limits: "
                    f"{value} not in [{lower}, {upper}]"
                )

    def clamp_action(self, action: tuple[float, ...] | list[float]) -> tuple[float, ...]:
        """Clamp an action vector to the configured safety envelope."""

        self.validate()
        if len(action) != self.action_dim:
            raise ValueError(f"action dimension mismatch: {len(action)} != {self.action_dim}")
        return tuple(
            min(max(float(value), lower), upper)
            for value, lower, upper in zip(
                action, self.action_lower, self.action_upper, strict=True
            )
        )

    def validate_command(self, linear_x: float, linear_y: float, angular_z: float) -> None:
        """Validate a planar velocity command against configured limits."""

        self.validate()
        if abs(linear_x) > self.max_linear_velocity_mps:
            raise ValueError("linear_x exceeds max_linear_velocity_mps")
        if abs(linear_y) > self.max_linear_velocity_mps:
            raise ValueError("linear_y exceeds max_linear_velocity_mps")
        if abs(angular_z) > self.max_angular_velocity_radps:
            raise ValueError("angular_z exceeds max_angular_velocity_radps")

    def is_command_fresh(self, age_s: float) -> bool:
        """Return whether a command age is within the timeout contract."""

        if age_s < 0.0:
            raise ValueError("age_s must be non-negative")
        return age_s <= self.command_timeout_s

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
