#!/usr/bin/env bash
# Cloud-only caller-entry diagnostic using the pinned O26 production source.
set -euo pipefail
[[ "${SMALLSORT_EXECUTION_PROVIDER:-}" == cloud-build &&
   "${LANE:-}" == o26-sort4-caller-entry &&
   -z "${GITHUB_ACTIONS:-}" ]] || exit 2
cloud_dir=${INFRA_CLOUD_DIR:-/workspace/infra/research/challenge-8/cloud-build}
exec python3 "$cloud_dir/sort4-caller-entry.py" "$@"
