# Hardware-Ready Interface Contract

This report documents the local deployment interface scaffold under
`source/isaaclab_quadruped/deployment` and `source/isaaclab_quadruped/ros2_bridge`.
The scaffold is intended to make the project easier to connect to an exported policy and a
future ROS 2 bridge. It is not real robot validation, not a hardware driver, and not a
claim that the policy is safe to run on a Unitree Go2.

## Scope

Local-only code:

- `source/isaaclab_quadruped/deployment/policy_contract.py`
- `source/isaaclab_quadruped/deployment/observation_schema.py`
- `source/isaaclab_quadruped/deployment/action_scaling.py`
- `source/isaaclab_quadruped/deployment/safety.py`
- `source/isaaclab_quadruped/deployment/export_metadata.py`
- `source/isaaclab_quadruped/ros2_bridge/topic_contracts.py`
- `source/isaaclab_quadruped/ros2_bridge/fake_state.py`
- `source/isaaclab_quadruped/ros2_bridge/bridge_config.py`
- `configs/deployment/go2_policy_interface.yaml`
- `configs/deployment/ros2_topics.yaml`

These files use plain Python dataclasses, dictionaries, and YAML. They must remain importable
without Isaac Lab, Isaac Sim, `omni`, `pxr`, or `rclpy`.

Runtime-only work:

- Isaac Lab training and evaluation require the rented GPU environment.
- Isaac Sim app launch, USD/PXR runtime checks, and simulation smoke tests require the rented GPU
  Isaac runtime.
- ROS 2 publishers, subscribers, launch files, hardware drivers, and real robot networking require
  a ROS 2 runtime and robot-specific integration that are not implemented here.

## Policy Input And Output Contract

The policy interface is defined by `PolicyInterfaceContract` and
`configs/deployment/go2_policy_interface.yaml`.

| Field | Contract |
| --- | --- |
| Policy name | `go2_hardware_interface_contract` |
| Robot target | Unitree Go2 interface shape |
| Control rate | 50 Hz |
| Observation dimension | 45 |
| Action dimension | 12 |
| Action representation | normalized joint action vector |
| Output validation | dimension check plus normalized safety limits |

The expected policy input is one flat observation vector with 45 floating-point values. The
expected policy output is one 12-element normalized action vector in the configured joint order.
The local contract can validate dimensions, joint-name consistency, action scale, action limits,
and command timeout values. It does not load a policy runtime or command a robot.

## Observation Schema

The observation vector order is:

| Segment | Size | Description |
| --- | ---: | --- |
| `base_angular_velocity` | 3 | Body-frame angular velocity |
| `projected_gravity` | 3 | Gravity vector projected into body frame |
| `command_velocity` | 3 | Desired x, y, and yaw velocity command |
| `joint_positions` | 12 | Measured joint positions |
| `joint_velocities` | 12 | Measured joint velocities |
| `previous_actions` | 12 | Previous normalized policy action |

The joint order is:

```text
FL_hip_joint
FL_thigh_joint
FL_calf_joint
FR_hip_joint
FR_thigh_joint
FR_calf_joint
RL_hip_joint
RL_thigh_joint
RL_calf_joint
RR_hip_joint
RR_thigh_joint
RR_calf_joint
```

The contract verifies that joint names are present, unique, and shared consistently across
observation, action scaling, and safety definitions.

## Action Scaling And Safety

The local action conversion is:

```text
joint_target = default_joint_position + 0.25 * normalized_action
```

Default joint positions are stored in `configs/deployment/go2_policy_interface.yaml`. The
normalized action limits are `[-1.0, 1.0]` for each of the 12 joints. The local safety contract
also validates:

- `command_timeout_s`: 0.25
- `max_linear_velocity_mps`: 1.5
- `max_angular_velocity_radps`: 1.5

These checks are interface guards. They are not torque limits, motor-temperature limits, contact
checks, balance guarantees, emergency stop handling, or hardware certification.

## ROS 2 Topic Contract

The local ROS 2 bridge contract is documented in `configs/deployment/ros2_topics.yaml`.

| Topic | Message type | Direction |
| --- | --- | --- |
| `/go2/joint_states` | `sensor_msgs/msg/JointState` | publish |
| `/go2/imu` | `sensor_msgs/msg/Imu` | publish |
| `/go2/cmd_vel` | `geometry_msgs/msg/Twist` | subscribe |
| `/go2/policy_action` | `trajectory_msgs/msg/JointTrajectory` | publish |

The local contract checks absolute topic names, uniqueness, message-type strings, and expected
publish/subscribe direction. It does not create ROS 2 publishers or subscribers.

## Fake Robot-State Publisher

`FakeStatePublisher` generates deterministic dictionary payloads for local tests:

- joint names, positions, and velocities
- IMU-like orientation, angular velocity, and linear acceleration fields
- planar command velocity messages

This is useful for validating downstream parsing and schema assumptions without installing ROS 2
or running Isaac Sim. It is not a simulator, not a sensor model, and not a real robot-state source.

## Current Limitation

This scaffold improves interface readiness only. Before any real hardware claim, the project still
needs exported policy artifacts, runtime inference code, a ROS 2 node, robot driver integration,
simulation validation on the rented GPU machine, hardware-in-the-loop testing, emergency stop
handling, and controlled real-robot validation.
