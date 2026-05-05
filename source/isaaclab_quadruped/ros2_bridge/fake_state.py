"""Deterministic fake bridge messages for local tests.

The publisher here produces dictionary payloads shaped like ROS bridge data.
It is not a ROS node, simulator adapter, or robot driver.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, sin
from typing import Any

from isaaclab_quadruped.deployment.observation_schema import GO2_JOINT_NAMES, validate_joint_names


@dataclass(frozen=True)
class FakeStatePublisher:
    """Generate deterministic state and command dictionaries for local tests."""

    joint_names: tuple[str, ...] = GO2_JOINT_NAMES
    dt_s: float = 0.02

    def validate(self) -> None:
        validate_joint_names(self.joint_names)
        if self.dt_s <= 0.0:
            raise ValueError("dt_s must be positive")

    def joint_state(self, step: int) -> dict[str, Any]:
        """Return deterministic joint positions and velocities."""

        self.validate()
        if step < 0:
            raise ValueError("step must be non-negative")
        phase = step * self.dt_s
        positions = [
            round(0.1 * sin(phase + index * 0.2), 6) for index in range(len(self.joint_names))
        ]
        velocities = [
            round(0.1 * cos(phase + index * 0.2), 6) for index in range(len(self.joint_names))
        ]
        return {
            "stamp_s": round(phase, 6),
            "name": list(self.joint_names),
            "position": positions,
            "velocity": velocities,
        }

    def imu(self, step: int) -> dict[str, Any]:
        """Return deterministic IMU-like orientation, angular velocity, and acceleration."""

        self.validate()
        if step < 0:
            raise ValueError("step must be non-negative")
        phase = step * self.dt_s
        return {
            "stamp_s": round(phase, 6),
            "orientation_xyzw": [
                round(0.01 * sin(phase), 6),
                round(0.01 * cos(phase), 6),
                round(0.02 * sin(phase * 0.5), 6),
                1.0,
            ],
            "angular_velocity_xyz": [
                round(0.05 * sin(phase), 6),
                round(0.05 * cos(phase), 6),
                round(0.02 * sin(phase * 0.25), 6),
            ],
            "linear_acceleration_xyz": [
                round(0.1 * sin(phase), 6),
                round(0.1 * cos(phase), 6),
                9.81,
            ],
        }

    def command_velocity(
        self,
        linear_x: float = 0.5,
        linear_y: float = 0.0,
        angular_z: float = 0.1,
    ) -> dict[str, Any]:
        """Return a plain dictionary shaped like a planar velocity command."""

        return {
            "linear": {"x": float(linear_x), "y": float(linear_y), "z": 0.0},
            "angular": {"x": 0.0, "y": 0.0, "z": float(angular_z)},
        }

    def sample(self, step: int) -> dict[str, Any]:
        """Return a complete deterministic fake bridge sample."""

        return {
            "joint_state": self.joint_state(step),
            "imu": self.imu(step),
            "command_velocity": self.command_velocity(),
        }
