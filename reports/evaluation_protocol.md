# Evaluation Protocol

## Default Evaluation

- Use fixed evaluation seed `1000`.
- Use at least 20 episodes for portfolio tables when GPU budget allows.
- Record per-episode return and episode length.
- Record fall or early termination flags when available.
- Evaluate from a documented checkpoint path.

## Robustness Sweeps

Robustness results should vary one axis at a time unless the config explicitly defines a combined stress setting.

Required axes:

- Terrain difficulty.
- Friction.
- Payload or mass.
- Actuator strength.
- Push magnitude or frequency.

## Output Contract

Each evaluation run should write one JSON file under `results/eval/`. The JSON should include:

- `policy`
- `task_id`
- `seed`
- `evaluation_seed`
- `episodes`
- `mean_return`
- `std_return`
- `mean_episode_length`
- `fall_rate`
- `checkpoint_path`
- `terrain`
- `randomization`
- `per_episode_returns`
- `per_episode_lengths`

The local `scripts/summarize_results.py` script aggregates these JSON files into `results/tables/evaluation_summary.csv` and `results/tables/evaluation_summary.md`.
