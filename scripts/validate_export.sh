#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
EXPORT_DIR="${EXPORT_DIR:-${PROJECT_ROOT}/results/exports/go2_policy}"
EXPORT_FORMAT="${EXPORT_FORMAT:-torchscript}"
MANIFEST_PATH="${MANIFEST_PATH:-${EXPORT_DIR}/export_manifest.json}"

case "${EXPORT_FORMAT}" in
  torchscript)
    POLICY_PATH="${POLICY_PATH:-${EXPORT_DIR}/policy.pt}"
    ;;
  onnx)
    POLICY_PATH="${POLICY_PATH:-${EXPORT_DIR}/policy.onnx}"
    ;;
  *)
    echo "ERROR: EXPORT_FORMAT must be torchscript or onnx." >&2
    exit 2
    ;;
esac

if [[ ! -d "${EXPORT_DIR}" ]]; then
  echo "ERROR: export directory does not exist: ${EXPORT_DIR}" >&2
  exit 2
fi

if [[ ! -f "${POLICY_PATH}" ]]; then
  echo "ERROR: exported policy file is missing: ${POLICY_PATH}" >&2
  exit 2
fi

if [[ ! -f "${MANIFEST_PATH}" ]]; then
  echo "ERROR: export manifest is missing: ${MANIFEST_PATH}" >&2
  exit 2
fi

PYTHONPATH="${PROJECT_ROOT}/source${PYTHONPATH:+:${PYTHONPATH}}" python - <<PY
from isaaclab_quadruped.deployment.export_manifest import read_manifest

manifest = read_manifest("${MANIFEST_PATH}")
if manifest.export_format != "${EXPORT_FORMAT}":
    raise SystemExit(
        f"manifest export_format mismatch: {manifest.export_format} != ${EXPORT_FORMAT}"
    )
print(f"Validated export manifest for {manifest.env_id}")
print(f"Policy file: ${POLICY_PATH}")
PY
