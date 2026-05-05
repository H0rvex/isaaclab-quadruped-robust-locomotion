from __future__ import annotations

from isaaclab_quadruped.deployment.observation_schema import GO2_JOINT_NAMES
from isaaclab_quadruped.ros2_bridge.fake_state import FakeStatePublisher


def test_fake_state_publisher_is_deterministic() -> None:
    publisher = FakeStatePublisher()

    assert publisher.sample(5) == publisher.sample(5)
    assert publisher.sample(5) != publisher.sample(6)


def test_fake_joint_state_contains_joint_positions_and_velocities() -> None:
    publisher = FakeStatePublisher()
    joint_state = publisher.joint_state(0)

    assert joint_state["name"] == list(GO2_JOINT_NAMES)
    assert len(joint_state["position"]) == 12
    assert len(joint_state["velocity"]) == 12
    assert joint_state["position"][0] == 0.0
    assert joint_state["velocity"][0] == 0.1


def test_fake_imu_and_command_velocity_are_plain_dictionaries() -> None:
    publisher = FakeStatePublisher()

    imu = publisher.imu(0)
    command = publisher.command_velocity(linear_x=0.4, linear_y=-0.1, angular_z=0.2)

    assert imu["orientation_xyzw"] == [0.0, 0.01, 0.0, 1.0]
    assert imu["linear_acceleration_xyz"][-1] == 9.81
    assert command == {
        "linear": {"x": 0.4, "y": -0.1, "z": 0.0},
        "angular": {"x": 0.0, "y": 0.0, "z": 0.2},
    }
