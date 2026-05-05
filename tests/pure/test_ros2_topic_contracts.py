from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from isaaclab_quadruped.ros2_bridge.bridge_config import BridgeConfig
from isaaclab_quadruped.ros2_bridge.topic_contracts import (
    Ros2TopicContracts,
    TopicContract,
    default_go2_topic_contracts,
)


def test_default_go2_topics_are_valid_and_absolute() -> None:
    topics = default_go2_topic_contracts()

    topics.validate()

    assert topics.joint_state.name == "/go2/joint_states"
    assert topics.command_velocity.direction == "subscribe"
    assert topics.policy_action.direction == "publish"


def test_topic_contracts_reject_bad_names_and_duplicates() -> None:
    with pytest.raises(ValueError, match="absolute"):
        TopicContract("go2/cmd_vel", "geometry_msgs/msg/Twist", "subscribe").validate()

    duplicate = Ros2TopicContracts(
        joint_state=TopicContract("/go2/state", "sensor_msgs/msg/JointState", "publish"),
        imu=TopicContract("/go2/state", "sensor_msgs/msg/Imu", "publish"),
        command_velocity=TopicContract("/go2/cmd_vel", "geometry_msgs/msg/Twist", "subscribe"),
        policy_action=TopicContract(
            "/go2/policy_action", "trajectory_msgs/msg/JointTrajectory", "publish"
        ),
    )
    with pytest.raises(ValueError, match="unique"):
        duplicate.validate()


def test_bridge_config_validates_topics_and_timeouts() -> None:
    config = BridgeConfig(
        namespace="/go2",
        policy_rate_hz=50.0,
        command_timeout_s=0.25,
        state_timeout_s=0.1,
        topics=default_go2_topic_contracts(),
    )

    config.validate()


def test_ros2_topics_yaml_has_required_contract_values() -> None:
    data = yaml.safe_load(Path("configs/deployment/ros2_topics.yaml").read_text(encoding="utf-8"))

    assert data["bridge"]["namespace"] == "/go2"
    assert data["bridge"]["command_timeout_s"] == 0.25
    assert data["topics"]["joint_state"]["name"] == "/go2/joint_states"
    assert data["topics"]["command_velocity"]["direction"] == "subscribe"
