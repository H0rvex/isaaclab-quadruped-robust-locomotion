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

if [[ -z "${CHECKPOINT_PATH:-}" ]]; then
  echo "ERROR: CHECKPOINT_PATH is unset. Set it to an RSL-RL checkpoint path." >&2
  exit 2
fi

PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
RESULTS_DIR="${RESULTS_DIR:-${PROJECT_ROOT}/results}"
TASK_ID="${TASK_ID:-Isaac-Velocity-Rough-Unitree-Go2-v0}"
NUM_ENVS="${NUM_ENVS:-16}"
VIDEO_LENGTH="${VIDEO_LENGTH:-400}"
VIDEO_INTERVAL="${VIDEO_INTERVAL:-1}"

mkdir -p "${RESULTS_DIR}/videos"

cd "${ISAACLAB_PATH}"
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
  --task "${TASK_ID}" \
  --num_envs "${NUM_ENVS}" \
  --checkpoint "${CHECKPOINT_PATH}" \
  --headless \
  --video \
  --video_length "${VIDEO_LENGTH}" \
  --video_interval "${VIDEO_INTERVAL}" \
  "$@"
