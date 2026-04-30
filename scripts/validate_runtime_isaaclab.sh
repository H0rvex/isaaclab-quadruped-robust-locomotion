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

echo "Project root: ${PROJECT_ROOT}"
echo "IsaacLab path: ${ISAACLAB_PATH}"
echo "Python: $(python --version)"

if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi
else
  echo "ERROR: nvidia-smi was not found. This validation must run on a GPU machine." >&2
  exit 2
fi

echo "Checking Python runtime imports..."
python - <<'PY'
import torch

print("torch:", torch.__version__)
print("cuda:", torch.version.cuda)
print("cuda available:", torch.cuda.is_available())
if not torch.cuda.is_available():
    raise SystemExit("ERROR: torch.cuda.is_available() is false")
PY

cd "${ISAACLAB_PATH}"

echo "Checking Isaac Sim, Isaac Lab, and pxr imports through isaaclab.sh..."
./isaaclab.sh -p -c \
  "import isaacsim; import isaaclab; from pxr import Usd; print('Isaac Sim, Isaac Lab, and pxr imports OK')"

ENV_LIST_FILE="$(mktemp)"
echo "Listing Isaac Lab environments..."
./isaaclab.sh -p scripts/environments/list_envs.py | tee "${ENV_LIST_FILE}"

echo "Filtering candidate quadruped environments..."
if ! grep -Ei "go2|unitree|anymal" "${ENV_LIST_FILE}"; then
  echo "ERROR: no Go2/Unitree/ANYmal environments found in environment list." >&2
  echo "Keep this log and select a fallback task only after confirming installed tasks." >&2
  exit 3
fi

echo "Running empty-scene headless smoke test..."
./isaaclab.sh -p scripts/tutorials/00_sim/create_empty.py --headless

echo "Isaac Lab runtime validation completed."
