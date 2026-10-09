#!/usr/bin/env bash
# Cloud-only distinct R3 ghost-scope TEST; all tool copies stay outside evidence.
set -euo pipefail
[[ "${SMALLSORT_EXECUTION_PROVIDER:-}" == cloud-build &&
   "${LANE:-}" == o26-r3-ghost-scope-test && -z "${GITHUB_ACTIONS:-}" ]] || exit 2
export O26_WITH_R3_RECEIVER_TEST=${O26_WITH_R3_RECEIVER_TEST:-0}
[[ "$O26_WITH_R3_RECEIVER_TEST" == 0 || "$O26_WITH_R3_RECEIVER_TEST" == 1 ]] || exit 2
cloud_dir=${INFRA_CLOUD_DIR:-/workspace/infra/research/challenge-8/cloud-build}
work_root=${WORK_ROOT:-/workspace/smallsort-work}
compiler_sysroot=
r3_source=
r3_evidence=
evidence=
proof_root=
deadline_epoch=
while (($#)); do
  case "$1" in
    --compiler-sysroot) compiler_sysroot=$2; shift 2 ;;
    --r3-source) r3_source=$2; shift 2 ;;
    --r3-evidence) r3_evidence=$2; shift 2 ;;
    --evidence) evidence=$2; shift 2 ;;
    --proof-root) proof_root=$2; shift 2 ;;
    --deadline-epoch) deadline_epoch=$2; shift 2 ;;
    *) exit 2 ;;
  esac
done
[[ "$cloud_dir" == /workspace/* && "$work_root" == /workspace/* &&
   "$compiler_sysroot" == /workspace/* && "$r3_source" == /workspace/* &&
   "$r3_evidence" == /workspace/* && "$evidence" == /workspace/* &&
   "$proof_root" == /workspace/* && "$deadline_epoch" =~ ^[0-9]+$ ]] || exit 2
deps_home="$work_root/vfdeps-adf88dc"
[[ -d "$deps_home/bin" && -d "$deps_home/include" && -d "$deps_home/lib" &&
   -d "$compiler_sysroot/lib" && -f "$cloud_dir/o26-r3-ghost-scope-test.py" ]] || exit 2
export PATH="$deps_home/bin:$PATH"
export CAPNP_INC_DIR="$deps_home/include"
export RUSTUP_TOOLCHAIN=nightly-2026-09-25
export LD_LIBRARY_PATH="$compiler_sysroot/lib:$r3_source/bin:$deps_home/lib:${LD_LIBRARY_PATH:-}"
exec python3 "$cloud_dir/o26-r3-ghost-scope-test.py" \
  --r3-source "$r3_source" --compiler-sysroot "$compiler_sysroot" \
  --cloud-dir "$cloud_dir" --work-root "$work_root" \
  --r3-evidence "$r3_evidence" --evidence "$evidence" \
  --proof-root "$proof_root" --deadline-epoch "$deadline_epoch"
