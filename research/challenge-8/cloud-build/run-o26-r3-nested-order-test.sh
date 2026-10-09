#!/usr/bin/env bash
# Separate Cloud TEST after an already captured R3 source; never proof acceptance.
set -euo pipefail

r3_source=
r3_evidence=
compiler_sysroot=
evidence=
deadline_epoch=
proof_root=
work_root=
cloud_dir=
while (($#)); do
  case "$1" in
    --r3-source) r3_source=$2; shift 2 ;;
    --r3-evidence) r3_evidence=$2; shift 2 ;;
    --compiler-sysroot) compiler_sysroot=$2; shift 2 ;;
    --evidence) evidence=$2; shift 2 ;;
    --deadline-epoch) deadline_epoch=$2; shift 2 ;;
    --proof-root) proof_root=$2; shift 2 ;;
    --work-root) work_root=$2; shift 2 ;;
    --cloud-dir) cloud_dir=$2; shift 2 ;;
    *) printf 'unknown R3 scheduling TEST argument: %s\n' "$1" >&2; exit 2 ;;
  esac
done
for path in "$r3_source" "$r3_evidence" "$compiler_sysroot" "$evidence" \
            "$proof_root" "$work_root" "$cloud_dir"; do
  [[ -n "$path" && "$path" == /workspace/* &&
     "$path" != *'/../'* && "$path" != *'/./'* ]] || exit 2
done
[[ "$deadline_epoch" =~ ^[0-9]+$ ]] || exit 2
[[ "${SMALLSORT_EXECUTION_PROVIDER:-}" == cloud-build &&
   -z "${GITHUB_ACTIONS:-}" &&
   "$(git -C "$proof_root" rev-parse HEAD)" == "${PROOF_SHA:?}" &&
   -d "$r3_source/.git" && -f "$r3_source/bin/verifast" &&
   -f "$r3_evidence/capture-check.json" &&
   ! -e "$evidence" ]] || exit 2
test_source="$work_root/o26-r3-nested-scheduled-source"
[[ ! -e "$test_source" ]] || exit 2
patch="$proof_root/research/challenge-8/overnight-assume-actual/verifast-r3-nested-before-outer-TEST.patch"
profile="$cloud_dir/o26-r3-nested-order-test.py"
[[ -f "$patch" && -f "$profile" ]] || exit 2
mkdir -p "$evidence"
common=(--proof-root "$proof_root" --cloud-dir "$cloud_dir"
        --r3-source "$r3_source" --test-source "$test_source"
        --r3-evidence "$r3_evidence" --evidence "$evidence"
        --compiler-sysroot "$compiler_sysroot" --deadline-epoch "$deadline_epoch")
current_stage=preflight
stage() {
  local name=$1; shift
  local seconds code=0
  current_stage=$name
  seconds=$((deadline_epoch - $(date +%s) - 25))
  ((seconds > 0)) || return 124
  /usr/bin/time -v -o "$evidence/$name-resources.txt" \
    timeout --signal=TERM --kill-after=10s "${seconds}s" "$@" \
    > "$evidence/$name.log" 2>&1 || code=$?
  printf '%s\n' "$code" > "$evidence/$name-exit-code.txt"
  cat "$evidence/$name.log"
  return "$code"
}
write_inconclusive() {
  local status=$?
  if [[ ! -f "$evidence/diagnostic-audit.json" ]]; then
    python3 "$profile" audit "${common[@]}" --runner-exit "$status" \
      --failed-stage "$current_stage" > "$evidence/audit.log" 2>&1 || true
  fi
}
trap write_inconclusive EXIT

stage test-preflight python3 "$profile" preflight "${common[@]}"
stage test-copy cp -a "$r3_source" "$test_source"
stage test-patch-check git -C "$test_source" apply --check "$patch"
stage test-patch-apply git -C "$test_source" apply "$patch"
[[ "$(sha256sum "$test_source/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml" | cut -d ' ' -f 1)" == \
   85962191c8613fbddae4931f65e32da06abca3df158d0dcb92cc21c4411986a6 ]] || exit 2
cp "$patch" "$evidence/test-patch.patch"

deps_home="$work_root/vfdeps-adf88dc"
[[ -d "$deps_home/bin" && -d "$deps_home/include" && -d "$deps_home/lib" ]] || exit 2
export PATH="$deps_home/bin:$PATH"
export CAPNP_INC_DIR="$deps_home/include"
export RUSTUP_TOOLCHAIN=nightly-2026-09-25
export LD_LIBRARY_PATH="$compiler_sysroot/lib:$test_source/bin:$deps_home/lib:${LD_LIBRARY_PATH:-}"
rm "$test_source/bin/verifast"
stage test-console-build make -C "$test_source/src" ../bin/verifast WITHOUT_LABLGTK=yes VERBOSE=yes
[[ -f "$test_source/bin/verifast" ]] || exit 2
ldd "$test_source/bin/verifast" > "$evidence/test-console-ldd.txt"
! rg -q 'not found' "$evidence/test-console-ldd.txt"
stage test-identity python3 "$profile" test-identity "${common[@]}"
stage test-full-proof python3 "$profile" proof "${common[@]}"
stage test-final-identity python3 "$profile" final-identity "${common[@]}"
current_stage=audit
python3 "$profile" audit "${common[@]}" --runner-exit 0 \
  --failed-stage complete
printf '%s\n' 'R3_NESTED_SCHEDULING_TEST_ONLY_NOT_ACCEPTED' > "$evidence/TEST-STATUS.txt"
