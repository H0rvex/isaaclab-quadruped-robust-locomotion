# Environment

This project is designed as an external Isaac Lab project. Local development should stay lightweight and simulator-free; Isaac Sim execution, environment registration, training, evaluation, and video capture are intended for a rented GPU machine.

## Target Runtime Stack

Full simulator work targets:

- Isaac Lab v2.3.2
- Isaac Sim 5.1.0
- Python 3.11
- PyTorch 2.7.0 with CUDA 12.8
- RSL-RL
- Ubuntu 22.04 or Ubuntu 24.04

The target stack should be validated on the rented GPU machine before long training runs. Record exact versions in the run metadata or environment matrix for every result-producing session.

## Local Development Stack

Local development targets Python 3.11 and pure-Python tooling:

- `pytest`
- `ruff`
- `black`
- `pyyaml`
- `numpy`
- `pandas`
- `matplotlib`
- `rich`
- `tqdm`

Isaac Sim is not required locally. Local commands should cover repository hygiene, config parsing, plotting utilities, result aggregation, documentation checks, and tests that do not need simulator imports.

## Hardware Assumptions

Local machine:

- GTX 1060-class GPU is for coding only.
- Do not rely on the local machine for Isaac Sim launch, training, environment registration tests, or rollout video recording.

Rented GPU machine:

- Use an RTX 4090, L40, L40S, or similar NVIDIA GPU for simulator execution and training.
- Minimum disk: 200 GB.
- Preferred disk: 500 GB, especially when saving Isaac Sim caches, checkpoints, videos, logs, and multiple training runs.

## Environment Variables

Recommended variables:

```bash
export ISAACLAB_PATH=/path/to/IsaacLab
export PROJECT_ROOT=/path/to/isaaclab-quadruped-robust-locomotion
export RESULTS_DIR="$PROJECT_ROOT/results"
```

Expected usage:

- `ISAACLAB_PATH`: location of the upstream IsaacLab checkout or installation.
- `PROJECT_ROOT`: this external project repository.
- `RESULTS_DIR`: root directory for metrics, checkpoints, videos, plots, and aggregated evaluation artifacts.

Do not hard-code user-specific absolute paths in committed configs or scripts. Prefer these variables or command-line arguments.

## Version-Pinning Policy

Pin versions where reproducibility depends on them:

- Isaac Lab and Isaac Sim versions are fixed for the main project target.
- Python major/minor version should remain Python 3.11.
- PyTorch/CUDA versions should match the target runtime unless the rented GPU provider requires a documented adjustment.
- RSL-RL version or commit should be recorded for all training runs.

Local pure-Python tooling can be less strict, but result-producing runs should record:

- OS version
- NVIDIA driver version
- CUDA version
- Python version
- PyTorch version
- Isaac Sim version
- Isaac Lab version
- RSL-RL version or commit
- GPU model

If a version differs from the target stack, document the reason and whether it affects comparability.

## Local Vs Rented GPU Execution

Can run locally:

- Markdown and documentation edits.
- Config file parsing and validation.
- Pure-Python unit tests.
- Result aggregation from existing CSV/JSON artifacts.
- Plot generation from existing metrics files.
- Lightweight scripts that do not import Isaac Lab, Isaac Sim, Omniverse, or Pixar modules.

Requires rented GPU:

- Isaac Sim launch.
- Isaac Lab app smoke tests.
- Environment registration tests.
- Built-in Isaac Lab task training.
- Custom task stepping or training.
- RSL-RL simulator training.
- Rollout video recording.
- Domain-randomization and perturbation evaluation sweeps.

## Import Boundaries For Tests

Pure tests must not import:

- `isaaclab`
- `isaacsim`
- `omni`
- `pxr`

Keep simulator imports inside GPU-only entrypoints or functions that are called only after the Isaac Lab app is launched. Avoid top-level imports of simulator packages in modules that local tests need to import.

Preferred pattern:

```python
def launch_simulator_entrypoint() -> None:
    from isaaclab.app import AppLauncher

    # Simulator-dependent code starts here.
```

Avoid this pattern in modules used by local tests:

```python
from isaaclab.app import AppLauncher
from pxr import Usd
```

Local tests should target pure utilities such as config loading, schema checks, command construction, result parsing, table generation, and plotting from saved metrics.

## Reproducibility Notes

Every result-producing run should preserve enough context to be audited later.

Required run metadata:

- Random seed or seed list.
- Config file path and committed config content.
- Training command.
- Evaluation command.
- Checkpoint path.
- Evaluation episode count.
- Evaluation seed.
- Runtime stack versions.

Expected artifacts:

- Training metrics, preferably CSV or JSON.
- Evaluation JSON with mean, standard deviation, episode lengths, termination/fall data where available, and per-episode returns.
- Video artifacts or GIFs for representative nominal, rough-terrain, robust, and failure rollouts.
- Result summary tables derived from raw metrics, not typed manually without source files.
- Plots for training curves and robustness sweeps.

Use fixed evaluation seeds for comparable tables. When multiple training seeds are used, report both seed-level results and aggregate statistics.

## Practical Rule

Local code should prepare, validate, parse, and present experiments. The rented GPU machine should execute Isaac Lab. If a local test fails because Isaac Sim is missing, the test boundary is wrong.
