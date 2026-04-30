# Install

This repository is an external Isaac Lab project. Local development is intentionally simulator-free. Isaac Sim launch, Isaac Lab environment registration, training, evaluation, and video recording are GPU-machine tasks.

## Local Development Install

Use this setup for editing docs, configs, pure Python utilities, result aggregation, plotting, and tests that do not import Isaac Lab or Isaac Sim.

```bash
conda create -n isaaclab-quad-dev python=3.11 -y
conda activate isaaclab-quad-dev

python -m pip install --upgrade pip
python -m pip install pytest ruff black pyyaml numpy pandas matplotlib rich tqdm
```

If the project has a `pyproject.toml` or `setup.py`, install it editable from the repository root:

```bash
cd /path/to/isaaclab-quadruped-robust-locomotion
python -m pip install -e .
```

Run local checks:

```bash
python -m pytest tests -q
python -m ruff check .
python -m black --check .
```

If `tests/` does not exist yet, create pure tests before treating this as a complete local validation step.

Isaac Sim is not required locally. The local GTX 1060 is for coding only and should not be treated as a supported Isaac Sim training/runtime target.

## Rented GPU Runtime Install

Recommended rented machine:

- RTX 4090, L40, L40S, or similar NVIDIA GPU
- 32-64 GB RAM
- 200 GB disk minimum
- 500 GB disk preferred
- Ubuntu 22.04 or Ubuntu 24.04

The target runtime stack is:

- Isaac Lab v2.3.2
- Isaac Sim 5.1.0
- Python 3.11
- PyTorch 2.7.0 with CUDA 12.8
- RSL-RL

### 1. Create Workspace

```bash
mkdir -p ~/isaac_ws
cd ~/isaac_ws
```

### 2. Clone Isaac Lab

```bash
git clone https://github.com/isaac-sim/IsaacLab.git
cd IsaacLab
git checkout v2.3.2
```

If `v2.3.2` is not available as a tag in the checkout, use the exact release commit for Isaac Lab 2.3.2 and record the commit hash in the environment matrix.

### 3. Create Python 3.11 Environment

```bash
conda create -n isaaclab python=3.11 -y
conda activate isaaclab

python -m pip install --upgrade pip
```

### 4. Install Isaac Sim 5.1.0

```bash
python -m pip install "isaacsim[all,extscache]==5.1.0" --extra-index-url https://pypi.nvidia.com
```

### 5. Install PyTorch 2.7.0 CUDA 12.8

```bash
python -m pip install -U torch==2.7.0 torchvision==0.22.0 --index-url https://download.pytorch.org/whl/cu128
```

### 6. Install Isaac Lab With RSL-RL

From the IsaacLab checkout:

```bash
cd ~/isaac_ws/IsaacLab
./isaaclab.sh --install rsl_rl
```

The Isaac Lab installer supports installing learning-framework extras through `isaaclab.sh`; `rsl_rl` is the expected backend for this project.

### 7. Clone This External Project

```bash
cd ~/isaac_ws
git clone <PROJECT_REPO_URL> isaaclab-quadruped-robust-locomotion
cd isaaclab-quadruped-robust-locomotion
```

Set useful paths:

```bash
export ISAACLAB_PATH="$HOME/isaac_ws/IsaacLab"
export PROJECT_ROOT="$HOME/isaac_ws/isaaclab-quadruped-robust-locomotion"
export RESULTS_DIR="$PROJECT_ROOT/results"
```

Install the external project editable if it has Python package metadata:

```bash
cd "$PROJECT_ROOT"
python -m pip install -e .
```

If package metadata has not been added yet, skip editable install and use this document as the target command flow for the scaffold milestone.

## Validation Commands

Run these on the rented GPU machine, not on the local GTX 1060.

### Import Checks

```bash
conda activate isaaclab

python - <<'PY'
import torch

print("torch:", torch.__version__)
print("cuda available:", torch.cuda.is_available())
print("cuda version:", torch.version.cuda)
PY
```

```bash
python - <<'PY'
import isaacsim  # noqa: F401
import isaaclab  # noqa: F401
from pxr import Usd  # noqa: F401

print("Isaac Sim, Isaac Lab, and pxr imports OK")
PY
```

### List Isaac Lab Environments

```bash
cd "$ISAACLAB_PATH"
./isaaclab.sh -p scripts/environments/list_envs.py
```

Use this output to choose the exact built-in task ID. Candidate quadruped tasks may include ANYmal or Unitree Go2 variants depending on the installed Isaac Lab release.

### Empty Scene Smoke Test

```bash
cd "$ISAACLAB_PATH"
./isaaclab.sh -p scripts/tutorials/00_sim/create_empty.py --headless
```

This validates that Isaac Sim can launch through Isaac Lab in headless mode.

### Short RSL-RL Training Run

First choose a task ID from `list_envs.py`:

```bash
export TASK_ID=<BUILT_IN_QUADRUPED_TASK_ID>
```

Example shape:

```bash
cd "$ISAACLAB_PATH"
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task "$TASK_ID" \
  --num_envs 128 \
  --max_iterations 10 \
  --headless
```

Use a small `--num_envs` and `--max_iterations` for smoke testing. Increase them only after the task launches and logs correctly.

### Play Or Record A Policy

After training produces a checkpoint, run a play command:

```bash
cd "$ISAACLAB_PATH"
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
  --task "$TASK_ID" \
  --num_envs 16 \
  --checkpoint <CHECKPOINT_PATH> \
  --headless
```

If the installed play script supports video flags, record a short rollout:

```bash
cd "$ISAACLAB_PATH"
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
  --task "$TASK_ID" \
  --num_envs 16 \
  --checkpoint <CHECKPOINT_PATH> \
  --headless \
  --video \
  --video_length 400 \
  --video_interval 1
```

Record the exact command, checkpoint path, task ID, seed, and output video path for each portfolio artifact.

## Troubleshooting

### Disk Full

Isaac Sim packages, caches, logs, checkpoints, videos, and terrain assets can consume disk quickly.

Actions:

- Prefer 500 GB disk for rented machines.
- Keep `RESULTS_DIR` on the largest available volume.
- Delete failed smoke logs and partial downloads after recording the error.
- Move completed videos and metrics off the rental machine when no longer needed.

### Missing `isaaclab` Module

Likely causes:

- The wrong conda environment is active.
- `./isaaclab.sh --install rsl_rl` was not run.
- Commands are using system Python instead of the Isaac Lab environment.

Checks:

```bash
which python
python -c "import sys; print(sys.executable)"
cd "$ISAACLAB_PATH" && ./isaaclab.sh -p -c "import isaaclab; print('ok')"
```

### Missing `pxr` Module

Likely causes:

- Isaac Sim pip packages are not installed in the active environment.
- The command is not being run through the Isaac Lab Python wrapper.
- Package versions are inconsistent.

Checks:

```bash
python -c "import isaacsim; from pxr import Usd; print('pxr ok')"
cd "$ISAACLAB_PATH" && ./isaaclab.sh -p scripts/tutorials/00_sim/create_empty.py --headless
```

### Unsupported Local GPU

The local GTX 1060 is not a project runtime target. Do not use local failure to launch Isaac Sim as evidence that the project install is broken. Use the rented RTX 4090/L40/L40S-class machine for simulator validation.

### Package Version Mismatch

Symptoms include import errors, extension load failures, CUDA errors, missing tasks, or RSL-RL script failures.

Actions:

- Confirm the active environment.
- Print versions before training.
- Reinstall PyTorch using the CUDA 12.8 wheel index.
- Confirm Isaac Sim is `5.1.0`.
- Confirm Isaac Lab checkout is `v2.3.2` or the recorded equivalent commit.
- Re-run the empty scene smoke test before attempting training.

Version capture:

```bash
python - <<'PY'
import platform
import torch

print("os:", platform.platform())
print("python:", platform.python_version())
print("torch:", torch.__version__)
print("cuda:", torch.version.cuda)
print("cuda available:", torch.cuda.is_available())
PY

nvidia-smi
git -C "$ISAACLAB_PATH" rev-parse HEAD
git -C "$PROJECT_ROOT" rev-parse HEAD
```

## References

- Isaac Lab installation docs: https://isaac-sim.github.io/IsaacLab/main/source/setup/installation/isaaclab_pip_installation.html
- Isaac Lab source install docs: https://isaac-sim.github.io/IsaacLab/v2.3.0/source/setup/installation/source_installation.html
- Isaac Sim 5.1.0 installation docs: https://docs.isaacsim.omniverse.nvidia.com/5.1.0/installation/index.html
