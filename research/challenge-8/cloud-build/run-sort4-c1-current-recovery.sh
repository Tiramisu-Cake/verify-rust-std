#!/usr/bin/env bash
# Cloud-only, exact-source c1 CURRENT recovery diagnostic. Experimental profile.
set -euo pipefail
[[ "${SMALLSORT_EXECUTION_PROVIDER:-}" == cloud-build &&
   "${LANE:-}" == o26-sort4-c1-current-recovery &&
   -z "${GITHUB_ACTIONS:-}" ]] || exit 2
cloud_dir=${INFRA_CLOUD_DIR:-/workspace/infra/research/challenge-8/cloud-build}
if [[ "${SORT4_NATIVE_C1_BOUND_PHASE:-}" == 1 ]]; then
  [[ "${SORT4_NATIVE_C1_BOUND_PHASE_ID:-}" == SORT4-NATIVE-C1-BOUND-CLOUD-2026-10-10 &&
     -z "${SORT4_NATIVE_C4_PHASE:-}" &&
     -z "${SORT4_NATIVE_OPAQUE_PHASE:-}" ]] || exit 2
  exec python3 "$cloud_dir/sort4-native-c4/driver.py" "$@"
fi
if [[ "${SORT4_NATIVE_OPAQUE_PHASE:-}" == 1 ]]; then
  [[ "${SORT4_NATIVE_OPAQUE_PHASE_ID:-}" == SORT4-NATIVE-OPAQUE-CLOUD-2026-10-10 &&
     -z "${SORT4_NATIVE_C4_PHASE:-}" ]] || exit 2
  exec python3 "$cloud_dir/sort4-native-c4/driver.py" "$@"
fi
if [[ "${SORT4_NATIVE_C4_PHASE:-}" == 1 ]]; then
  [[ "${SORT4_NATIVE_C4_PHASE_ID:-}" == SORT4-NATIVE-C4-CLOUD-2026-10-10 ]] || exit 2
  exec python3 "$cloud_dir/sort4-native-c4/driver.py" "$@"
fi
exec python3 "$cloud_dir/sort4-c1-current-recovery.py" "$@"
