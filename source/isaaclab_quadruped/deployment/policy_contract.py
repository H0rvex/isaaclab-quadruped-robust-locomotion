"""Policy interface contracts for local hardware-readiness checks.

The policy contract binds expected observation shape, action shape, joint order,
action scaling, and safety limits. It is deliberately pure Python and does not
load a policy runtime or command a robot.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from isaaclab_quadruped.deployment.action_scaling import ActionScaling
from isaaclab_quadruped.deployment.observation_schema import ObservationSchema
from isaaclab_quadruped.deployment.safety import SafetyLimits


@dataclass(frozen=True)
class PolicyInterfaceContract:
    """End-to-end interface expected by an exported quadruped policy."""

    policy_name: str
    observation_schema: ObservationSchema
    action_scaling: ActionScaling
    safety_limits: SafetyLimits
    control_rate_hz: float
    exported_action_dim: int
    exported_observation_dim: int

    @property
    def joint_names(self) -> tuple[str, ...]:
        return self.observation_schema.joint_names

    @property
    def action_dim(self) -> int:
        return len(self.joint_names)

    @property
    def observation_dim(self) -> int:
        return self.observation_schema.dimension

    def validate(self) -> None:
        if not self.policy_name:
            raise ValueError("policy_name must not be empty")
        if self.control_rate_hz <= 0.0:
            raise ValueError("control_rate_hz must be positive")

        self.observation_schema.validate(expected_dimension=self.exported_observation_dim)
        self.action_scaling.validate()
        self.safety_limits.validate()

        if self.exported_action_dim != self.action_dim:
            raise ValueError(
                "exported action dimension mismatch: "
                f"{self.exported_action_dim} != {self.action_dim}"
            )
        if self.action_scaling.joint_names != self.joint_names:
            raise ValueError("action scaling joint_names must match observation schema joint_names")
        if self.safety_limits.joint_names != self.joint_names:
            raise ValueError("safety joint_names must match observation schema joint_names")

    def validate_io(
        self,
        observation: tuple[float, ...] | list[float],
        action: tuple[float, ...] | list[float],
    ) -> None:
        """Validate one policy input and one policy output against the contract."""

        self.validate()
        self.observation_schema.validate_vector(observation)
        self.safety_limits.validate_action(action)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
