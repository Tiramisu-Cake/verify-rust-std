#!/usr/bin/env bash
# Cloud-only pinned historical controls verification and re-audit.
set -euo pipefail
[[ "${SMALLSORT_EXECUTION_PROVIDER:-}" == cloud-build &&
   "${LANE:-}" == o26-strict-cut-reuse-false-posts &&
   -z "${GITHUB_ACTIONS:-}" ]] || exit 2
cloud_dir=${INFRA_CLOUD_DIR:-/workspace/infra/research/challenge-8/cloud-build}
[[ "$cloud_dir" == /workspace/* && -f "$cloud_dir/strict-cut-reuse-controls.py" ]] || exit 2
exec python3 "$cloud_dir/strict-cut-reuse-controls.py" "$@"
