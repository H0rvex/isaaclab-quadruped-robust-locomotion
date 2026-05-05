# ROS 2 Bridge Plan

This plan documents the local ROS 2 bridge contract scaffold. The repository currently defines
topic names, message-type strings, bridge timing values, and deterministic fake message payloads.
It does not include a ROS 2 node, launch file, robot driver, or hardware communication layer.

## Local Topic Contract

The source of truth is:

- `configs/deployment/ros2_topics.yaml`
- `source/isaaclab_quadruped/ros2_bridge/topic_contracts.py`
- `source/isaaclab_quadruped/ros2_bridge/bridge_config.py`

Configured bridge values:

| Item | Value |
| --- | --- |
| Namespace | `/go2` |
| Policy rate | 50 Hz |
| Command timeout | 0.25 seconds |
| State timeout | 0.1 seconds |

Topic contract:

| Topic | Message type | Direction | Purpose |
| --- | --- | --- | --- |
| `/go2/joint_states` | `sensor_msgs/msg/JointState` | publish | Joint position and velocity state |
| `/go2/imu` | `sensor_msgs/msg/Imu` | publish | Base orientation, angular velocity, and acceleration |
| `/go2/cmd_vel` | `geometry_msgs/msg/Twist` | subscribe | Operator or planner velocity command |
| `/go2/policy_action` | `trajectory_msgs/msg/JointTrajectory` | publish | Policy-generated joint target output |

The local validators check absolute topic names, unique topic names, non-empty message types, and
the expected publish/subscribe directions.

## Fake State Publisher

`FakeStatePublisher` emits deterministic plain Python dictionaries for local testing:

- `joint_state(step)` returns `stamp_s`, `name`, `position`, and `velocity`.
- `imu(step)` returns orientation, angular velocity, and linear acceleration fields.
- `command_velocity(...)` returns a dictionary shaped like a planar velocity command.
- `sample(step)` combines one joint-state message, one IMU message, and one command message.

The fake publisher exists to test parsing and interface assumptions on a local machine without
ROS 2, Isaac Sim, or robot hardware. It is not a physics model, sensor model, state estimator, or
driver.

## Future Runtime Bridge

A real bridge should be implemented only in a runtime-specific module that imports ROS 2 libraries
inside the rented or robot runtime environment. The local package should continue to avoid
`rclpy`, Isaac Lab, Isaac Sim, `omni`, and `pxr` imports.

Expected future runtime responsibilities:

1. Subscribe to `/go2/joint_states`, `/go2/imu`, and `/go2/cmd_vel`.
2. Assemble the 45-element policy observation in the documented order.
3. Run the exported policy at 50 Hz.
4. Clamp or reject action outputs outside the normalized safety envelope.
5. Convert normalized actions into joint targets using the documented action scale.
6. Publish `/go2/policy_action`.
7. Drop stale velocity commands after `0.25` seconds.
8. Fail closed on missing state, stale state, invalid policy output, or driver errors.

## Runtime Requirements

The following require a ROS 2 and robot-specific runtime and are not local-only:

- `rclpy` publishers and subscribers
- ROS 2 launch files
- Unitree driver integration
- real-time scheduling assumptions
- network setup to the robot
- emergency stop integration
- hardware safety monitoring
- hardware-in-the-loop tests

Isaac Sim and Isaac Lab validation also remain rented-GPU tasks. They are separate from ROS 2
runtime validation.

## Limitations

This bridge plan is a contract scaffold. It does not validate real robot behavior, actuator
limits, timing jitter, packet loss, state-estimator quality, terrain interaction, fall recovery, or
operator safety. Real hardware work requires a separate driver implementation and a controlled
validation procedure.
