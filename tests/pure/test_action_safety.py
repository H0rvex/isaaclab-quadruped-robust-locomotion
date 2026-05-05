from __future__ import annotations

import pytest

from isaaclab_quadruped.deployment.action_scaling import ActionScaling
from isaaclab_quadruped.deployment.observation_schema import GO2_JOINT_NAMES
from isaaclab_quadruped.deployment.safety import SafetyLimits


def make_safety() -> SafetyLimits:
    return SafetyLimits(
        joint_names=GO2_JOINT_NAMES,
        action_lower=(-1.0,) * 12,
        action_upper=(1.0,) * 12,
        command_timeout_s=0.25,
        max_linear_velocity_mps=1.5,
        max_angular_velocity_radps=1.5,
    )


def test_action_scaling_maps_normalized_action_to_joint_targets() -> None:
    scaling = ActionScaling(
        joint_names=GO2_JOINT_NAMES,
        scale=0.25,
        default_joint_positions=(0.0,) * 12,
    )

    assert scaling.scale_action([1.0, -1.0, 0.0, 0.5, -0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])[
        :5
    ] == (0.25, -0.25, 0.0, 0.125, -0.125)


def test_action_scaling_rejects_invalid_scale_and_dimension() -> None:
    scaling = ActionScaling(
        joint_names=GO2_JOINT_NAMES,
        scale=0.0,
        default_joint_positions=(0.0,) * 12,
    )

    with pytest.raises(ValueError, match="scale"):
        scaling.validate()

    valid_scaling = ActionScaling(
        joint_names=GO2_JOINT_NAMES,
        scale=0.25,
        default_joint_positions=(0.0,) * 12,
    )
    with pytest.raises(ValueError, match="dimension"):
        valid_scaling.scale_action([0.0] * 11)


def test_safety_validates_action_limits_and_timeout() -> None:
    safety = make_safety()

    safety.validate_action([0.0] * 12)

    assert safety.clamp_action([2.0] * 12) == (1.0,) * 12
    assert safety.is_command_fresh(0.25)
    assert not safety.is_command_fresh(0.251)


def test_safety_rejects_action_and_command_outside_limits() -> None:
    safety = make_safety()

    with pytest.raises(ValueError, match="outside limits"):
        safety.validate_action([1.2] + [0.0] * 11)
    with pytest.raises(ValueError, match="linear_x"):
        safety.validate_command(linear_x=2.0, linear_y=0.0, angular_z=0.0)
    with pytest.raises(ValueError, match="angular_z"):
        safety.validate_command(linear_x=0.0, linear_y=0.0, angular_z=2.0)
