#!/usr/bin/env bash
# Isolated component-23 draft; called only after canonical O26 refresh proof.
set -euo pipefail

production_source=
production_patch=
stock_home=
compiler_sysroot=
evidence=
deadline_epoch=
proof_root=
work_root=
cloud_dir=
comp19_mode=${O26_WITH_WRAPPER_COMP19_TEST:-0}
[[ "$comp19_mode" == 0 || "$comp19_mode" == 1 ]] || exit 2
[[ "$comp19_mode" == 0 || "${LANE:-}" == o26-wrapper-controls ]] || exit 2
while (($#)); do
  case "$1" in
    --production-source) production_source=$2; shift 2 ;;
    --production-applied-patch) production_patch=$2; shift 2 ;;
    --stock-home) stock_home=$2; shift 2 ;;
    --compiler-sysroot) compiler_sysroot=$2; shift 2 ;;
    --evidence) evidence=$2; shift 2 ;;
    --deadline-epoch) deadline_epoch=$2; shift 2 ;;
    --proof-root) proof_root=$2; shift 2 ;;
    --work-root) work_root=$2; shift 2 ;;
    --cloud-dir) cloud_dir=$2; shift 2 ;;
    *) printf 'unknown wrapper profile argument: %s\n' "$1" >&2; exit 2 ;;
  esac
done
for path in "$production_source" "$production_patch" "$stock_home" "$compiler_sysroot" \
  "$evidence" "$proof_root" "$work_root" "$cloud_dir"; do
  [[ "$path" == /workspace/* && "$path" != *'/../'* && "$path" != *'/./'* ]] || exit 2
done
[[ "$deadline_epoch" =~ ^[0-9]+$ ]] || exit 2
[[ "${SMALLSORT_EXECUTION_PROVIDER:-}" == cloud-build && -z "${GITHUB_ACTIONS:-}" ]] || exit 2
[[ "$(git -C "$proof_root" rev-parse HEAD)" == "${PROOF_SHA:?}" ]] || exit 2
[[ -d "$production_source/.git" && -f "$production_patch" && -f "$production_source/bin/verifast" ]] || exit 2
[[ -f "$cloud_dir/o26-wrapper-profile.py" && -f "$cloud_dir/o26-recipe.py" ]] || exit 2
[[ "$(basename "$(dirname "$evidence")")" == cases ]] || exit 2
[[ ! -e "$evidence" ]] || exit 2
profile_source="$work_root/o26-wrapper-profile-source"
[[ ! -e "$profile_source" ]] || exit 2
mkdir -p "$evidence"
common=(--production-source "$production_source" --production-patch "$production_patch"
  --profile-source "$profile_source" --stock-home "$stock_home"
  --compiler-sysroot "$compiler_sysroot" --evidence "$evidence"
  --deadline-epoch "$deadline_epoch" --proof-root "$proof_root"
  --cloud-dir "$cloud_dir")
script="$cloud_dir/o26-wrapper-profile.py"
remaining() {
  local seconds=$((deadline_epoch - $(date +%s) - 20))
  (( seconds > 0 )) || { printf 'wrapper profile deadline reached\n' >&2; exit 124; }
  printf '%s' "$seconds"
}
stage() {
  local name=$1; shift
  local seconds code=0
  seconds=$(remaining)
  /usr/bin/time -v -o "$evidence/$name-resources.txt" \
    timeout --signal=TERM --kill-after=10s "${seconds}s" "$@" \
    > "$evidence/$name.log" 2>&1 || code=$?
  printf '%s\n' "$code" > "$evidence/$name-exit-code.txt"
  cat "$evidence/$name.log"
  return "$code"
}

# Placeholder observed pins are rejected before any tool copy, build, or proof.
stage profile-preflight python3 "$script" preflight "${common[@]}"
stage profile-production-snapshot python3 "$script" production-snapshot "${common[@]}"
patch="$proof_root/research/challenge-8/overnight-assume-actual/verifast-o26-wrapper-rebase-profile-26.10.patch"
[[ -f "$patch" ]] || exit 2
stage profile-copy cp -a "$production_source" "$profile_source"
cmp "$production_patch" <(git -C "$profile_source" diff --binary HEAD)
stage profile-patch-check git -C "$profile_source" apply --check "$patch"
stage profile-patch-apply git -C "$profile_source" apply "$patch"
[[ "$(git -C "$profile_source" rev-parse HEAD)" == f76012fb518703b1d98e243ac4f487f16877cfcb ]] || exit 2
deps_home="$work_root/vfdeps-adf88dc"
[[ -d "$deps_home/bin" && -d "$deps_home/include" && -d "$deps_home/lib" ]] || exit 2
export PATH="$deps_home/bin:$PATH"
export CAPNP_INC_DIR="$deps_home/include"
export RUSTUP_TOOLCHAIN=nightly-2026-09-25
export LD_LIBRARY_PATH="$compiler_sysroot/lib:$profile_source/bin:$deps_home/lib:${LD_LIBRARY_PATH:-}"
rm "$profile_source/bin/verifast"
stage profile-console-build make -C "$profile_source/src" ../bin/verifast WITHOUT_LABLGTK=yes VERBOSE=yes
[[ -f "$profile_source/bin/verifast" ]] || exit 2
ldd "$profile_source/bin/verifast" > "$evidence/profile-console-ldd.txt"
! rg -q 'not found' "$evidence/profile-console-ldd.txt"
stage profile-tool-identity python3 "$script" tool-identity "${common[@]}"
stage profile-capture python3 "$proof_root/research/challenge-8/overnight-assume-actual/capture.py" \
  --tool-home "$profile_source" \
  --schema "$profile_source/src/rust_frontend/vf_mir/vf_mir.capnp" \
  --compiler-sysroot "$compiler_sysroot" --evidence "$evidence/capture" \
  --deadline-epoch "$deadline_epoch" --wrapper-rebase --fingerprint
stage profile-capture-check python3 "$script" capture-check "${common[@]}"
stage profile-proofs python3 "$script" proofs "${common[@]}"
stage profile-owner-controls python3 "$script" owner-controls "${common[@]}"
a1="$evidence/a1-isolated-test"
mkdir "$a1"
test_source="$work_root/o26-wrapper-profile-a1-test-source"
[[ ! -e "$test_source" ]] || exit 2
a1script="$cloud_dir/o26-wrapper-profile-a1.py"
[[ -f "$a1script" ]] || exit 2
a1common=(--proof-root "$proof_root" --cloud-dir "$cloud_dir"
  --profile-source "$profile_source" --test-source "$test_source"
  --compiler-sysroot "$compiler_sysroot" --evidence "$a1"
  --deadline-epoch "$deadline_epoch")
stage a1-rebase-capture python3 "$a1script" capture "${a1common[@]}"
stage a1-owner-hash-delta python3 "$a1script" delta "${a1common[@]}"
stage a1-test-copy cp -a "$profile_source" "$test_source"
cmp <(git -C "$profile_source" diff --binary HEAD) \
    <(git -C "$test_source" diff --binary HEAD)
stage a1-delta-check git -C "$test_source" apply --check "$a1/test-owner17-delta.patch"
stage a1-delta-apply git -C "$test_source" apply "$a1/test-owner17-delta.patch"
rm "$test_source/bin/verifast"
stage a1-test-console-build make -C "$test_source/src" ../bin/verifast WITHOUT_LABLGTK=yes VERBOSE=yes
[[ -f "$test_source/bin/verifast" ]] || exit 2
ldd "$test_source/bin/verifast" > "$a1/test-console-ldd.txt"
! rg -q 'not found' "$a1/test-console-ldd.txt"
stage a1-move-copy-negative python3 "$a1script" test "${a1common[@]}"
comp19_status=0
if [[ "$comp19_mode" == 1 ]]; then
  stage comp19-isolated-test bash "$cloud_dir/run-o26-wrapper-comp19-test.sh" \
    --profile-source "$profile_source" --compiler-sysroot "$compiler_sysroot" \
    --evidence "$evidence/comp19-isolated-test" --deadline-epoch "$deadline_epoch" \
    --proof-root "$proof_root" --work-root "$work_root" --cloud-dir "$cloud_dir" || comp19_status=$?
  printf '%s\n' "$comp19_status" > "$evidence/comp19-helper-exit-code.txt"
fi
stage profile-final-identity python3 "$script" final-identity "${common[@]}"
printf '%s\n' 'WRAPPER_REBASE_COMPONENT23_DIAGNOSTIC_NOT_ACCEPTED' > "$evidence/PROFILE-STATUS.txt"
(( comp19_status == 0 )) || exit "$comp19_status"
