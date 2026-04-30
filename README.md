# Isaac Lab Quadruped Robust Locomotion

Isaac Lab project for robust quadruped locomotion with PPO/RSL-RL. The project follows a completed from-scratch MuJoCo PPO locomotion project and shifts the focus from implementing PPO mechanics to building a reproducible Isaac Lab robotics workflow.

## Current Status

Local scaffold is complete:

- Source-layout Python package: `source/isaaclab_quadruped`.
- Pure local utilities for result IO, table generation, plotting, and experiment schemas.
- Local configs, reports, install docs, and roadmap.
- GPU-facing shell scripts for Isaac Lab setup, validation, training, playback, and video recording.
- Pure tests pass locally without Isaac Sim.

Isaac Sim is not required locally. Simulator execution, environment registration, RSL-RL training, and video recording are rented-GPU tasks.

## Runtime Targets

- Isaac Lab v2.3.2
- Isaac Sim 5.1.0
- Python 3.11
- PyTorch 2.7.0 with CUDA 12.8
- RSL-RL
- Ubuntu 22.04 or 24.04
- RTX 4090/L40/L40S-class rented GPU

The local GTX 1060 is for coding only and is not a supported training/runtime target.

## Repository Structure

```text
.
|-- configs/
|   |-- go2_flat_baseline.yaml
|   |-- go2_rough_baseline.yaml
|   |-- go2_rough_dr.yaml
|   |-- go2_rough_dr_curriculum.yaml
|   |-- robustness_sweep.yaml
|   `-- version_matrix.md
|-- reports/
|   |-- domain_randomization_plan.md
|   |-- evaluation_protocol.md
|   |-- experiment_plan.md
|   |-- failure_analysis.md
|   |-- rental_gpu_log.md
|   `-- rented_gpu_validation_checklist.md
|-- results/
|   |-- eval/
|   |   `-- placeholder_go2_flat_eval.json
|   `-- tables/
|-- scripts/
|   |-- list_envs.sh
|   |-- play_policy.sh
|   |-- record_video.sh
|   |-- setup_runtime_isaaclab.sh
|   |-- smoke_test_isaaclab.sh
|   |-- summarize_results.py
|   |-- train_go2_flat.sh
|   |-- train_go2_rough.sh
|   |-- train_go2_rough_dr.sh
|   `-- validate_runtime_isaaclab.sh
|-- source/
|   `-- isaaclab_quadruped/
`-- tests/
    |-- pure/
    `-- sim/
```

## Local Workflow

Create a local Python 3.11 environment and install the pure development stack:

```bash
python -m pip install -e ".[dev]"
```

Run local validation:

```bash
python -m pytest tests -q
python -m ruff check source scripts tests
python -m ruff format --check source scripts tests
```

Pure utilities must not import `isaaclab`, `isaacsim`, `omni`, or `pxr`. Simulation tests under `tests/sim` are skipped unless `RUN_SIM_TESTS=1`.

Generate summary tables from evaluation JSON files:

```bash
python scripts/summarize_results.py \
  --eval-dir results/eval \
  --out-dir results/tables
```

This writes:

- `results/tables/summary.csv`
- `results/tables/summary.md`

## Validation

Validation is split into local checks and rented-GPU checks. Local validation proves the repository scaffold, pure utilities, configs, reports, and result aggregation work without Isaac Sim. Rented-GPU validation proves the Isaac Lab runtime can actually launch, discover tasks, and run simulator smoke tests.

### Local Validation

Run these on the development machine:

```bash
python -m pytest tests -q
python -m ruff check source scripts tests
python -m ruff format --check source scripts tests
python scripts/summarize_results.py \
  --eval-dir results/eval \
  --out-dir results/tables
```

Expected local result:

- Pure tests pass.
- `tests/sim` is skipped by default.
- Ruff lint and format checks pass.
- `results/tables/summary.csv` and `results/tables/summary.md` are generated from `results/eval/placeholder_go2_flat_eval.json`.

The local checks must not require `isaaclab`, `isaacsim`, `omni`, or `pxr`.

### Rented-GPU Runtime Validation

Run these only on the rented GPU machine after setting paths:

```bash
export ISAACLAB_PATH=/path/to/IsaacLab
export PROJECT_ROOT=/path/to/isaaclab-quadruped-robust-locomotion
export RESULTS_DIR="$PROJECT_ROOT/results"

cd "$PROJECT_ROOT"
bash scripts/setup_runtime_isaaclab.sh
bash scripts/validate_runtime_isaaclab.sh
```

`scripts/validate_runtime_isaaclab.sh` checks:

- `ISAACLAB_PATH` is set and contains executable `isaaclab.sh`.
- `nvidia-smi` is available.
- PyTorch sees CUDA.
- `isaacsim`, `isaaclab`, and `pxr` import through Isaac Lab's Python wrapper.
- Isaac Lab can list registered environments.
- Go2, Unitree, or ANYmal candidate environments appear in the environment list.
- `scripts/tutorials/00_sim/create_empty.py --headless` runs successfully.

Optional simulator pytest gate:

```bash
RUN_SIM_TESTS=1 ISAACLAB_PATH="$ISAACLAB_PATH" python -m pytest tests/sim -q
```

Expected rented-GPU result:

- Runtime validation completes without import, CUDA, or app-launch errors.
- Go2 is selected if available cleanly.
- ANYmal is selected as the fallback if Go2 is unavailable or unstable.
- Any failure is recorded in `reports/rental_gpu_log.md` before spending more GPU time.

## Rented GPU Workflow

Set paths on the rented GPU machine:

```bash
export ISAACLAB_PATH=/path/to/IsaacLab
export PROJECT_ROOT=/path/to/isaaclab-quadruped-robust-locomotion
export RESULTS_DIR="$PROJECT_ROOT/results"
```

Install the runtime stack:

```bash
cd "$PROJECT_ROOT"
bash scripts/setup_runtime_isaaclab.sh
```

Validate Isaac Lab using the commands in the validation section above.

Training scripts use `ISAACLAB_PATH` and fail early if it is unset:

```bash
bash scripts/list_envs.sh
TASK_ID=<GO2_OR_ANYMAL_TASK_ID> bash scripts/train_go2_flat.sh
TASK_ID=<GO2_OR_ANYMAL_TASK_ID> bash scripts/train_go2_rough.sh
TASK_ID=<GO2_OR_ANYMAL_TASK_ID> bash scripts/train_go2_rough_dr.sh
```

## Planned Experiment Ladder

1. Validate Isaac Lab v2.3.2 and Isaac Sim 5.1.0 on rented GPU.
2. Train built-in Go2 flat-terrain baseline, or ANYmal fallback if Go2 is not cleanly available.
3. Train built-in Go2 rough-terrain baseline.
4. Add external-project task/config scaffold.
5. Add domain randomization for friction, mass/payload, actuator scaling, observation noise, and pushes.
6. Add terrain and randomization curriculum.
7. Run robustness sweeps over terrain, friction, payload, actuator strength, and push perturbations.
8. Aggregate results into curves, videos/GIFs, tables, and failure analysis.

## Reporting Standard

Final claims should be backed by artifacts:

- Training curves.
- Evaluation JSON files.
- Summary tables.
- Config files.
- Rollout videos or GIFs.
- Failure analysis.
- Runtime version matrix.

The project does not claim sim-to-real transfer without hardware validation.
