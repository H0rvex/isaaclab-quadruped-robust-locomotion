"""Observation schema contracts for local deployment validation.

These dataclasses describe the vector layout a learned policy expects. They are
interface contracts only, not simulator observations and not real sensor
drivers.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

GO2_JOINT_NAMES: tuple[str, ...] = (
    "FL_hip_joint",
    "FL_thigh_joint",
    "FL_calf_joint",
    "FR_hip_joint",
    "FR_thigh_joint",
    "FR_calf_joint",
    "RL_hip_joint",
    "RL_thigh_joint",
    "RL_calf_joint",
    "RR_hip_joint",
    "RR_thigh_joint",
    "RR_calf_joint",
)


@dataclass(frozen=True)
class ObservationField:
    """One named segment inside the flat policy observation vector."""

    name: str
    size: int
    description: str

    def validate(self) -> None:
        if not self.name:
            raise ValueError("observation field name must not be empty")
        if self.size <= 0:
            raise ValueError(f"observation field {self.name!r} must have positive size")


@dataclass(frozen=True)
class ObservationSchema:
    """Flat observation layout consumed by an exported locomotion policy."""

    fields: tuple[ObservationField, ...]
    joint_names: tuple[str, ...]

    @property
    def dimension(self) -> int:
        return sum(field.size for field in self.fields)

    @property
    def field_names(self) -> tuple[str, ...]:
        return tuple(field.name for field in self.fields)

    def validate(self, expected_dimension: int | None = None) -> None:
        if not self.fields:
            raise ValueError("observation fields must not be empty")
        for field in self.fields:
            field.validate()
        if len(set(self.field_names)) != len(self.field_names):
            raise ValueError("observation field names must be unique")
        validate_joint_names(self.joint_names)
        if expected_dimension is not None and self.dimension != expected_dimension:
            raise ValueError(
                f"observation dimension mismatch: {self.dimension} != {expected_dimension}"
            )

    def validate_vector(self, observation: tuple[float, ...] | list[float]) -> None:
        """Validate the length of one flat observation vector."""

        self.validate()
        if len(observation) != self.dimension:
            raise ValueError(
                f"observation dimension mismatch: {len(observation)} != {self.dimension}"
            )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def validate_joint_names(joint_names: tuple[str, ...] | list[str]) -> None:
    """Validate the joint-name list shared across policy and bridge contracts."""

    if not joint_names:
        raise ValueError("joint_names must not be empty")
    if any(not name for name in joint_names):
        raise ValueError("joint_names must not contain empty names")
    if len(set(joint_names)) != len(joint_names):
        raise ValueError("joint_names must be unique")


def default_go2_observation_schema() -> ObservationSchema:
    """Return the local Go2 deployment observation layout."""

    joint_count = len(GO2_JOINT_NAMES)
    return ObservationSchema(
        fields=(
            ObservationField("base_angular_velocity", 3, "Body-frame angular velocity."),
            ObservationField("projected_gravity", 3, "Gravity vector projected into body frame."),
            ObservationField("command_velocity", 3, "Desired x, y, and yaw velocity command."),
            ObservationField("joint_positions", joint_count, "Measured joint positions."),
            ObservationField("joint_velocities", joint_count, "Measured joint velocities."),
            ObservationField("previous_actions", joint_count, "Last normalized policy action."),
        ),
        joint_names=GO2_JOINT_NAMES,
    )
