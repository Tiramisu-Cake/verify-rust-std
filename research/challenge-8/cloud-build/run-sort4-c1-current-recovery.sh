#!/usr/bin/env bash
# Cloud-only, exact-source c1 CURRENT recovery diagnostic. Experimental profile.
set -euo pipefail
[[ "${SMALLSORT_EXECUTION_PROVIDER:-}" == cloud-build &&
   "${LANE:-}" == o26-sort4-c1-current-recovery &&
   -z "${GITHUB_ACTIONS:-}" ]] || exit 2
cloud_dir=${INFRA_CLOUD_DIR:-/workspace/infra/research/challenge-8/cloud-build}
if [[ "${SORT4_A1_AUTHORIZATION_PHASE_ID:-}" == SORT4-CHECKED-CALLER-NATIVE-PROOF-2026-10-21-R11 ]]; then
  [[ "${SORT4_A1_PHASE_ID:-}" == SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17 &&
     "${SORT4_A1_CHECKED_TRAIT_CONTRACT:-}" == 1 &&
     -n "${SORT4_A1_PROFILE_SHA256:-}" &&
     -z "${SORT4_ACTUAL_CALLER_ENTRY_PHASE:-}" &&
     -z "${SORT4_NATIVE_C4_PHASE:-}" && -z "${SORT4_NATIVE_OPAQUE_PHASE:-}" &&
     -z "${SORT4_NATIVE_C1_ZST_REPAIR_PHASE:-}" ]] || exit 2
  exec python3 "$cloud_dir/sort4-caller-entry-native/a1-entry-r11.py" "$@"
fi
if [[ "${SORT4_A1_AUTHORIZATION_PHASE_ID:-}" == SORT4-DELIVERABLE-NATIVE-PROOF-2026-10-20-R10 ]]; then
  [[ "${SORT4_A1_PHASE_ID:-}" == SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17 &&
     "${SORT4_A1_CHECKED_TRAIT_CONTRACT:-}" == 1 &&
     -z "${SORT4_ACTUAL_CALLER_ENTRY_PHASE:-}" &&
     -z "${SORT4_NATIVE_C4_PHASE:-}" && -z "${SORT4_NATIVE_OPAQUE_PHASE:-}" &&
     -z "${SORT4_NATIVE_C1_ZST_REPAIR_PHASE:-}" ]] || exit 2
  exec python3 "$cloud_dir/sort4-caller-entry-native/a1-entry-r10.py" "$@"
fi
if [[ "${SORT4_A1_AUTHORIZATION_PHASE_ID:-}" == SORT4-NATIVE-INTERFACE-PROOF-2026-10-20-R9 ]]; then
  [[ "${SORT4_A1_PHASE_ID:-}" == SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17 &&
     "${SORT4_A1_CHECKED_TRAIT_CONTRACT:-}" == 1 &&
     -z "${SORT4_ACTUAL_CALLER_ENTRY_PHASE:-}" &&
     -z "${SORT4_NATIVE_C4_PHASE:-}" && -z "${SORT4_NATIVE_OPAQUE_PHASE:-}" &&
     -z "${SORT4_NATIVE_C1_ZST_REPAIR_PHASE:-}" ]] || exit 2
  exec python3 "$cloud_dir/sort4-caller-entry-native/a1-entry-r9.py" "$@"
fi
if [[ "${SORT4_A1_AUTHORIZATION_PHASE_ID:-}" == SORT4-POST-MIGRATION-NATIVE-PROOF-2026-10-20-R8 ]]; then
  [[ "${SORT4_A1_PHASE_ID:-}" == SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17 &&
     "${SORT4_A1_CHECKED_TRAIT_CONTRACT:-}" == 1 &&
     -z "${SORT4_ACTUAL_CALLER_ENTRY_PHASE:-}" &&
     -z "${SORT4_NATIVE_C4_PHASE:-}" && -z "${SORT4_NATIVE_OPAQUE_PHASE:-}" &&
     -z "${SORT4_NATIVE_C1_ZST_REPAIR_PHASE:-}" ]] || exit 2
  exec python3 "$cloud_dir/sort4-caller-entry-native/a1-entry-r8.py" "$@"
fi
if [[ "${SORT4_A1_AUTHORIZATION_PHASE_ID:-}" == SORT4-PACKAGING-NATIVE-PROOF-2026-10-20-R7 ]]; then
  [[ "${SORT4_A1_PHASE_ID:-}" == SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17 &&
     "${SORT4_A1_CHECKED_TRAIT_CONTRACT:-}" == 1 &&
     -z "${SORT4_ACTUAL_CALLER_ENTRY_PHASE:-}" &&
     -z "${SORT4_NATIVE_C4_PHASE:-}" && -z "${SORT4_NATIVE_OPAQUE_PHASE:-}" &&
     -z "${SORT4_NATIVE_C1_ZST_REPAIR_PHASE:-}" ]] || exit 2
  exec python3 "$cloud_dir/sort4-caller-entry-native/a1-entry-r7.py" "$@"
fi
if [[ -n "${SORT4_A1_PHASE_ID:-}" || -n "${SORT4_A1_CHECKED_TRAIT_CONTRACT:-}" ]]; then
  [[ "${SORT4_A1_PHASE_ID:-}" == SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17 &&
     "${SORT4_A1_CHECKED_TRAIT_CONTRACT:-}" == 1 &&
     -z "${SORT4_ACTUAL_CALLER_ENTRY_PHASE:-}" &&
     -z "${SORT4_NATIVE_C4_PHASE:-}" && -z "${SORT4_NATIVE_OPAQUE_PHASE:-}" &&
     -z "${SORT4_NATIVE_C1_ZST_REPAIR_PHASE:-}" ]] || exit 2
  exec python3 "$cloud_dir/sort4-caller-entry-native/a1-entry.py" "$@"
fi
if [[ -n "${SORT4_ACTUAL_CALLER_ENTRY_PHASE:-}" ||
      -n "${SORT4_ACTUAL_CALLER_ENTRY_PHASE_ID:-}" ]]; then
  [[ "${SORT4_ACTUAL_CALLER_ENTRY_PHASE:-}" == 1 &&
     ( "${SORT4_ACTUAL_CALLER_ENTRY_PHASE_ID:-}" == SORT4-ACTUAL-CALLER-ENTRY-CLOUD-2026-10-11 ||
       "${SORT4_ACTUAL_CALLER_ENTRY_PHASE_ID:-}" == SORT4-CALLER-DERIVED-BOUND-CLOUD-2026-10-11 ||
       "${SORT4_ACTUAL_CALLER_ENTRY_PHASE_ID:-}" == SORT4-COMPILER-BINDING-PREFIX-CLOUD-2026-10-11 ) &&
     "${LANE:-}" == o26-sort4-c1-current-recovery &&
     -z "${SORT4_NATIVE_C4_PHASE:-}" &&
     -z "${SORT4_NATIVE_C4_PHASE_ID:-}" &&
     -z "${SORT4_NATIVE_OPAQUE_PHASE:-}" &&
     -z "${SORT4_NATIVE_OPAQUE_PHASE_ID:-}" &&
     -z "${SORT4_NATIVE_C1_ZST_REPAIR_PHASE:-}" &&
     -z "${SORT4_NATIVE_C1_ZST_REPAIR_PHASE_ID:-}" ]] || exit 2
  exec python3 "$cloud_dir/sort4-caller-entry-native/driver.py" "$@"
fi
if [[ "${SORT4_NATIVE_C1_ZST_REPAIR_PHASE:-}" == 1 ]]; then
  [[ "${SORT4_NATIVE_C1_ZST_REPAIR_PHASE_ID:-}" == SORT4-NATIVE-C1-ZST-REPAIR-CLOUD-2026-10-11 &&
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
