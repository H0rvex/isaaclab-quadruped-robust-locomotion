# Experiment Plan

## Purpose

Train and evaluate robust quadruped locomotion policies in Isaac Lab using RSL-RL PPO. The study should progress from built-in flat locomotion to rough terrain, domain randomization, curriculum, and robustness sweeps.

## Experiment Ladder

1. Go2 flat baseline if supported cleanly.
2. Go2 rough-terrain baseline.
3. Go2 rough terrain with domain randomization.
4. Go2 rough terrain with domain randomization and curriculum.
5. Robustness sweeps over terrain, friction, payload, actuator scaling, and pushes.

If Go2 is blocked by Isaac Lab v2.3.2 compatibility, use a built-in ANYmal task as the temporary baseline and document the fallback.

## Required Evidence

- Exact train command.
- Exact config file.
- Runtime version matrix.
- Checkpoint path.
- Evaluation JSON.
- Training curves.
- Rollout video or GIF.
- Result summary table.
- Failure notes.

## Seed Policy

Use seed `1` for first smoke and baseline runs. Add seeds `2` and `3` for final comparison runs when GPU budget allows. Use fixed evaluation seed `1000` for deterministic tables unless a config explicitly defines a sweep seed list.

## Completion Criteria

An experiment is complete only when it has metrics, config, command, checkpoint reference, evaluation JSON, and a short written interpretation. A single rollout video is not sufficient evidence.
