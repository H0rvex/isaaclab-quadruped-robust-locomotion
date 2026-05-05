from __future__ import annotations

from pathlib import Path

from isaaclab_quadruped.deployment.interface_demo import (
    build_policy_contract,
    deterministic_policy_action,
    format_plain_summary,
    observation_from_fake_state,
    read_yaml,
    run_interface_demo,
)
from isaaclab_quadruped.ros2_bridge.fake_state import FakeStatePublisher


def test_run_interface_demo_returns_summary_and_writes_json(tmp_path: Path) -> None:
    json_out = tmp_path / "local_interface_demo.json"

    summary = run_interface_demo(
        policy_config_path=Path("configs/deployment/go2_policy_interface.yaml"),
        topics_config_path=Path("configs/deployment/ros2_topics.yaml"),
        json_out=json_out,
        step=5,
    )

    assert summary["policy_name"] == "go2_hardware_interface_contract"
    assert summary["observation_dim"] == 45
    assert summary["action_dim"] == 12
    assert summary["joint_count"] == 12
    assert summary["command_velocity"] == {"x": 0.5, "y": 0.0, "yaw": 0.1}
    assert summary["observation_validation_status"] == "PASS"
    assert summary["final_status"] == "PASS"
    assert len(summary["raw_action"]) == 12
    assert len(summary["clipped_action"]) == 12
    assert len(summary["scaled_joint_targets"]) == 12
    assert summary["ros2_topic_names"]["joint_state"] == "/go2/joint_states"
    assert summary["ros2_topic_names"]["policy_action"] == "/go2/policy_action"
    assert json_out.exists()
    assert '"final_status": "PASS"' in json_out.read_text(encoding="utf-8")


def test_observation_assembly_matches_contract_order() -> None:
    contract = build_policy_contract(
        read_yaml(Path("configs/deployment/go2_policy_interface.yaml"))
    )
    previous_action = (0.0,) * contract.action_dim
    fake_sample = FakeStatePublisher(joint_names=contract.joint_names).sample(0)

    observation = observation_from_fake_state(
        fake_sample=fake_sample,
        previous_action=previous_action,
    )

    assert len(observation) == contract.observation_dim
    assert observation[:3] == tuple(fake_sample["imu"]["angular_velocity_xyz"])
    assert observation[3:6] == (0.0, 0.0, -1.0)
    assert observation[6:9] == (0.5, 0.0, 0.1)
    assert observation[9:21] == tuple(fake_sample["joint_state"]["position"])
    assert observation[21:33] == tuple(fake_sample["joint_state"]["velocity"])
    assert observation[33:] == previous_action


def test_deterministic_policy_action_is_clipped_and_scaled() -> None:
    contract = build_policy_contract(
        read_yaml(Path("configs/deployment/go2_policy_interface.yaml"))
    )

    raw_action = deterministic_policy_action(contract.action_dim)
    clipped_action = contract.safety_limits.clamp_action(raw_action)
    scaled_joint_targets = contract.action_scaling.scale_action(clipped_action)

    assert raw_action == deterministic_policy_action(contract.action_dim)
    assert clipped_action[0] == -1.0
    assert clipped_action[-1] == 1.0
    assert scaled_joint_targets[0] == -0.15
    assert scaled_joint_targets[-1] == -1.25


def test_plain_summary_includes_reviewer_fields(tmp_path: Path) -> None:
    summary = run_interface_demo(
        policy_config_path=Path("configs/deployment/go2_policy_interface.yaml"),
        topics_config_path=Path("configs/deployment/ros2_topics.yaml"),
        json_out=tmp_path / "demo.json",
    )
    text = format_plain_summary(summary)

    assert "Policy name: go2_hardware_interface_contract" in text
    assert "Observation validation: PASS" in text
    assert "Final status: PASS" in text
