from pathlib import Path

import yaml

EXPECTED_CONFIGS = [
    "go2_flat_baseline.yaml",
    "go2_rough_baseline.yaml",
    "go2_rough_dr.yaml",
    "go2_rough_dr_curriculum.yaml",
    "robustness_sweep.yaml",
]


def test_expected_configs_exist_and_load() -> None:
    config_root = Path("configs")
    for filename in EXPECTED_CONFIGS:
        path = config_root / filename
        assert path.exists(), filename
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(data, dict), filename
        assert "experiment" in data, filename


def test_training_configs_have_runtime_and_artifact_contract() -> None:
    for path in Path("configs").glob("go2_*.yaml"):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert data["runtime"]["isaac_lab"] == "2.3.2"
        assert data["runtime"]["isaac_sim"] == "5.1.0"
        assert data["runtime"]["python"] == "3.11"
        assert data["runtime"]["backend"] == "rsl_rl"
        assert data["artifacts"]["results_dir"] == "results"
        assert data["evaluation"]["seed"] == 1000


def test_runtime_shell_scripts_require_isaaclab_path() -> None:
    local_only_scripts = {Path("scripts/validate_export.sh")}
    for path in Path("scripts").glob("*.sh"):
        if path in local_only_scripts:
            continue
        text = path.read_text(encoding="utf-8")
        assert "ISAACLAB_PATH" in text, path
        assert "is unset" in text, path
