#!/usr/bin/env bash
# Isolated O26 A1 negative TEST. It never upgrades the production proof.
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
    *) printf 'Unknown A1 TEST argument: %s\n' "$1" >&2; exit 2 ;;
  esac
done
for path in "$production_source" "$production_patch" "$stock_home" "$compiler_sysroot" "$evidence" "$proof_root" "$work_root" "$cloud_dir"; do
  [[ -n "$path" ]] || { printf 'A1 TEST requires all nine arguments\n' >&2; exit 2; }
done
[[ "$deadline_epoch" =~ ^[0-9]+$ ]] || exit 2
[[ "${SMALLSORT_EXECUTION_PROVIDER:-}" == cloud-build && -z "${GITHUB_ACTIONS:-}" ]] || exit 2
for path in "$production_source" "$production_patch" "$stock_home" "$compiler_sysroot" "$evidence" "$proof_root" "$work_root" "$cloud_dir"; do
  [[ "$path" == /workspace/* && "$path" != *'/../'* && "$path" != *'/./'* ]] || {
    printf 'A1 TEST path outside /workspace: %s\n' "$path" >&2; exit 2;
  }
done
[[ -d "$production_source/.git" && -f "$production_patch" && -f "$production_source/bin/verifast" ]] || exit 2
[[ -d "$proof_root/.git" && -d "$compiler_sysroot/lib" ]] || exit 2
[[ "$(git -C "$proof_root" rev-parse HEAD)" == "${PROOF_SHA:?PROOF_SHA is required}" ]] || exit 2
[[ "$(basename "$(dirname "$evidence")")" == cases ]] || {
  printf 'A1 TEST evidence must be an allprooflogs/cases child\n' >&2; exit 2;
}
[[ -f "$stock_home/bin/vf-rust-mir-exporter" && -f "$stock_home/bin/refinement-checker" ]] || exit 2
[[ -f "$cloud_dir/a1-isolated-test.py" && -f "$cloud_dir/o26-recipe.py" && -f "$cloud_dir/provider.py" ]] || exit 2
for relative in \
  research/challenge-8/overnight-assume-actual/O26-REFRESH-PROFILE.json \
  research/challenge-8/overnight-assume-actual/capture.py \
  research/challenge-8/overnight-assume-actual/prepare.py \
  research/challenge-8/overnight-helper/capture-actual-owner-mir-mutation.py \
  research/challenge-8/overnight-helper/prepare-actual-owner-linked.py; do
  [[ -f "$proof_root/$relative" ]] || { printf 'Missing A1 TEST input: %s\n' "$relative" >&2; exit 2; }
done
[[ ! -e "$evidence" ]] || { printf 'A1 TEST evidence exists: %s\n' "$evidence" >&2; exit 2; }
test_source="$work_root/a1-isolated-test-source"
[[ ! -e "$test_source" ]] || { printf 'A1 TEST source exists: %s\n' "$test_source" >&2; exit 2; }
mkdir -p "$evidence" "$work_root"
export A1_TEST_PROOF_ROOT="$proof_root"
common=(--production-source "$production_source" --production-patch "$production_patch"
  --stock-home "$stock_home" --compiler-sysroot "$compiler_sysroot"
  --evidence "$evidence" --deadline-epoch "$deadline_epoch"
  --proof-root "$proof_root" --work-root "$work_root" --cloud-dir "$cloud_dir")
trap 'status=$?; if [[ ! -f "$evidence/diagnostic-audit.json" ]]; then python3 "$cloud_dir/a1-isolated-test.py" audit "${common[@]}" --test-source "$test_source" > "$evidence/early-audit.log" 2>&1 || true; fi' EXIT
python3 "$cloud_dir/provider.py" > "$evidence/provider.json"
python3 - "$evidence/provider.json" <<'PROVIDER'
import json,sys
assert json.load(open(sys.argv[1]))['provider']=='cloud-build'
PROVIDER
{
  printf 'proof_sha=%s\n' "$(git -C "$proof_root" rev-parse HEAD)"
  printf 'production_source_head=%s\n' "$(git -C "$production_source" rev-parse HEAD)"
  printf 'deadline_epoch=%s\n' "$deadline_epoch"
  printf 'classification=A1_ISOLATED_TEST_DIAGNOSTIC_ONLY_NOT_ACCEPTED\n'
  printf 'mutation=outer_normal_assume_init_Move_37_to_Copy_37\n'
} > "$evidence/input-identity.txt"

remaining() {
  local seconds=$((deadline_epoch - $(date +%s) - 20))
  (( seconds > 0 )) || { printf 'A1 TEST deadline reached\n' >&2; exit 124; }
  printf '%s' "$seconds"
}
stage() {
  local name=$1; shift
  local budget code=0
  budget=$(remaining)
  /usr/bin/time -v -o "$evidence/$name-resources.txt" \
    timeout --signal=TERM --kill-after=10s "${budget}s" "$@" \
    > "$evidence/$name.log" 2>&1 || code=$?
  printf '%s\n' "$code" > "$evidence/$name-exit-code.txt"
  cat "$evidence/$name.log"
  return "$code"
}
script="$cloud_dir/a1-isolated-test.py"
stage production-snapshot python3 "$script" snapshot "${common[@]}"
stage canonical-pair-and-synthetic-probe python3 "$script" capture "${common[@]}"
stage synthetic-owner17-delta python3 "$script" delta "${common[@]}"
stage test-source-copy cp -a "$production_source" "$test_source"
git -C "$test_source" diff --binary HEAD > "$evidence/test-before.patch"
cmp "$production_patch" "$evidence/test-before.patch"
stage test-delta-check git -C "$test_source" apply --check "$evidence/test-owner17-delta.patch"
stage test-delta-apply git -C "$test_source" apply "$evidence/test-owner17-delta.patch"
stage test-delta-verify python3 "$script" verify-delta "${common[@]}" --test-source "$test_source"
cp "$test_source/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml" "$evidence/test-translator.ml"
git -C "$test_source" diff --binary HEAD > "$evidence/test-applied.patch"

deps_home="$work_root/vfdeps-adf88dc"
[[ -d "$deps_home/bin" && -d "$deps_home/include" && -d "$deps_home/lib" ]] || {
  printf 'A1 TEST requires existing vfdeps\n' >&2; exit 2;
}
export PATH="$deps_home/bin:$PATH"
export CAPNP_INC_DIR="$deps_home/include"
export RUSTUP_TOOLCHAIN=nightly-2026-09-25
export LD_LIBRARY_PATH="$compiler_sysroot/lib:$test_source/bin:$deps_home/lib:${LD_LIBRARY_PATH:-}"
for tool in make capnp capnpc-ocaml-decoder rustc; do
  command -v "$tool" >/dev/null || { printf 'A1 TEST dependency missing: %s\n' "$tool" >&2; exit 2; }
done
[[ "$(rustc --print sysroot)" == "$compiler_sysroot" ]] || exit 2
(( $(remaining) >= 60 )) || { printf 'Insufficient A1 TEST build time\n' >&2; exit 124; }
rm "$test_source/bin/verifast"
stage test-console-build make -C "$test_source/src" ../bin/verifast WITHOUT_LABLGTK=yes VERBOSE=yes
[[ -f "$test_source/bin/verifast" ]] || exit 2
ldd "$test_source/bin/verifast" > "$evidence/test-console-ldd.txt"
! rg -q 'not found' "$evidence/test-console-ldd.txt"
[[ "$(sha256sum "$test_source/bin/verifast" | cut -d' ' -f1)" != "$(sha256sum "$production_source/bin/verifast" | cut -d' ' -f1)" ]] || exit 2
stage test-a1-negative python3 "$script" test "${common[@]}" --test-source "$test_source"
stage a1-audit python3 "$script" audit "${common[@]}" --test-source "$test_source"
printf '%s\n' 'A1_ISOLATED_TEST_DIAGNOSTIC_ONLY_NOT_ACCEPTED' > "$evidence/PROFILE-STATUS.txt"
