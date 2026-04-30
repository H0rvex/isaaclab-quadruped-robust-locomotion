# Rented GPU Runbook

This runbook is the paid-GPU execution checklist for Isaac Lab runtime validation and first training smoke tests.

## 0. Machine Requirements

Recommended:
- Ubuntu 22.04 or 24.04
- RTX 4090 / L40 / L40S-class GPU
- 32-64 GB RAM
- 200 GB disk minimum, 500 GB preferred
- NVIDIA driver compatible with CUDA 12.x

## 1. Initial Machine Check

```bash
nvidia-smi
df -h
free -h
python3 --version
```

## 2. Workspace Setup

```bash
mkdir -p /mnt/data/robotics
cd /mnt/data/robotics

git clone https://github.com/<USER>/isaaclab-quadruped-robust-locomotion.git
git clone https://github.com/isaac-sim/IsaacLab.git

cd IsaacLab
git checkout v2.3.2
```

## 3. Set Paths

```bash
export ISAACLAB_PATH=/mnt/data/robotics/IsaacLab
export PROJECT_ROOT=/mnt/data/robotics/isaaclab-quadruped-robust-locomotion
export RESULTS_DIR="$PROJECT_ROOT/results"
```

Optional persistent shell setup:

```bash
echo 'export ISAACLAB_PATH=/mnt/data/robotics/IsaacLab' >> ~/.bashrc
echo 'export PROJECT_ROOT=/mnt/data/robotics/isaaclab-quadruped-robust-locomotion' >> ~/.bashrc
echo 'export RESULTS_DIR="$PROJECT_ROOT/results"' >> ~/.bashrc
source ~/.bashrc
```

## 4. Runtime Install

```bash
cd "$PROJECT_ROOT"
bash scripts/setup_runtime_isaaclab.sh
```

If install fails:

Record error in reports/rental_gpu_log.md.
Do not start training.
Fix install/runtime first.

## 5. Runtime Validation

```bash
cd "$PROJECT_ROOT"
bash scripts/validate_runtime_isaaclab.sh
```

Expected:

nvidia-smi works.
PyTorch CUDA works.
Isaac Lab wrapper works.
Isaac Sim app launches.
Environments can be listed.
Go2/Unitree or ANYmal candidate tasks appear.

## 6. Sim Tests

```bash
cd "$PROJECT_ROOT"
RUN_SIM_TESTS=1 ISAACLAB_PATH="$ISAACLAB_PATH" python -m pytest tests/sim -q
```

If these fail due to runtime/import/CUDA/Isaac errors, stop and fix before training.

## 7. Environment Discovery

```bash
cd "$PROJECT_ROOT"
bash scripts/list_envs.sh
```

Preferred tasks:

Isaac-Velocity-Flat-Unitree-Go2-v0
Isaac-Velocity-Rough-Unitree-Go2-v0

Fallback tasks:

Isaac-Velocity-Flat-Anymal-C-v0
Isaac-Velocity-Rough-Anymal-C-v0
Isaac-Velocity-Flat-Anymal-D-v0
Isaac-Velocity-Rough-Anymal-D-v0

Record selected task IDs in reports/rental_gpu_log.md.

## 8. First Training Smoke Test

```bash
cd "$PROJECT_ROOT"

TASK_ID=Isaac-Velocity-Flat-Unitree-Go2-v0 \
MAX_ITERATIONS=10 \
SEED=1 \
bash scripts/train_go2_flat.sh
```

If Go2 fails, retry with ANYmal fallback:

```bash
TASK_ID=Isaac-Velocity-Flat-Anymal-C-v0 \
MAX_ITERATIONS=10 \
SEED=1 \
bash scripts/train_go2_flat.sh
```

## 9. Play / Video Smoke Test

Use the checkpoint produced by the 10-iteration run.

```bash
TASK_ID=<TASK_ID> \
CHECKPOINT_PATH=<PATH_TO_MODEL_PT> \
bash scripts/play_policy.sh
```

Then:

```bash
TASK_ID=<TASK_ID> \
CHECKPOINT_PATH=<PATH_TO_MODEL_PT> \
bash scripts/record_video.sh
```

## Completion Criteria

- Isaac Sim launches.
- Isaac Lab imports correctly.
- RSL-RL is installed.
- Locomotion envs are discoverable.
- A 10-iteration RSL-RL train run completes.
- Play or video script works.
- Failures and selected task IDs are logged.

## 10. First Real Baseline 

```bash
TASK_ID=<SELECTED_FLAT_TASK> \
MAX_ITERATIONS=<BASELINE_ITERATIONS> \
SEED=1 \
bash scripts/train_go2_flat.sh
```

Then repeat for seeds 2 and 3.
