"""Local bridge configuration contracts.

BridgeConfig ties topic contracts to policy timing and command timeout values.
It is a local validation object only, not a ROS 2 launch file or driver.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from isaaclab_quadruped.ros2_bridge.topic_contracts import Ros2TopicContracts


@dataclass(frozen=True)
class BridgeConfig:
    """Validated local config for the future policy-to-ROS bridge."""

    namespace: str
    policy_rate_hz: float
    command_timeout_s: float
    state_timeout_s: float
    topics: Ros2TopicContracts

    def validate(self) -> None:
        if not self.namespace.startswith("/"):
            raise ValueError("namespace must start with /")
        if self.policy_rate_hz <= 0.0:
            raise ValueError("policy_rate_hz must be positive")
        if self.command_timeout_s <= 0.0:
            raise ValueError("command_timeout_s must be positive")
        if self.state_timeout_s <= 0.0:
            raise ValueError("state_timeout_s must be positive")
        self.topics.validate()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
