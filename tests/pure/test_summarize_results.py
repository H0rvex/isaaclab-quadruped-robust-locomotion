from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

from isaaclab_quadruped.utils.result_io import write_json


def load_summarize_module() -> ModuleType:
    script_path = Path("scripts/summarize_results.py")
    spec = importlib.util.spec_from_file_location("summarize_results", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_summarize_results_writes_csv_and_markdown(tmp_path) -> None:
    eval_dir = tmp_path / "results" / "eval"
    out_dir = tmp_path / "results" / "tables"
    write_json(
        eval_dir / "go2_flat.json",
        {
            "policy": "go2_flat",
            "task_id": "Isaac-Velocity-Flat-Unitree-Go2-v0",
            "terrain": "flat",
            "randomization": "none",
            "seed": 1,
            "evaluation_seed": 1000,
            "episodes": 2,
            "mean_return": 100.0,
            "std_return": 5.0,
            "mean_episode_length": 200.0,
            "fall_rate": 0.0,
            "checkpoint_path": "runs/go2_flat/model.pt",
            "per_episode_returns": [95.0, 105.0],
            "per_episode_lengths": [200, 200],
        },
    )

    module = load_summarize_module()
    exit_code = module.main(["--eval-dir", str(eval_dir), "--out-dir", str(out_dir)])

    assert exit_code == 0
    csv_path = out_dir / "evaluation_summary.csv"
    markdown_path = out_dir / "evaluation_summary.md"
    assert csv_path.exists()
    assert markdown_path.exists()
    assert "go2_flat" in markdown_path.read_text(encoding="utf-8")
    assert "mean_return" in csv_path.read_text(encoding="utf-8")


def test_summarize_results_can_compute_mean_from_episode_returns(tmp_path) -> None:
    eval_dir = tmp_path / "eval"
    out_dir = tmp_path / "tables"
    write_json(
        eval_dir / "computed.json",
        {
            "policy": "computed",
            "task_id": "task",
            "seed": 2,
            "evaluation_seed": 1000,
            "checkpoint_path": "checkpoint.pt",
            "per_episode_returns": [1.0, 3.0],
            "per_episode_lengths": [10, 20],
        },
    )

    module = load_summarize_module()
    module.summarize(eval_dir, out_dir)

    assert "2.0" in (out_dir / "evaluation_summary.csv").read_text(encoding="utf-8")
