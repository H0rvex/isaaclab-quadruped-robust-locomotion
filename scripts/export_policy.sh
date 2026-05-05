#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${ISAACLAB_PATH:-}" ]]; then
  echo "ERROR: ISAACLAB_PATH is unset. Run policy export on the rented GPU Isaac Lab machine." >&2
  exit 2
fi

if [[ ! -x "${ISAACLAB_PATH}/isaaclab.sh" ]]; then
  echo "ERROR: ${ISAACLAB_PATH}/isaaclab.sh is missing or not executable." >&2
  exit 2
fi

if [[ -z "${CHECKPOINT_PATH:-}" ]]; then
  echo "ERROR: CHECKPOINT_PATH is unset. Set it to the trained RSL-RL checkpoint." >&2
  exit 2
fi

if [[ ! -f "${CHECKPOINT_PATH}" ]]; then
  echo "ERROR: checkpoint file does not exist: ${CHECKPOINT_PATH}" >&2
  exit 2
fi

PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
EXPORT_DIR="${EXPORT_DIR:-${PROJECT_ROOT}/results/exports/go2_policy}"
TASK_ID="${TASK_ID:-Isaac-Velocity-Rough-Unitree-Go2-v0}"
EXPORT_FORMAT="${EXPORT_FORMAT:-torchscript}"
OBSERVATION_DIMENSION="${OBSERVATION_DIMENSION:-45}"
ACTION_DIMENSION="${ACTION_DIMENSION:-12}"
NORMALIZATION_INFO="${NORMALIZATION_INFO:-none}"

case "${EXPORT_FORMAT}" in
  torchscript)
    POLICY_FILENAME="policy.pt"
    ;;
  onnx)
    POLICY_FILENAME="policy.onnx"
    ;;
  *)
    echo "ERROR: EXPORT_FORMAT must be torchscript or onnx." >&2
    exit 2
    ;;
esac

mkdir -p "${EXPORT_DIR}"

cat <<EOF
Policy export scaffold
----------------------
Run this script on the rented GPU machine after training has produced a checkpoint.

Expected environment:
  ISAACLAB_PATH=${ISAACLAB_PATH}
  PROJECT_ROOT=${PROJECT_ROOT}
  CHECKPOINT_PATH=${CHECKPOINT_PATH}
  TASK_ID=${TASK_ID}
  EXPORT_DIR=${EXPORT_DIR}
  EXPORT_FORMAT=${EXPORT_FORMAT}

Expected output files:
  ${EXPORT_DIR}/${POLICY_FILENAME}
  ${EXPORT_DIR}/export_manifest.json

This scaffold records the export contract, but the actual Isaac Lab/RSL-RL export
command still needs to be wired to the selected runtime exporter.
EOF

PYTHONPATH="${PROJECT_ROOT}/source${PYTHONPATH:+:${PYTHONPATH}}" python - <<PY
from isaaclab_quadruped.deployment.export_manifest import create_manifest, write_manifest

manifest = create_manifest(
    env_id="${TASK_ID}",
    checkpoint_path="${CHECKPOINT_PATH}",
    export_format="${EXPORT_FORMAT}",
    observation_dimension=int("${OBSERVATION_DIMENSION}"),
    action_dimension=int("${ACTION_DIMENSION}"),
    normalization_info={"source": "${NORMALIZATION_INFO}"},
    repo_root="${PROJECT_ROOT}",
)
write_manifest("${EXPORT_DIR}/export_manifest.json", manifest)
PY

echo "Wrote ${EXPORT_DIR}/export_manifest.json"
echo "After the runtime exporter writes ${POLICY_FILENAME}, run:"
echo "  EXPORT_DIR=\"${EXPORT_DIR}\" EXPORT_FORMAT=\"${EXPORT_FORMAT}\" bash scripts/validate_export.sh"
