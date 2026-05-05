# Policy Export Plan

This plan describes how the local policy interface contract should be used when a trained Isaac Lab
policy is exported. It is a plan and contract document only; this repository does not yet include a
complete policy exporter or hardware inference runtime.

## Local Contract

The source of truth for the policy interface is:

- `configs/deployment/go2_policy_interface.yaml`
- `source/isaaclab_quadruped/deployment/policy_contract.py`
- `source/isaaclab_quadruped/deployment/export_metadata.py`

The exported policy must match:

| Item | Required value |
| --- | --- |
| Observation dimension | 45 |
| Action dimension | 12 |
| Control rate | 50 Hz |
| Joint order | Go2 joint list in `observation_schema.py` |
| Action scale | 0.25 |
| Normalized action limits | `[-1.0, 1.0]` per joint |
| Command timeout | 0.25 seconds |
| Expected export format | TorchScript first; ONNX acceptable later |

The local tests validate shape and metadata consistency. They do not prove policy quality,
closed-loop stability, or robot safety.

## Export Metadata

Each exported artifact should carry metadata that can be validated against
`PolicyInterfaceContract`:

- `policy_name`
- `artifact_path`
- `checkpoint_path`
- `export_format`
- `observation_dim`
- `action_dim`
- `joint_names`
- `source_config`
- `created_by`

The local `PolicyExportMetadata.validate_against(...)` method checks that metadata dimensions,
joint names, and policy name match the interface contract.

## Rented-GPU Export Workflow

Run this workflow only after Isaac Lab training has produced a checkpoint on the rented GPU
machine.

1. Validate the rented runtime:

   ```bash
   export ISAACLAB_PATH=/path/to/IsaacLab
   export PROJECT_ROOT=/path/to/isaaclab-quadruped-robust-locomotion
   cd "$PROJECT_ROOT"
   bash scripts/validate_runtime_isaaclab.sh
   ```

2. Select the source checkpoint and config:

   ```bash
   export CHECKPOINT_PATH=/path/to/policy_checkpoint.pt
   export SOURCE_CONFIG=configs/go2_rough_dr_curriculum.yaml
   ```

3. Export the policy using the Isaac Lab or RSL-RL runtime exporter once that exporter is added.
   The initial target should be a TorchScript artifact.

4. Write export metadata beside the artifact and validate it against
   `configs/deployment/go2_policy_interface.yaml`.

5. Run deterministic evaluation in simulation before considering any bridge or hardware work.

## Acceptance Gates

A policy export is not portfolio-ready unless the repository records:

- exact training config
- checkpoint path or artifact reference
- export command
- export metadata
- policy input/output dimensions
- evaluation JSON summary
- simulation rollout evidence from the rented GPU runtime
- known failure modes and limitations

## Limitations

This plan does not implement policy export, real-time inference, ROS 2 transport, actuator
commands, safety supervision, or real robot validation. It only defines the evidence and interface
checks required before those steps are credible.
