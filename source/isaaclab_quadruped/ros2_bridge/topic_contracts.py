"""ROS 2 topic-name contracts for the local bridge boundary.

These dataclasses validate topic names and expected message types using plain
strings. They do not create publishers, subscribers, or real robot drivers.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class TopicContract:
    """One bridge topic endpoint."""

    name: str
    message_type: str
    direction: str
    required: bool = True

    def validate(self) -> None:
        if not self.name.startswith("/"):
            raise ValueError(f"topic name must be absolute: {self.name}")
        if " " in self.name or "//" in self.name:
            raise ValueError(f"invalid topic name: {self.name}")
        if not self.message_type:
            raise ValueError("message_type must not be empty")
        if self.direction not in {"publish", "subscribe"}:
            raise ValueError("direction must be publish or subscribe")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Ros2TopicContracts:
    """Topic contract set expected by the future deployment bridge."""

    joint_state: TopicContract
    imu: TopicContract
    command_velocity: TopicContract
    policy_action: TopicContract

    def validate(self) -> None:
        topics = self.as_tuple()
        for topic in topics:
            topic.validate()
        names = tuple(topic.name for topic in topics)
        if len(set(names)) != len(names):
            raise ValueError("topic names must be unique")
        if self.command_velocity.direction != "subscribe":
            raise ValueError("command_velocity topic must be a subscription")
        if self.policy_action.direction != "publish":
            raise ValueError("policy_action topic must be a publisher")

    def as_tuple(self) -> tuple[TopicContract, ...]:
        return (self.joint_state, self.imu, self.command_velocity, self.policy_action)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def default_go2_topic_contracts(namespace: str = "/go2") -> Ros2TopicContracts:
    """Return the default local topic contract set for Go2 deployment."""

    root = namespace.rstrip("/")
    if not root.startswith("/"):
        raise ValueError("namespace must start with /")
    return Ros2TopicContracts(
        joint_state=TopicContract(f"{root}/joint_states", "sensor_msgs/msg/JointState", "publish"),
        imu=TopicContract(f"{root}/imu", "sensor_msgs/msg/Imu", "publish"),
        command_velocity=TopicContract(f"{root}/cmd_vel", "geometry_msgs/msg/Twist", "subscribe"),
        policy_action=TopicContract(
            f"{root}/policy_action", "trajectory_msgs/msg/JointTrajectory", "publish"
        ),
    )
