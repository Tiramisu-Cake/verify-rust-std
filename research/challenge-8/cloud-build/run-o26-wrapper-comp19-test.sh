#!/usr/bin/env bash
# Future opt-in Cloud hook, separate from the current profile recipe.
set -euo pipefail

profile_source=
compiler_sysroot=
evidence=
deadline_epoch=
proof_root=
work_root=
cloud_dir=
while (($#)); do
  case "$1" in
    --profile-source) profile_source=$2; shift 2 ;;
    --compiler-sysroot) compiler_sysroot=$2; shift 2 ;;
    --evidence) evidence=$2; shift 2 ;;
    --deadline-epoch) deadline_epoch=$2; shift 2 ;;
    --proof-root) proof_root=$2; shift 2 ;;
    --work-root) work_root=$2; shift 2 ;;
    --cloud-dir) cloud_dir=$2; shift 2 ;;
    *) printf 'unknown component-19 TEST argument: %s\n' "$1" >&2; exit 2 ;;
  esac
done
for path in "$profile_source" "$compiler_sysroot" "$evidence" "$proof_root" \
  "$work_root" "$cloud_dir"; do
  [[ "$path" == /workspace/* && "$path" != *'/../'* && "$path" != *'/./'* ]] || exit 2
done
[[ "$deadline_epoch" =~ ^[0-9]+$ ]] || exit 2
[[ "${SMALLSORT_EXECUTION_PROVIDER:-}" == cloud-build && -z "${GITHUB_ACTIONS:-}" ]] || exit 2
[[ "$(git -C "$proof_root" rev-parse HEAD)" == "${PROOF_SHA:?}" ]] || exit 2
[[ -d "$profile_source/.git" && -f "$profile_source/bin/verifast" ]] || exit 2
[[ -f "$cloud_dir/o26-wrapper-profile-comp19.py" && -f "$cloud_dir/o26-wrapper-profile-a1.py" ]] || exit 2
[[ "$(basename "$(dirname "$evidence")")" == wrapper-profile ]] || exit 2
[[ ! -e "$evidence" ]] || exit 2
test_source="$work_root/o26-wrapper-profile-comp19-test-source"
[[ ! -e "$test_source" ]] || exit 2
mkdir -p "$evidence"
[[ -f "$cloud_dir/provider.py" ]] || exit 2
CLOUD_BUILD_ID=${CLOUD_BUILD_ID:?} \
CLOUD_BUILD_PROJECT_ID=${CLOUD_BUILD_PROJECT_ID:?} \
CLOUD_BUILD_REGION=${CLOUD_BUILD_REGION:?} \
  python3 "$cloud_dir/provider.py" > "$evidence/provider.json"
python3 - "$evidence/provider.json" <<'PROVIDER'
import json,sys
assert json.load(open(sys.argv[1]))['provider']=='cloud-build'
PROVIDER
script="$cloud_dir/o26-wrapper-profile-comp19.py"
common=(--profile-source "$profile_source" --test-source "$test_source"
  --compiler-sysroot "$compiler_sysroot" --evidence "$evidence"
  --deadline-epoch "$deadline_epoch" --proof-root "$proof_root"
  --cloud-dir "$cloud_dir")
remaining() {
  local seconds=$((deadline_epoch - $(date +%s) - 20))
  (( seconds > 0 )) || { printf 'component-19 TEST deadline reached\n' >&2; exit 124; }
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

stage comp19-fresh-capture python3 "$script" capture "${common[@]}"
stage comp19-owner-hash-delta python3 "$script" delta "${common[@]}"
stage comp19-test-copy cp -a "$profile_source" "$test_source"
cmp <(git -C "$profile_source" diff --binary HEAD) \
    <(git -C "$test_source" diff --binary HEAD)
stage comp19-delta-check git -C "$test_source" apply --check "$evidence/test-owner17-delta.patch"
stage comp19-delta-apply git -C "$test_source" apply "$evidence/test-owner17-delta.patch"
deps_home="$work_root/vfdeps-adf88dc"
[[ -d "$deps_home/bin" && -d "$deps_home/include" && -d "$deps_home/lib" ]] || exit 2
export PATH="$deps_home/bin:$PATH"
export CAPNP_INC_DIR="$deps_home/include"
export RUSTUP_TOOLCHAIN=nightly-2026-09-25
export LD_LIBRARY_PATH="$compiler_sysroot/lib:$test_source/bin:$deps_home/lib:${LD_LIBRARY_PATH:-}"
rm "$test_source/bin/verifast"
stage comp19-test-console-build make -C "$test_source/src" ../bin/verifast WITHOUT_LABLGTK=yes VERBOSE=yes
[[ -f "$test_source/bin/verifast" ]] || exit 2
ldd "$test_source/bin/verifast" > "$evidence/test-console-ldd.txt"
! rg -q 'not found' "$evidence/test-console-ldd.txt"
stage comp19-move-copy-negative python3 "$script" test "${common[@]}"
printf '%s\n' 'COMP19_MOVE_COPY_TEST_DIAGNOSTIC_ONLY_NOT_ACCEPTED' > "$evidence/PROFILE-STATUS.txt"
