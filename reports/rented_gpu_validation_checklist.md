# Rented GPU Validation Checklist

Use this checklist on the rented GPU machine before launching long training runs.

## Machine

- GPU: RTX 4090, L40, L40S, or similar.
- RAM: 32-64 GB.
- Disk: 200 GB minimum, 500 GB preferred.
- OS: Ubuntu 22.04 or 24.04.
- NVIDIA driver visible through `nvidia-smi`.

## Environment Variables

```bash
export ISAACLAB_PATH=/path/to/IsaacLab
export PROJECT_ROOT=/path/to/isaaclab-quadruped-robust-locomotion
export RESULTS_DIR="$PROJECT_ROOT/results"
```

Validation scripts fail early if `ISAACLAB_PATH` is unset or does not contain `isaaclab.sh`.

## Setup

```bash
cd "$PROJECT_ROOT"
bash scripts/setup_runtime_isaaclab.sh
```

Expected result:

- IsaacLab is checked out at `v2.3.2`.
- Isaac Sim `5.1.0` is installed.
- PyTorch `2.7.0+cu128` is installed.
- Isaac Lab RSL-RL extras are installed.
- This external project is installed editable when package metadata is present.

## Runtime Validation

```bash
cd "$PROJECT_ROOT"
bash scripts/validate_runtime_isaaclab.sh
```

The validation script runs:

1. Path checks for `ISAACLAB_PATH`.
2. Python import checks for `torch`, `isaacsim`, `isaaclab`, and `pxr`.
3. `nvidia-smi`.
4. Isaac Lab environment listing.
5. Go2/ANYmal environment filtering.
6. `scripts/tutorials/00_sim/create_empty.py --headless`.

## Optional Pytest Simulation Gate

Simulation tests are skipped by default. Run them only on the rented GPU machine:

```bash
cd "$PROJECT_ROOT"
RUN_SIM_TESTS=1 ISAACLAB_PATH="$ISAACLAB_PATH" python -m pytest tests/sim -q
```

Do not run these tests on the local GTX 1060 machine.

## First Training Smoke

After runtime validation passes, choose an exact task ID from the environment list:

```bash
export TASK_ID=<GO2_OR_ANYMAL_TASK_ID>
export NUM_ENVS=128
export MAX_ITERATIONS=10
export SEED=1
bash scripts/train_go2_flat.sh
```

Record the command, task ID, output log path, and whether the run reached iteration 10.

## Evidence To Save

- `nvidia-smi` output.
- Isaac Lab commit and project commit.
- Version matrix in `configs/version_matrix.md`.
- Import-check output.
- Environment list output showing Go2/ANYmal availability.
- Empty-scene smoke output.
- First training smoke log.
- Any failure tracebacks.

## Stop Conditions

Stop and record evidence before spending more GPU time if:

- `isaacsim`, `isaaclab`, or `pxr` cannot import.
- `create_empty.py --headless` fails.
- Go2 is unavailable and the ANYmal fallback has not been selected.
- A short RSL-RL run cannot start.
