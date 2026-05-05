"""Demonstrate the local policy and ROS 2 interface contracts.

This script is intentionally local-only. It does not import Isaac Lab, Isaac Sim,
ROS 2, rclpy, torch, gymnasium, or ONNX packages.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = PROJECT_ROOT / "source"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from isaaclab_quadruped.deployment.action_scaling import ActionScaling  # noqa: E402
from isaaclab_quadruped.deployment.observation_schema import (  # noqa: E402
    ObservationField,
    ObservationSchema,
)
from isaaclab_quadruped.deployment.policy_contract import PolicyInterfaceContract  # noqa: E402
from isaaclab_quadruped.deployment.safety import SafetyLimits  # noqa: E402
from isaaclab_quadruped.ros2_bridge.fake_state import FakeStatePublisher  # noqa: E402
from isaaclab_quadruped.ros2_bridge.topic_contracts import (  # noqa: E402
    Ros2TopicContracts,
    TopicContract,
)
from isaaclab_quadruped.utils.result_io import read_yaml  # noqa: E402


def build_policy_contract(config: dict[str, Any]) -> PolicyInterfaceContract:
    """Build a local policy contract from the deployment YAML config."""

    joint_names = tuple(str(name) for name in config["joint_names"])
    fields = tuple(
        ObservationField(
            name=str(field["name"]),
            size=int(field["size"]),
            description=str(field.get("description", "")),
        )
        for field in config["observation_schema"]["fields"]
    )
    observation_schema = ObservationSchema(fields=fields, joint_names=joint_names)
    action_scaling = ActionScaling(
        joint_names=joint_names,
        scale=float(config["action_scaling"]["scale"]),
        default_joint_positions=tuple(
            float(value) for value in config["action_scaling"]["default_joint_positions"]
        ),
    )
    safety_limits = SafetyLimits(
        joint_names=joint_names,
        action_lower=tuple(float(value) for value in config["safety"]["action_lower"]),
        action_upper=tuple(float(value) for value in config["safety"]["action_upper"]),
        command_timeout_s=float(config["safety"]["command_timeout_s"]),
        max_linear_velocity_mps=float(config["safety"]["max_linear_velocity_mps"]),
        max_angular_velocity_radps=float(config["safety"]["max_angular_velocity_radps"]),
    )
    contract = PolicyInterfaceContract(
        policy_name=str(config["policy"]["name"]),
        observation_schema=observation_schema,
        action_scaling=action_scaling,
        safety_limits=safety_limits,
        control_rate_hz=float(config["policy"]["control_rate_hz"]),
        exported_action_dim=int(config["policy"]["action_dim"]),
        exported_observation_dim=int(config["policy"]["observation_dim"]),
    )
    contract.validate()
    return contract


def build_topic_contracts(config: dict[str, Any]) -> Ros2TopicContracts:
    """Build ROS 2 topic-name contracts from the local YAML config."""

    topics = config["topics"]
    contracts = Ros2TopicContracts(
        joint_state=_topic_contract(topics["joint_state"]),
        imu=_topic_contract(topics["imu"]),
        command_velocity=_topic_contract(topics["command_velocity"]),
        policy_action=_topic_contract(topics["policy_action"]),
    )
    contracts.validate()
    return contracts


def _topic_contract(data: dict[str, Any]) -> TopicContract:
    return TopicContract(
        name=str(data["name"]),
        message_type=str(data["message_type"]),
        direction=str(data["direction"]),
        required=bool(data.get("required", True)),
    )


def command_velocity_vector(command_velocity: dict[str, Any]) -> tuple[float, float, float]:
    """Extract x, y, and yaw velocity from a dictionary-shaped command."""

    return (
        float(command_velocity["linear"]["x"]),
        float(command_velocity["linear"]["y"]),
        float(command_velocity["angular"]["z"]),
    )


def observation_from_fake_state(
    *,
    fake_sample: dict[str, Any],
    previous_action: tuple[float, ...],
) -> tuple[float, ...]:
    """Convert fake bridge dictionaries into the documented flat observation vector."""

    imu = fake_sample["imu"]
    joint_state = fake_sample["joint_state"]
    command_velocity = fake_sample["command_velocity"]
    return (
        *[float(value) for value in imu["angular_velocity_xyz"]],
        0.0,
        0.0,
        -1.0,
        *command_velocity_vector(command_velocity),
        *[float(value) for value in joint_state["position"]],
        *[float(value) for value in joint_state["velocity"]],
        *[float(value) for value in previous_action],
    )


def deterministic_policy_action(action_dim: int) -> tuple[float, ...]:
    """Return a deterministic fake policy action with clipping visible."""

    if action_dim <= 0:
        raise ValueError("action_dim must be positive")
    return tuple(round(-1.2 + 0.24 * index, 6) for index in range(action_dim))


def topic_names(topics: Ros2TopicContracts) -> dict[str, str]:
    """Return readable topic names for demo output."""

    return {
        "joint_state": topics.joint_state.name,
        "imu": topics.imu.name,
        "command_velocity": topics.command_velocity.name,
        "policy_action": topics.policy_action.name,
    }


def run_demo(
    *,
    policy_config_path: Path = PROJECT_ROOT / "configs/deployment/go2_policy_interface.yaml",
    topics_config_path: Path = PROJECT_ROOT / "configs/deployment/ros2_topics.yaml",
    step: int = 5,
) -> dict[str, Any]:
    """Run the local interface demo and return its summary dictionary."""

    contract = build_policy_contract(read_yaml(policy_config_path))
    topics = build_topic_contracts(read_yaml(topics_config_path))

    previous_action = (0.0,) * contract.action_dim
    fake_sample = FakeStatePublisher(joint_names=contract.joint_names).sample(step)
    observation = observation_from_fake_state(
        fake_sample=fake_sample,
        previous_action=previous_action,
    )
    contract.observation_schema.validate_vector(observation)

    raw_action = deterministic_policy_action(contract.action_dim)
    if len(raw_action) != contract.action_dim:
        raise ValueError(f"action dimension mismatch: {len(raw_action)} != {contract.action_dim}")
    clipped_action = contract.safety_limits.clamp_action(raw_action)
    contract.validate_io(observation, clipped_action)
    scaled_joint_targets = contract.action_scaling.scale_action(clipped_action)

    return {
        "observation_dim": len(observation),
        "action_dim": len(raw_action),
        "joint_names": list(contract.joint_names),
        "command_velocity": {
            "x": fake_sample["command_velocity"]["linear"]["x"],
            "y": fake_sample["command_velocity"]["linear"]["y"],
            "yaw": fake_sample["command_velocity"]["angular"]["z"],
        },
        "raw_action": list(raw_action),
        "clipped_action": list(clipped_action),
        "scaled_joint_targets": list(scaled_joint_targets),
        "ros2_topic_names": topic_names(topics),
    }


def main() -> int:
    """Print a readable local interface summary."""

    summary = run_demo()
    print("Local interface demo")
    print("--------------------")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
