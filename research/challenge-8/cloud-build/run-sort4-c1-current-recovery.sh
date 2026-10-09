#!/usr/bin/env bash
# Cloud-only, exact-source c1 CURRENT recovery diagnostic. Experimental profile.
set -euo pipefail
[[ "${SMALLSORT_EXECUTION_PROVIDER:-}" == cloud-build &&
   "${LANE:-}" == o26-sort4-c1-current-recovery &&
   -z "${GITHUB_ACTIONS:-}" ]] || exit 2
cloud_dir=${INFRA_CLOUD_DIR:-/workspace/infra/research/challenge-8/cloud-build}
exec python3 "$cloud_dir/sort4-c1-current-recovery.py" "$@"
