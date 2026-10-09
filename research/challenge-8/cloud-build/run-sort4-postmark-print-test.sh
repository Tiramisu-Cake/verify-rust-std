#!/usr/bin/env bash
# Cloud-only isolated verifier-core print TEST; never an accepted proof profile.
set -euo pipefail

production_source= production_patch= stock_home= compiler_sysroot=
evidence= deadline_epoch= proof_root= work_root= cloud_dir=
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
    *) printf 'Unknown post-mark print TEST argument: %s\n' "$1" >&2; exit 2 ;;
  esac
done
for path in "$production_source" "$production_patch" "$stock_home" \
  "$compiler_sysroot" "$evidence" "$proof_root" "$work_root" "$cloud_dir"; do
  [[ "$path" == /workspace/* && "$path" != *'/../'* && "$path" != *'/./'* ]] || exit 2
done
[[ "$deadline_epoch" =~ ^[0-9]+$ ]] || exit 2
[[ "${SMALLSORT_EXECUTION_PROVIDER:-}" == cloud-build && -z "${GITHUB_ACTIONS:-}" ]] || exit 2
[[ "${SORT4_ACTUAL_AST_SCOPE_TEST:-0}" != 1 &&
   "${SORT4_AST_SCOPE_PROBE:-0}" != 1 &&
   "${SORT4_HRTB_OUTPUT:-0}" != 1 &&
   "${SORT4_HRTB_OUTPUT_TARGETS:-0}" != 1 &&
   "${SORT4_STRICT_LFT_CUT:-0}" != 1 &&
   "${SORT4_CALLBACK_UNWIND:-0}" != 1 ]] || exit 2
[[ -d "$production_source/.git" && -f "$production_source/bin/verifast" &&
   -d "$proof_root/.git" && -f "$production_patch" && -d "$stock_home/bin" &&
   -d "$compiler_sysroot/lib" && -f "$cloud_dir/provider.py" &&
   ! -e "$evidence" ]] || exit 2

translator=src/rust_frontend/vf_mir_translator/vf_mir_translator.ml
profile_sha=0862e635075edd06a827c567710a3e1125ac03aa122e95149db755a1fddce48a
[[ "$(sha256sum "$production_source/$translator" | cut -d' ' -f1)" == "$profile_sha" ]] || exit 2
verifast_ml=src/verifast.ml
stock_verifast_ml_sha=adbf2c3de02cba7fbdb0b8e203a864e34c1b2ab16de4f6b153477106dbba04d0
test_verifast_ml_sha=de821f944772683239d4fb7115e9602aa6fcf0cdb3be598f235ba7580a81417b
[[ "$(sha256sum "$production_source/$verifast_ml" | cut -d' ' -f1)" == "$stock_verifast_ml_sha" ]] || exit 2
schema="$production_source/src/rust_frontend/vf_mir/vf_mir.capnp"
[[ -f "$schema" ]] || exit 2
patch="$proof_root/research/challenge-8/overnight-callback/verifast-actual-sort4-postmark-print-TEST.patch"
card="$proof_root/research/challenge-8/overnight-callback/CLOUD-ACTUAL-SORT4-POSTMARK-PRINT-TEST-CARD.md"
manifest="$proof_root/research/challenge-8/overnight-callback/ACTUAL-SORT4-POSTMARK-PRINT-TEST.json"
capture="$cloud_dir/actual-sort4-capture.py"
audit="$cloud_dir/sort4-postmark-print-audit.py"
prior_audit="$cloud_dir/sort4-ast-audit.py"
for file in "$patch" "$card" "$manifest" "$capture" "$audit" "$prior_audit"; do [[ -f "$file" ]] || exit 2; done
patch_sha=57c271e5db2c72d69162a16fec10d975cd68fd7619a02ca54aa80a58426d3c6d
printf '%s  %s\n' "$patch_sha" "$patch" | sha256sum -c -
python3 - "$patch" "$verifast_ml" "$manifest" "$patch_sha" <<'PATCH_SCOPE'
from pathlib import Path
import json,sys
lines = Path(sys.argv[1]).read_text().splitlines()
path = sys.argv[2]
assert [row for row in lines if row.startswith('--- ')] == ['--- a/' + path]
assert [row for row in lines if row.startswith('+++ ')] == ['+++ b/' + path]
manifest=json.loads(Path(sys.argv[3]).read_text())
assert manifest['patch_sha256']==sys.argv[4]
assert manifest['accepted'] is False and manifest['kernel_operations_changed'] is False
PATCH_SCOPE
mkdir -p "$evidence"
python3 "$cloud_dir/provider.py" > "$evidence/provider.json"
python3 - "$evidence/provider.json" <<'PROVIDER'
import json,sys
assert json.load(open(sys.argv[1]))['provider']=='cloud-build'
PROVIDER
git -C "$production_source" diff --binary HEAD > "$evidence/production-before.patch"
cmp "$production_patch" "$evidence/production-before.patch"
sha256sum "$patch" "$card" "$manifest" "$capture" "$audit" "$prior_audit" > "$evidence/inputs-sha256.txt"
{
  printf 'proof_sha=%s\n' "$(git -C "$proof_root" rev-parse HEAD)"
  printf 'production_head=%s\n' "$(git -C "$production_source" rev-parse HEAD)"
  printf 'production_translator_sha256=%s\n' "$profile_sha"
  printf 'production_verifast_ml_sha256=%s\n' "$stock_verifast_ml_sha"
  printf 'test_verifast_ml_sha256=%s\n' "$test_verifast_ml_sha"
  printf 'probe_patch_sha256=%s\n' "$patch_sha"
  printf 'production_verifast_sha256=%s\n' "$(sha256sum "$production_source/bin/verifast" | cut -d' ' -f1)"
  printf 'stock_verifast_sha256=%s\n' "$(sha256sum "$stock_home/bin/verifast" | cut -d' ' -f1)"
  printf 'schema_sha256=%s\n' "$(sha256sum "$schema" | cut -d' ' -f1)"
  printf 'profile=PRINT_ONLY_ACTUAL_SORT4_POSTMARK_TEST_NOT_ACCEPTED\n'
} > "$evidence/input-identity.txt"

remaining() {
  local seconds=$((deadline_epoch - $(date +%s) - 30))
  (( seconds > 0 )) || return 124
  printf '%s' "$seconds"
}
stage() {
  local name=$1; shift
  local seconds code=0
  seconds=$(remaining) || return 124
  /usr/bin/time -v -o "$evidence/$name-resources.txt" \
    timeout --signal=TERM --kill-after=10s "${seconds}s" "$@" \
    > "$evidence/$name.log" 2>&1 || code=$?
  printf '%s\n' "$code" > "$evidence/$name-exit-code.txt"
  return "$code"
}

# The baseline captures the same O24 source, paired complete typed MIR,
# candidate first-call CFG audit, refinement and stock reserved-marker refusal.
unset SORT4_POSTMARK_TEST SORT4_POSTMARK_TEST_DIR \
  SORT4_ACTUAL_AST_SCOPE_TEST SORT4_AST_SCOPE_PROBE SORT4_AST_SCOPE_PROBE_DIR \
  SORT4_HRTB_OUTPUT SORT4_HRTB_OUTPUT_TARGETS SORT4_STRICT_LFT_CUT \
  SORT4_CALLBACK_UNWIND
stage baseline python3 "$capture" --proof-root "$proof_root" \
  --cloud-dir "$cloud_dir" --tool-home "$production_source" \
  --schema "$schema" --compiler-sysroot "$compiler_sysroot" \
  --evidence "$evidence/baseline" --deadline-epoch "$deadline_epoch"
python3 "$audit" preflight --baseline "$evidence/baseline" \
  --output "$evidence/preflight.json"

probe_source="$work_root/sort4-postmark-print-test-isolated-source"
[[ ! -e "$probe_source" ]] || exit 2
stage source-copy cp -a "$production_source" "$probe_source"
cmp "$production_source/bin/verifast" "$probe_source/bin/verifast"
cmp "$production_source/src/verifast.ml" "$probe_source/src/verifast.ml"
stage probe-patch-check git -C "$probe_source" apply --check "$patch"
stage probe-patch-apply git -C "$probe_source" apply "$patch"
[[ "$(sha256sum "$probe_source/$verifast_ml" | cut -d' ' -f1)" == "$test_verifast_ml_sha" ]] || exit 2
cmp "$production_source/$translator" "$probe_source/$translator"
cmp "$production_source/src/rust_frontend/vf_mir/vf_mir.capnp" "$probe_source/src/rust_frontend/vf_mir/vf_mir.capnp"
python3 - "$production_source" "$probe_source" <<'ONLY_CORE_PRINT'
import pathlib,subprocess,sys
production,probe=map(pathlib.Path,sys.argv[1:])
def changed(root):
    return set(subprocess.check_output(['git','-C',str(root),'diff','--name-only','HEAD'],text=True).splitlines())
assert 'src/verifast.ml' not in changed(production)
assert changed(probe)==changed(production)|{'src/verifast.ml'}
ONLY_CORE_PRINT
git -C "$probe_source" diff --binary HEAD > "$evidence/probe-applied.patch"

# Reuse dependencies already installed by the production Cloud build.
deps_home="$work_root/vfdeps-adf88dc"
[[ -d "$deps_home/bin" && -d "$deps_home/include" && -d "$deps_home/lib" ]] || exit 2
export PATH="$deps_home/bin:$PATH"
export CAPNP_INC_DIR="$deps_home/include"
export RUSTUP_TOOLCHAIN=nightly-2026-09-25
export LD_LIBRARY_PATH="$compiler_sysroot/lib:$probe_source/bin:$deps_home/lib:${LD_LIBRARY_PATH:-}"
[[ "$(rustc --print sysroot)" == "$compiler_sysroot" ]] || exit 2
rm "$probe_source/bin/verifast"
stage probe-console-build make -C "$probe_source/src" ../bin/verifast \
  WITHOUT_LABLGTK=yes VERBOSE=yes
[[ -f "$probe_source/bin/verifast" ]] || exit 2
[[ "$(sha256sum "$probe_source/bin/verifast" | cut -d' ' -f1)" != \
   "$(sha256sum "$production_source/bin/verifast" | cut -d' ' -f1)" ]] || exit 2
sha256sum "$probe_source/bin/verifast" > "$evidence/probe-verifast-sha256.txt"
sha256sum "$production_source/bin/verifast" > "$evidence/production-verifast-sha256.txt"
ldd "$probe_source/bin/verifast" > "$evidence/probe-console-ldd.txt"
! rg -q 'not found' "$evidence/probe-console-ldd.txt"

fixture="$evidence/baseline/actual-sort4-fixture"
[[ -f "$fixture/verified/lib.rs" ]] || exit 2
mkdir "$evidence/probe-off-output"
export SORT4_POSTMARK_TEST=0
export SORT4_POSTMARK_TEST_DIR="$evidence/probe-off-output"
stage probe-off-full-verification bash -c \
  'cd "$1" && "$2" -rustc_args "--edition 2021" -verbose 1 verified/lib.rs' \
  bash "$fixture" "$probe_source/bin/verifast" || true
unset SORT4_POSTMARK_TEST SORT4_POSTMARK_TEST_DIR
mkdir "$evidence/probe-output"
export SORT4_POSTMARK_TEST=1
export SORT4_POSTMARK_TEST_DIR="$evidence/probe-output"
stage probe-full-verification bash -c \
  'cd "$1" && "$2" -rustc_args "--edition 2021" -verbose 1 verified/lib.rs' \
  bash "$fixture" "$probe_source/bin/verifast" || true
unset SORT4_POSTMARK_TEST SORT4_POSTMARK_TEST_DIR
sha256sum -c "$evidence/probe-verifast-sha256.txt" > "$evidence/probe-verifast-integrity.txt"
sha256sum -c "$evidence/production-verifast-sha256.txt" > "$evidence/production-verifast-integrity.txt"
python3 "$audit" classify --baseline "$evidence/baseline" \
  --manifest "$manifest" \
  --probe-off-log "$evidence/probe-off-full-verification.log" \
  --probe-off-exit "$(cat "$evidence/probe-off-full-verification-exit-code.txt")" \
  --probe-off-output "$evidence/probe-off-output" \
  --probe-log "$evidence/probe-full-verification.log" \
  --probe-exit "$(cat "$evidence/probe-full-verification-exit-code.txt")" \
  --probe-output "$evidence/probe-output" \
  --production-source "$production_source" --probe-source "$probe_source" \
  --output "$evidence/sort4-postmark-result.json"
git -C "$production_source" diff --binary HEAD > "$evidence/production-after.patch"
cmp "$production_patch" "$evidence/production-after.patch"
printf 'PRINT_ONLY_ACTUAL_SORT4_POSTMARK_TEST_NOT_ACCEPTED\n' > "$evidence/PROFILE-STATUS.txt"
