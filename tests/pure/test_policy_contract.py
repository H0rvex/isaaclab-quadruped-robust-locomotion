from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from isaaclab_quadruped.deployment.action_scaling import ActionScaling
from isaaclab_quadruped.deployment.observation_schema import (
    GO2_JOINT_NAMES,
    default_go2_observation_schema,
)
from isaaclab_quadruped.deployment.policy_contract import PolicyInterfaceContract
from isaaclab_quadruped.deployment.safety import SafetyLimits


def make_contract() -> PolicyInterfaceContract:
    schema = default_go2_observation_schema()
    scaling = ActionScaling(
        joint_names=GO2_JOINT_NAMES,
        scale=0.25,
        default_joint_positions=(0.0,) * len(GO2_JOINT_NAMES),
    )
    safety = SafetyLimits(
        joint_names=GO2_JOINT_NAMES,
        action_lower=(-1.0,) * len(GO2_JOINT_NAMES),
        action_upper=(1.0,) * len(GO2_JOINT_NAMES),
        command_timeout_s=0.25,
        max_linear_velocity_mps=1.5,
        max_angular_velocity_radps=1.5,
    )
    return PolicyInterfaceContract(
        policy_name="go2_hardware_interface_contract",
        observation_schema=schema,
        action_scaling=scaling,
        safety_limits=safety,
        control_rate_hz=50.0,
        exported_action_dim=len(GO2_JOINT_NAMES),
        exported_observation_dim=schema.dimension,
    )


def test_policy_contract_validates_expected_dimensions() -> None:
    contract = make_contract()

    contract.validate()
    contract.validate_io([0.0] * 45, [0.0] * 12)

    assert contract.observation_dim == 45
    assert contract.action_dim == 12


def test_policy_contract_rejects_dimension_mismatch() -> None:
    contract = make_contract()
    broken = PolicyInterfaceContract(
        policy_name=contract.policy_name,
        observation_schema=contract.observation_schema,
        action_scaling=contract.action_scaling,
        safety_limits=contract.safety_limits,
        control_rate_hz=contract.control_rate_hz,
        exported_action_dim=11,
        exported_observation_dim=contract.exported_observation_dim,
    )

    with pytest.raises(ValueError, match="action dimension"):
        broken.validate()


def test_go2_policy_interface_yaml_matches_contract_values() -> None:
    data = yaml.safe_load(
        Path("configs/deployment/go2_policy_interface.yaml").read_text(encoding="utf-8")
    )
    schema = default_go2_observation_schema()

    assert data["policy"]["observation_dim"] == schema.dimension
    assert data["policy"]["action_dim"] == len(GO2_JOINT_NAMES)
    assert tuple(data["joint_names"]) == GO2_JOINT_NAMES
    assert data["action_scaling"]["scale"] == 0.25
    assert len(data["action_scaling"]["default_joint_positions"]) == len(GO2_JOINT_NAMES)
    assert len(data["safety"]["action_lower"]) == len(GO2_JOINT_NAMES)
    assert len(data["safety"]["action_upper"]) == len(GO2_JOINT_NAMES)
    assert data["safety"]["command_timeout_s"] == 0.25
