# Roadmap: Isaac Lab Quadruped Robust Locomotion

## Project Thesis

This repository is a portfolio-grade robotics project focused on robust quadruped locomotion in Isaac Lab. The core goal is to train and evaluate PPO policies for legged locomotion under terrain variation, dynamics variation, and external perturbations, then present the result with reproducible commands, videos, curves, tables, and failure analysis.

The project should demonstrate practical robotics engineering judgement rather than only high reward. A complete result should answer:

- Can a quadruped policy learn stable locomotion on flat and rough terrain in Isaac Lab?
- How does performance change under terrain difficulty, randomized physics, and push perturbations?
- Which configurations improve robustness, and where does the policy still fail?
- Are the training and evaluation artifacts reproducible from a clean environment?

The preferred robot is Unitree Go2 if Isaac Lab v2.3.2 supports it cleanly through built-in assets and tasks. If Go2 support creates avoidable compatibility risk, the baseline should use a built-in ANYmal task first, then optionally return to Go2 once the runtime stack is stable.

## Why This Follows The MuJoCo PPO Project

The previous project built continuous-control locomotion with PPO from scratch in MuJoCo. That work established the fundamentals: rollout collection, advantage estimation, PPO updates, observation normalization, checkpointing, deterministic evaluation, curves, videos, and artifact-backed reporting.

This project should deliberately move one layer up the robotics stack:

- Use a production robotics simulator instead of MuJoCo Gym tasks.
- Use RSL-RL PPO instead of reimplementing PPO again.
- Focus engineering effort on environment configuration, terrain curriculum, domain randomization, perturbation evaluation, and evidence quality.
- Treat robustness, reproducibility, and failure modes as first-class results.

The portfolio story is therefore not "PPO again." It is "from implementing PPO mechanics to using an Isaac Lab robotics stack to evaluate robust locomotion."

## Target Runtime Stack

Full simulator work targets:

- Isaac Lab v2.3.2
- Isaac Sim 5.1.0
- Python 3.11
- PyTorch 2.7.0 with CUDA 12.8
- RSL-RL
- Ubuntu 22.04 or 24.04
- NVIDIA GPU rental machine with enough VRAM for Isaac Sim training

This repository should be structured as an external Isaac Lab project. It should not fork, vendor, or modify the upstream IsaacLab repository.

## Local-Vs-Rental Workflow

Local development has a hard boundary: this machine cannot reliably run Isaac Sim. Local work should avoid importing `isaaclab`, `isaacsim`, `omni`, or `pxr` at module import time. Any file that needs those packages should use lazy imports inside simulator-only entrypoints, and local tests should exercise only pure Python logic, config validation, documentation checks, and artifact parsing.

Local machine responsibilities:

- Maintain repository structure, documentation, and roadmap.
- Write external-project scaffold files without requiring Isaac imports during normal local checks.
- Prepare config files, command templates, result schemas, and aggregation scripts.
- Validate YAML/TOML/Markdown formatting where possible.
- Validate result parsing and plotting code against small synthetic fixtures.
- Keep generated artifacts out of source control unless they are intended portfolio assets.

Rented GPU responsibilities:

- Install and verify Isaac Sim, Isaac Lab, RSL-RL, CUDA, and PyTorch.
- Run Isaac Lab app smoke tests.
- Verify built-in task training and environment registration.
- Train flat and rough-terrain baselines.
- Run custom external-project tasks.
- Record rollout videos and generate evaluation data.
- Run perturbation and robustness sweeps.

The practical workflow is:

1. Prepare code and configs locally without simulator imports.
2. Push or copy the repo to the GPU machine.
3. Run install and smoke commands on the GPU machine.
4. Train and evaluate on the GPU machine.
5. Pull back metrics, videos, plots, and logs.
6. Aggregate and document results locally.

## Milestones

### M0: Local Repo Scaffold And Docs

Purpose: create a clean external-project foundation that can be developed locally without Isaac Sim.

Deliverables:

- Top-level `README.md` with project scope, stack, and workflow.
- `ROADMAP.md` with milestone plan and definition of done.
- External-project style directory layout for source, configs, scripts, docs, and assets.
- `.gitignore` rules for checkpoints, logs, caches, simulator outputs, and large training runs.
- Local-only validation commands that do not import `isaaclab`, `isaacsim`, `omni`, or `pxr`.
- Initial environment/version matrix template.
- GPU machine setup checklist.

Exit criteria:

- A fresh local checkout can run the local checks without Isaac Sim installed.
- Documentation clearly separates local development from GPU simulator execution.
- No upstream IsaacLab files are copied into or modified by this repo.

### M1: Rented GPU Install And Isaac Lab Smoke Test

Purpose: prove the target runtime stack works before writing project-specific training code.

Deliverables:

- GPU setup notes for Ubuntu, driver, CUDA compatibility, Isaac Sim, Isaac Lab, PyTorch, and RSL-RL.
- Captured version matrix for Isaac Lab, Isaac Sim, Python, PyTorch, CUDA, driver, OS, and GPU model.
- Isaac Lab app launch smoke test.
- Built-in environment listing or task-discovery output.
- Minimal RSL-RL training smoke run using a built-in Isaac Lab task.
- Install failure log if setup is not clean on the first attempt.

Exit criteria:

- Isaac Lab v2.3.2 launches on the rented GPU machine.
- A built-in task can step or train briefly without runtime import or asset errors.
- The exact install commands and versions are recorded.

### M2: Built-In Go2/ANYmal Flat Baseline

Purpose: establish a known-good quadruped locomotion baseline before adding custom configuration.

Deliverables:

- Selection note: Go2 if cleanly supported, otherwise ANYmal as the stable baseline.
- Built-in flat-terrain PPO/RSL-RL training command.
- Training curves for episode return, episode length, losses, and relevant RSL-RL diagnostics.
- Checkpoint selection rule, such as best evaluation checkpoint or final checkpoint.
- Deterministic evaluation command with fixed seed and episode count.
- Flat-terrain rollout video or GIF.
- Baseline result table with mean return, standard deviation, episode length, success/fall rate if available, checkpoint path, seed, and command.

Exit criteria:

- A built-in quadruped policy trains to stable forward locomotion on flat terrain.
- The result can be reproduced from documented commands.
- The baseline is documented honestly, including any falls, instability, or seed sensitivity.

### M3: Built-In Rough-Terrain Baseline

Purpose: establish the built-in rough-terrain reference before introducing custom terrain or randomization.

Deliverables:

- Built-in rough-terrain task command.
- Training curves and evaluation summary.
- Rollout video showing representative rough-terrain behavior.
- Comparison table against the flat baseline.
- Notes on terrain settings, curriculum if built in, and observed failure modes.

Exit criteria:

- A built-in rough-terrain policy completes a meaningful training run.
- The README can show a direct flat-vs-rough comparison.
- Any degradation from flat terrain is quantified rather than described qualitatively only.

### M4: Custom External-Project Task/Config Scaffold

Purpose: move from built-in examples to a clean project-owned task and configuration layer without modifying IsaacLab upstream.

Deliverables:

- External-project package scaffold for custom task/config registration.
- Simulator-only entrypoints with lazy Isaac imports.
- Config files for robot selection, terrain, rewards, observations, commands, randomization, and training.
- CLI scripts or documented commands for training, evaluation, and video recording.
- Minimal registration smoke test on the GPU machine.
- Local tests for pure config/result utilities that do not import Isaac packages.

Exit criteria:

- The custom task can be discovered and launched from the external project on the GPU machine.
- Local import of the repository remains safe without Isaac Sim installed.
- The custom task reproduces behavior close to the built-in baseline before additional complexity is added.

### M5: Domain Randomization Config

Purpose: add explicit dynamics and disturbance variation for robustness.

Deliverables:

- Configurable randomization ranges for at least:
  - Ground friction.
  - Body mass or payload.
  - Actuator strength or motor scaling.
  - Joint damping or stiffness if supported cleanly.
  - Observation noise.
  - External pushes or velocity perturbations.
- Randomization schedule documented by train phase.
- Ablation-ready configs: no randomization, moderate randomization, and stronger randomization.
- Training runs for at least baseline and moderate randomization.
- Evaluation table on nominal conditions and randomized conditions.

Exit criteria:

- Randomization is controlled by config, not hard-coded in scripts.
- The README can explain what was randomized and why.
- At least one randomization setting is trained and evaluated against the non-randomized baseline.

### M6: Terrain/Randomization Curriculum

Purpose: make training progression explicit instead of relying on one fixed hard setting.

Deliverables:

- Terrain curriculum config that increases terrain difficulty over training.
- Optional randomization curriculum that widens dynamics ranges over training.
- Curves showing curriculum progress where Isaac Lab exposes this signal.
- Comparison against non-curriculum rough terrain or fixed-randomization training.
- Notes on stability, reward progression, and failure patterns during curriculum changes.

Exit criteria:

- Curriculum behavior is reproducible from config.
- The project can show whether curriculum improved robustness, learning speed, or final performance.
- Any negative result is preserved and explained rather than hidden.

### M7: Robustness Evaluation Sweep

Purpose: evaluate trained policies across controlled perturbation axes rather than relying on one rollout video.

Deliverables:

- Evaluation sweep script or command set for:
  - Terrain difficulty levels.
  - Friction levels.
  - Payload or mass variation.
  - Actuator strength scaling.
  - Push magnitude or push frequency.
  - Optional command velocity ranges.
- CSV or JSON result files with one row per policy, seed, perturbation setting, and evaluation seed.
- Aggregated robustness tables.
- Failure metrics such as fall rate, early termination rate, mean distance, episode length, or recovery rate where available.
- Representative videos for nominal behavior, robust behavior, and failure cases.

Exit criteria:

- Robustness claims are based on sweep tables, not single videos.
- The evaluation protocol is documented with fixed seeds and episode counts.
- The strongest policy and its known weaknesses are both identifiable from the data.

### M8: Result Aggregation, Videos, Plots, README Finalization

Purpose: turn raw runs into a complete portfolio presentation.

Deliverables:

- Final README with:
  - Project thesis.
  - Runtime stack and version matrix.
  - Reproducible setup, train, evaluate, and video commands.
  - Representative videos/GIFs.
  - Training curves.
  - Flat-vs-rough results.
  - Randomization and curriculum ablations.
  - Robustness sweep tables.
  - Failure analysis.
  - Limitations and non-goals.
- Result aggregation script for raw metrics.
- Plotting script for training and evaluation curves.
- Curated asset directory for portfolio visuals.
- Clear mapping from table values to source files.
- Final artifact checklist.

Exit criteria:

- A reviewer can understand the project from the README without reading every script.
- Every headline metric points back to a source artifact.
- Videos and plots are embedded or linked in a way that survives a clean checkout.
- Placeholder language is removed once real results exist.

### M9: Optional Extension: Policy Export Or Sim-To-Real Discussion

Purpose: add a bounded extension only after the core result is complete.

Deliverables:

- Optional policy export path if RSL-RL and Isaac Lab support it cleanly.
- Export verification command where possible.
- Short discussion of sim-to-real requirements, including hardware, calibration, safety, control frequency, observation matching, latency, and deployment risk.
- Clear statement that this project does not claim hardware transfer unless hardware validation is actually performed.

Exit criteria:

- The extension does not destabilize the completed training and evaluation story.
- Sim-to-real language is honest and bounded by evidence.

## Definition Of Done

The project is done when the repository contains a reproducible, artifact-backed Isaac Lab robust locomotion study. Specifically:

- The repo uses external Isaac Lab project structure and does not modify upstream IsaacLab.
- Local development remains possible without importing Isaac Sim or Isaac Lab packages.
- The GPU machine environment is documented with an exact version matrix.
- At least one built-in quadruped baseline is trained and evaluated.
- At least one rough-terrain baseline is trained and evaluated.
- A custom external-project task/config scaffold runs on the GPU machine.
- Domain randomization is configurable and evaluated.
- Terrain and/or randomization curriculum is tested.
- Robustness sweeps are run across multiple perturbation axes.
- Results include curves, rollout videos/GIFs, tables, configs, commands, and failure analysis.
- README claims are backed by source artifacts in the repo or documented run directories.
- Limitations are explicit, especially around lack of hardware transfer.

## Non-Goals

- Do not write PPO from scratch again. RSL-RL is the training backend for this project.
- Do not build a simulator. Isaac Sim and Isaac Lab provide the simulation stack.
- Do not claim sim-to-real transfer without real hardware validation.
- Do not depend on the local GTX 1060 for training, video recording, or simulator validation.
- Do not fork, vendor, or patch upstream IsaacLab as part of normal project development.
- Do not treat a single successful rollout video as sufficient robustness evidence.

## Risks And Mitigations

### Isaac Lab Install Instability

Risk: Isaac Sim and Isaac Lab installation may fail because of driver, CUDA, Python, or package conflicts.

Mitigations:

- Validate the full stack in M1 before building custom tasks.
- Record exact versions and commands.
- Keep a clean setup log and failure notes.
- Prefer documented Isaac Lab install paths over ad hoc environment changes.

### Version Mismatch

Risk: Isaac Lab v2.3.2, Isaac Sim 5.1.0, PyTorch 2.7.0, CUDA 12.8, and RSL-RL may not align exactly on the rented machine.

Mitigations:

- Treat the version matrix as a required artifact.
- Pin versions where practical.
- Run smoke tests before long training jobs.
- Avoid local code that depends on unverified simulator APIs until M1 succeeds.

### GPU Rental Cost

Risk: Debugging install problems or unstable training on rented GPUs can waste budget.

Mitigations:

- Prepare configs, docs, scripts, and result parsers locally first.
- Use short smoke runs before full training.
- Save logs and checkpoints frequently.
- Prefer built-in tasks before custom tasks.
- Stop unstable runs early and record the failure rather than burning time.

### Go2 Task Incompatibility

Risk: Unitree Go2 may not be supported cleanly in the target Isaac Lab version or may require extra assets/configuration.

Mitigations:

- Check built-in Go2 support during M1/M2.
- Use ANYmal as the baseline fallback if Go2 blocks progress.
- Keep the robot-selection decision documented.
- Do not let Go2-specific issues block the robustness study.

### Poor Training Stability

Risk: Policies may fail to learn or may overfit to narrow terrain/randomization settings.

Mitigations:

- Start from built-in stable configs.
- Change one axis at a time: terrain, randomization, curriculum, then perturbation evaluation.
- Use multiple seeds when budget allows.
- Track episode length, termination causes, and failure videos, not only return.
- Preserve negative or mixed results as part of failure analysis.

## Expected Final Portfolio Artifacts

The final repository should include or reference:

- Training curves for flat, rough, randomized, and curriculum runs.
- Evaluation curves or summaries for checkpoint selection.
- Rollout videos/GIFs for nominal locomotion, rough terrain, robust behavior, and failure cases.
- Robustness sweep tables across terrain, friction, payload, actuator scaling, and push perturbations.
- Config files for each major experiment.
- Reproducible commands for setup, training, evaluation, video recording, plotting, and aggregation.
- Failure analysis with specific observed behaviors and likely causes.
- Environment/version matrix for Isaac Lab, Isaac Sim, Python, PyTorch, CUDA, driver, OS, GPU, and RSL-RL.
- Source artifact mapping from README metrics to raw CSV/JSON/log files.

## Operating Principle

The project should prefer a smaller number of well-documented, reproducible experiments over many loosely tracked runs. The final portfolio value comes from a clean robotics workflow, credible robustness evaluation, and honest reporting of both successes and failures.
