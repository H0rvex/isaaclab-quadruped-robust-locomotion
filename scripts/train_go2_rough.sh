#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${ISAACLAB_PATH:-}" ]]; then
  echo "ERROR: ISAACLAB_PATH is unset. Set it to the IsaacLab checkout path." >&2
  exit 2
fi

if [[ ! -x "${ISAACLAB_PATH}/isaaclab.sh" ]]; then
  echo "ERROR: ${ISAACLAB_PATH}/isaaclab.sh is missing or not executable." >&2
  exit 2
fi

PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
RESULTS_DIR="${RESULTS_DIR:-${PROJECT_ROOT}/results}"
CONFIG_PATH="${CONFIG_PATH:-${PROJECT_ROOT}/configs/go2_rough_baseline.yaml}"
TASK_ID="${TASK_ID:-Isaac-Velocity-Rough-Unitree-Go2-v0}"
NUM_ENVS="${NUM_ENVS:-4096}"
MAX_ITERATIONS="${MAX_ITERATIONS:-2500}"
SEED="${SEED:-1}"

mkdir -p "${RESULTS_DIR}"

echo "Project root: ${PROJECT_ROOT}"
echo "Results dir: ${RESULTS_DIR}"
echo "Config: ${CONFIG_PATH}"
echo "Task: ${TASK_ID}"

cd "${ISAACLAB_PATH}"
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task "${TASK_ID}" \
  --num_envs "${NUM_ENVS}" \
  --seed "${SEED}" \
  --max_iterations "${MAX_ITERATIONS}" \
  --headless \
  "$@"
