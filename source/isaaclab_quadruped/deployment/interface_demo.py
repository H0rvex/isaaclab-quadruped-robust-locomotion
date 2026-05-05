"""Local hardware-interface demo helpers.

The demo uses only local contract code and deterministic dictionary payloads. It
does not import Isaac Lab, Isaac Sim, ROS 2, rclpy, torch, gymnasium, pxr, or
omni.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from isaaclab_quadruped.deployment.action_scaling import ActionScaling
from isaaclab_quadruped.deployment.observation_schema import ObservationField, ObservationSchema
from isaaclab_quadruped.deployment.policy_contract import PolicyInterfaceContract
from isaaclab_quadruped.deployment.safety import SafetyLimits
from isaaclab_quadruped.ros2_bridge.fake_state import FakeStatePublisher
from isaaclab_quadruped.ros2_bridge.topic_contracts import Ros2TopicContracts, TopicContract
from isaaclab_quadruped.utils.result_io import read_yaml

DEFAULT_STEP = 5


def build_policy_contract(config: dict[str, Any]) -> PolicyInterfaceContract:
    """Build a local policy contract from the deployment YAML config."""

    joint_names = tuple(str(name) for name in config["joint_names"])
    observation_schema = ObservationSchema(
        fields=tuple(
            ObservationField(
                name=str(field["name"]),
                size=int(field["size"]),
                description=str(field.get("description", "")),
            )
            for field in config["observation_schema"]["fields"]
        ),
        joint_names=joint_names,
    )
    contract = PolicyInterfaceContract(
        policy_name=str(config["policy"]["name"]),
        observation_schema=observation_schema,
        action_scaling=ActionScaling(
            joint_names=joint_names,
            scale=float(config["action_scaling"]["scale"]),
            default_joint_positions=tuple(
                float(value) for value in config["action_scaling"]["default_joint_positions"]
            ),
        ),
        safety_limits=SafetyLimits(
            joint_names=joint_names,
            action_lower=tuple(float(value) for value in config["safety"]["action_lower"]),
            action_upper=tuple(float(value) for value in config["safety"]["action_upper"]),
            command_timeout_s=float(config["safety"]["command_timeout_s"]),
            max_linear_velocity_mps=float(config["safety"]["max_linear_velocity_mps"]),
            max_angular_velocity_radps=float(config["safety"]["max_angular_velocity_radps"]),
        ),
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


def run_interface_demo(
    *,
    policy_config_path: Path,
    topics_config_path: Path,
    json_out: Path | None = None,
    step: int = DEFAULT_STEP,
) -> dict[str, Any]:
    """Run the local interface demo and optionally save a JSON artifact."""

    contract = build_policy_contract(read_yaml(policy_config_path))
    topics = build_topic_contracts(read_yaml(topics_config_path))

    previous_action = (0.0,) * contract.action_dim
    fake_sample = FakeStatePublisher(joint_names=contract.joint_names).sample(step)
    observation = observation_from_fake_state(
        fake_sample=fake_sample,
        previous_action=previous_action,
    )
    contract.observation_schema.validate_vector(observation)
    observation_validation_status = "PASS"

    raw_action = deterministic_policy_action(contract.action_dim)
    if len(raw_action) != contract.action_dim:
        raise ValueError(f"action dimension mismatch: {len(raw_action)} != {contract.action_dim}")
    clipped_action = contract.safety_limits.clamp_action(raw_action)
    contract.validate_io(observation, clipped_action)
    scaled_joint_targets = contract.action_scaling.scale_action(clipped_action)

    summary = {
        "policy_name": contract.policy_name,
        "observation_dim": len(observation),
        "action_dim": len(raw_action),
        "joint_count": len(contract.joint_names),
        "joint_names": list(contract.joint_names),
        "command_velocity": {
            "x": fake_sample["command_velocity"]["linear"]["x"],
            "y": fake_sample["command_velocity"]["linear"]["y"],
            "yaw": fake_sample["command_velocity"]["angular"]["z"],
        },
        "observation_validation_status": observation_validation_status,
        "action_limits": [
            min(contract.safety_limits.action_lower),
            max(contract.safety_limits.action_upper),
        ],
        "raw_action": list(raw_action),
        "clipped_action": list(clipped_action),
        "scaled_joint_targets": list(scaled_joint_targets),
        "ros2_topic_names": topic_names(topics),
        "final_status": "PASS",
    }
    if json_out is not None:
        write_demo_summary(json_out, summary)
    return summary


def write_demo_summary(path: Path, summary: dict[str, Any]) -> None:
    """Write a machine-readable demo artifact."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")


def format_plain_summary(summary: dict[str, Any]) -> str:
    """Format a compact engineering-style terminal summary."""

    lines = [
        "Local Hardware-Interface Contract Demo",
        "--------------------------------------",
        f"Policy name: {summary.get('policy_name', 'unknown')}",
        f"Observation dimension: {summary.get('observation_dim', 'unknown')}",
        f"Action dimension: {summary.get('action_dim', 'unknown')}",
        f"Joint count: {summary.get('joint_count', 'unknown')}",
        f"Command velocity: {_format_mapping(summary.get('command_velocity', {}))}",
        "",
        f"Observation validation: {summary.get('observation_validation_status', 'FAIL')}",
        "",
        "Action pipeline:",
        f"  Action limits: {_format_sequence(summary.get('action_limits', []))}",
        f"  Raw action: {_format_sequence(summary.get('raw_action', []))}",
        f"  Clipped action: {_format_sequence(summary.get('clipped_action', []))}",
        "  Scaled joint position targets:",
    ]
    lines.extend(
        f"    {joint_name}: {float(target):.3f}"
        for joint_name, target in zip(
            summary.get("joint_names", []),
            summary.get("scaled_joint_targets", []),
            strict=True,
        )
    )
    lines.extend(["", "ROS 2 topic contract:"])
    topics = summary.get("ros2_topic_names", {})
    if isinstance(topics, dict):
        lines.extend(f"  {key}: {value}" for key, value in topics.items())
    else:
        lines.append("  unavailable")
    lines.append("")
    if "json_out" in summary:
        lines.append(f"JSON artifact: {summary['json_out']}")
    if "error" in summary:
        lines.append(f"Error: {summary['error']}")
    lines.append(f"Final status: {summary.get('final_status', 'FAIL')}")
    return "\n".join(lines)


def _format_sequence(values: Any) -> str:
    if not isinstance(values, list | tuple):
        return str(values)
    return "[" + ", ".join(f"{float(value):.3f}" for value in values) + "]"


def _format_mapping(values: Any) -> str:
    if not isinstance(values, dict):
        return str(values)
    return ", ".join(f"{key}={float(value):.3f}" for key, value in values.items())
