from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType


def load_demo_module() -> ModuleType:
    script_path = Path("scripts/demo_local_interface.py")
    spec = importlib.util.spec_from_file_location("demo_local_interface", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_run_demo_returns_valid_interface_summary() -> None:
    module = load_demo_module()

    summary = module.run_demo(step=5)

    assert summary["observation_dim"] == 45
    assert summary["action_dim"] == 12
    assert len(summary["joint_names"]) == 12
    assert summary["command_velocity"] == {"x": 0.5, "y": 0.0, "yaw": 0.1}
    assert len(summary["raw_action"]) == 12
    assert len(summary["clipped_action"]) == 12
    assert len(summary["scaled_joint_targets"]) == 12
    assert summary["clipped_action"][0] == -1.0
    assert summary["raw_action"][0] == -1.2
    assert summary["ros2_topic_names"]["joint_state"] == "/go2/joint_states"
    assert summary["ros2_topic_names"]["policy_action"] == "/go2/policy_action"


def test_observation_assembly_matches_contract_order() -> None:
    module = load_demo_module()
    policy_config = module.read_yaml(Path("configs/deployment/go2_policy_interface.yaml"))
    contract = module.build_policy_contract(policy_config)
    previous_action = (0.0,) * contract.action_dim
    fake_sample = module.FakeStatePublisher(joint_names=contract.joint_names).sample(0)

    observation = module.observation_from_fake_state(
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
    module = load_demo_module()
    contract = module.build_policy_contract(
        module.read_yaml(Path("configs/deployment/go2_policy_interface.yaml"))
    )

    raw_action = module.deterministic_policy_action(contract.action_dim)
    clipped_action = contract.safety_limits.clamp_action(raw_action)
    scaled_joint_targets = contract.action_scaling.scale_action(clipped_action)

    assert raw_action == module.deterministic_policy_action(contract.action_dim)
    assert clipped_action[0] == -1.0
    assert clipped_action[-1] == 1.0
    assert scaled_joint_targets[0] == -0.15
    assert scaled_joint_targets[-1] == -1.25
