from __future__ import annotations

import pytest

from isaaclab_quadruped.deployment.observation_schema import (
    GO2_JOINT_NAMES,
    ObservationField,
    ObservationSchema,
    default_go2_observation_schema,
    validate_joint_names,
)


def test_default_go2_observation_schema_has_expected_layout() -> None:
    schema = default_go2_observation_schema()

    schema.validate(expected_dimension=45)

    assert schema.dimension == 45
    assert schema.joint_names == GO2_JOINT_NAMES
    assert schema.field_names == (
        "base_angular_velocity",
        "projected_gravity",
        "command_velocity",
        "joint_positions",
        "joint_velocities",
        "previous_actions",
    )


def test_observation_schema_rejects_bad_vector_length() -> None:
    schema = default_go2_observation_schema()

    with pytest.raises(ValueError, match="observation dimension"):
        schema.validate_vector([0.0] * 44)


def test_observation_schema_rejects_duplicate_joint_names() -> None:
    with pytest.raises(ValueError, match="unique"):
        validate_joint_names(["joint_a", "joint_a"])


def test_observation_schema_rejects_duplicate_fields() -> None:
    schema = ObservationSchema(
        fields=(
            ObservationField("duplicate", 1, "first"),
            ObservationField("duplicate", 1, "second"),
        ),
        joint_names=("joint_a",),
    )

    with pytest.raises(ValueError, match="unique"):
        schema.validate()
