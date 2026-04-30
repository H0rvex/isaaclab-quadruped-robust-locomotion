#!/usr/bin/env bash
set -euo pipefail

ISAACLAB_VERSION="${ISAACLAB_VERSION:-v2.3.2}"
ISAACSIM_VERSION="${ISAACSIM_VERSION:-5.1.0}"
PYTORCH_VERSION="${PYTORCH_VERSION:-2.7.0}"
TORCHVISION_VERSION="${TORCHVISION_VERSION:-0.22.0}"
CUDA_WHEEL_INDEX="${CUDA_WHEEL_INDEX:-https://download.pytorch.org/whl/cu128}"
ISAACLAB_REPO_URL="${ISAACLAB_REPO_URL:-https://github.com/isaac-sim/IsaacLab.git}"

if [[ -z "${ISAACLAB_PATH:-}" ]]; then
  echo "ERROR: ISAACLAB_PATH is unset. Set it to the target IsaacLab checkout path." >&2
  exit 2
fi

PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"

echo "Project root: ${PROJECT_ROOT}"
echo "IsaacLab path: ${ISAACLAB_PATH}"
echo "Isaac Lab target: ${ISAACLAB_VERSION}"
echo "Isaac Sim target: ${ISAACSIM_VERSION}"
echo "PyTorch target: ${PYTORCH_VERSION} CUDA 12.8"

python - <<'PY'
import sys

if sys.version_info[:2] != (3, 11):
    raise SystemExit(
        f"ERROR: Python 3.11 is required for this project; got {sys.version.split()[0]}"
    )
print("Python:", sys.version.split()[0])
PY

if [[ ! -d "${ISAACLAB_PATH}/.git" ]]; then
  echo "Cloning IsaacLab into ${ISAACLAB_PATH}..."
  mkdir -p "$(dirname "${ISAACLAB_PATH}")"
  git clone "${ISAACLAB_REPO_URL}" "${ISAACLAB_PATH}"
fi

cd "${ISAACLAB_PATH}"
git fetch --tags
git checkout "${ISAACLAB_VERSION}"

python -m pip install --upgrade pip
python -m pip install "isaacsim[all,extscache]==${ISAACSIM_VERSION}" \
  --extra-index-url https://pypi.nvidia.com
python -m pip install -U "torch==${PYTORCH_VERSION}" "torchvision==${TORCHVISION_VERSION}" \
  --index-url "${CUDA_WHEEL_INDEX}"

if [[ ! -x "${ISAACLAB_PATH}/isaaclab.sh" ]]; then
  echo "ERROR: ${ISAACLAB_PATH}/isaaclab.sh is missing or not executable after checkout." >&2
  exit 2
fi

./isaaclab.sh --install rsl_rl

cd "${PROJECT_ROOT}"
if [[ -f pyproject.toml || -f setup.py ]]; then
  python -m pip install -e .
fi

echo "Runtime setup completed. Run scripts/validate_runtime_isaaclab.sh next."
