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

cd "${ISAACLAB_PATH}"
echo "Running Isaac Lab empty-scene smoke test..."
./isaaclab.sh -p scripts/tutorials/00_sim/create_empty.py --headless

echo "Listing registered environments..."
./isaaclab.sh -p scripts/environments/list_envs.py
