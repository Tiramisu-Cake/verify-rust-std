#!/usr/bin/env bash
# Blocked-by-review, Cloud-only actual-sort4 first-scope TEST diagnostic.
set -euo pipefail

production_source= production_patch= stock_home= compiler_sysroot=
evidence= deadline_epoch= proof_root= work_root= cloud_dir=
relocation_evidence= controls_evidence= false_posts_evidence=
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
    --relocation-evidence) relocation_evidence=$2; shift 2 ;;
    --controls-evidence) controls_evidence=$2; shift 2 ;;
    --false-posts-evidence) false_posts_evidence=$2; shift 2 ;;
    *) printf 'Unknown first-scope argument: %s\n' "$1" >&2; exit 2 ;;
  esac
done
for path in "$production_source" "$production_patch" "$stock_home" \
            "$compiler_sysroot" "$evidence" "$proof_root" "$work_root" \
            "$cloud_dir" "$relocation_evidence" "$controls_evidence" \
            "$false_posts_evidence"; do
  [[ -n "$path" && "$path" == /workspace/* &&
     "$path" != *'/../'* && "$path" != *'/./'* ]] || exit 2
done
[[ "$deadline_epoch" =~ ^[0-9]+$ ]] || exit 2
[[ "${SMALLSORT_EXECUTION_PROVIDER:-}" == cloud-build &&
   -z "${GITHUB_ACTIONS:-}" ]] || exit 2
[[ -d "$proof_root/.git" && -d "$production_source/.git" &&
   -f "$production_patch" && -f "$cloud_dir/provider.py" &&
   -d "$stock_home/bin" && -d "$compiler_sysroot/lib" &&
   ! -e "$evidence" ]] || exit 2
base_source="$work_root/cut-relocation-isolated-source"
test_source="$work_root/sort4-first-scope-isolated-source"
[[ -d "$base_source/.git" && -f "$base_source/bin/verifast" &&
   ! -e "$test_source" ]] || exit 2
[[ "$(git -C "$proof_root" rev-parse HEAD)" == "${PROOF_SHA:?}" ]] || exit 2
for relative in sort4-first-scope-audit.py sort4-ast-audit.py \
                strict-cut-controls-audit.py strict-cut-false-posts-audit.py \
                actual-sort4-capture.py provider.py; do
  [[ -f "$cloud_dir/$relative" ]] || exit 2
done
patch="$proof_root/research/challenge-8/overnight-callback/verifast-actual-sort4-first-scope-TEST.patch"
manifest="$proof_root/research/challenge-8/overnight-callback/ACTUAL-SORT4-AST-SCOPE-TEST.json"
[[ -f "$patch" && -f "$manifest" ]] || exit 2
mkdir -p "$evidence"
printf '%s\n' BLOCKED_UNTIL_REVIEW > "$evidence/PROFILE-STATUS.txt"
python3 "$cloud_dir/provider.py" > "$evidence/provider.json"
audit="$cloud_dir/sort4-first-scope-audit.py"
common=(--production-source "$production_source"
        --production-applied-patch "$production_patch"
        --stock-home "$stock_home" --compiler-sysroot "$compiler_sysroot"
        --evidence "$evidence" --deadline-epoch "$deadline_epoch"
        --proof-root "$proof_root" --work-root "$work_root"
        --cloud-dir "$cloud_dir" --relocation-evidence "$relocation_evidence"
        --controls-evidence "$controls_evidence"
        --false-posts-evidence "$false_posts_evidence")
remaining() {
  local seconds=$((deadline_epoch - $(date +%s) - 30))
  (( seconds > 0 )) || return 124
  printf '%s' "$seconds"
}
stage() {
  local name=$1; shift
  local budget code=0
  budget=$(remaining) || return 124
  /usr/bin/time -v -o "$evidence/$name-resources.txt" \
    timeout --signal=TERM --kill-after=10s "${budget}s" "$@" \
    > "$evidence/$name.log" 2>&1 || code=$?
  printf '%s\n' "$code" > "$evidence/$name-exit-code.txt"
  return "$code"
}

# The committed manifest remains BLOCKED until the raw strict-control/MIR/storage
# review is recorded. No copy, build, or verifier precedes it.
stage review-preflight python3 "$audit" preflight "${common[@]}" \
  --output "$evidence/preflight.json"
printf '%s\n' FIRST_SCOPE_REVIEWED_TEST_ONLY_NOT_ACCEPTED > "$evidence/PROFILE-STATUS.txt"
git -C "$production_source" diff --binary HEAD > "$evidence/production-before.patch"
cmp "$production_patch" "$evidence/production-before.patch"
cp "$relocation_evidence/diagnostic-audit.json" "$evidence/prior-relocation-audit.json"
cp "$controls_evidence/diagnostic-audit.json" "$evidence/prior-controls-audit.json"
cp "$false_posts_evidence/diagnostic-audit.json" "$evidence/prior-false-posts-audit.json"
mkdir "$evidence/prior-raw-logs"
for key in normal-false unwind-false; do
  cp "$false_posts_evidence/cases/$key/full-verification.log" \
    "$evidence/prior-raw-logs/$key-full-verification.log"
done
sha256sum "$patch" "$manifest" "$audit" "$cloud_dir/actual-sort4-capture.py" \
  "$cloud_dir/strict-cut-controls-audit.py" \
  "$cloud_dir/strict-cut-false-posts-audit.py" \
  > "$evidence/inputs-sha256.txt"

# Recompute both reviewed control verdicts from same-Build raw artifacts.
stage prior-controls-reaudit python3 "$cloud_dir/strict-cut-controls-audit.py" final \
  --production-source "$production_source" \
  --production-applied-patch "$production_patch" --stock-home "$stock_home" \
  --relocation-source "$base_source" --relocation-evidence "$relocation_evidence" \
  --proof-root "$proof_root" --cloud-dir "$cloud_dir" \
  --evidence "$controls_evidence" --output "$evidence/recomputed-controls-audit.json"
cmp "$controls_evidence/diagnostic-audit.json" "$evidence/recomputed-controls-audit.json"
stage prior-false-posts-reaudit python3 "$cloud_dir/strict-cut-false-posts-audit.py" \
  --proof-root "$proof_root" --controls-evidence "$controls_evidence" \
  --evidence "$false_posts_evidence" --cloud-dir "$cloud_dir" \
  --output "$evidence/recomputed-false-posts-audit.json"
cmp "$false_posts_evidence/diagnostic-audit.json" "$evidence/recomputed-false-posts-audit.json"

deps_home="$work_root/vfdeps-adf88dc"
[[ -d "$deps_home/bin" && -d "$deps_home/include" &&
   -d "$deps_home/lib" ]] || exit 2
export PATH="$deps_home/bin:$base_source/bin:$PATH"
export CAPNP_INC_DIR="$deps_home/include"
export LD_LIBRARY_PATH="$compiler_sysroot/lib:$base_source/bin:$deps_home/lib:${LD_LIBRARY_PATH:-}"
export RUSTUP_TOOLCHAIN=nightly-2026-09-25
export SMALLSORT_CLOUD_PROVIDER_PATH="$cloud_dir/provider.py"
unset SORT4_ACTUAL_AST_SCOPE_TEST SORT4_AST_SCOPE_PROBE SORT4_AST_SCOPE_PROBE_DIR
unset SORT4_STRICT_LFT_TRACE SORT4_STRICT_LFT_RELOCATE SORT4_HRTB_OUTPUT SORT4_HRTB_OUTPUT_TARGETS
unset SORT4_STRICT_LFT_CUT SORT4_CALLBACK_UNWIND
for tool in make capnp rustc; do command -v "$tool" >/dev/null || exit 2; done
[[ "$(rustc --print sysroot)" == "$compiler_sysroot" ]] || exit 2

# Same-Build production-profile O24 source/MIR/refinement and original first
# reserved-marker refusal. The isolated strict CUT tool refuses its opt-in first.
stage actual-baseline env \
  LD_LIBRARY_PATH="$compiler_sysroot/lib:$production_source/bin:$deps_home/lib:${LD_LIBRARY_PATH:-}" \
  python3 "$cloud_dir/actual-sort4-capture.py" \
  --proof-root "$proof_root" --cloud-dir "$cloud_dir" \
  --tool-home "$production_source" \
  --schema "$production_source/src/rust_frontend/vf_mir/vf_mir.capnp" \
  --compiler-sysroot "$compiler_sysroot" --evidence "$evidence/baseline" \
  --deadline-epoch "$deadline_epoch"
stage baseline-check python3 "$audit" baseline "${common[@]}" \
  --output "$evidence/baseline-check.json"

stage test-source-copy cp -a "$base_source" "$test_source"
cmp "$base_source/bin/verifast" "$test_source/bin/verifast"
cmp "$base_source/src/verifast.ml" "$test_source/src/verifast.ml"
git -C "$base_source" diff --binary HEAD > "$evidence/base-isolated-applied.patch"
cmp "$evidence/base-isolated-applied.patch" \
  <(git -C "$test_source" diff --binary HEAD)
stage test-patch-check git -C "$test_source" apply --check "$patch"
stage test-patch-apply git -C "$test_source" apply "$patch"
cmp "$base_source/src/verifast.ml" "$test_source/src/verifast.ml"
sha256sum "$test_source/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml" \
  > "$evidence/test-patched-translator.sha256"
git -C "$test_source" diff --binary HEAD > "$evidence/test-isolated-applied.patch"
rm "$test_source/bin/verifast"
export PATH="$deps_home/bin:$test_source/bin:$PATH"
export LD_LIBRARY_PATH="$compiler_sysroot/lib:$test_source/bin:$deps_home/lib:${LD_LIBRARY_PATH:-}"
stage test-console-build make -C "$test_source/src" ../bin/verifast \
  WITHOUT_LABLGTK=yes VERBOSE=yes
[[ -f "$test_source/bin/verifast" ]] || exit 2
sha256sum -c "$evidence/test-patched-translator.sha256" \
  > "$evidence/test-patched-translator-after-build.txt"
ldd "$test_source/bin/verifast" > "$evidence/test-console-ldd.txt"
! rg -q 'not found' "$evidence/test-console-ldd.txt"
stage tool-check python3 "$audit" tool "${common[@]}" \
  --output "$evidence/tool-check.json"

# Every old strictCUT case is rerun under the new console with the actual-only
# branch disabled. No old negative is credited by a changed first error.
matrix="$evidence/new-tool-matrix"
mkdir -p "$matrix/cases"
capture="$proof_root/research/challenge-8/overnight-lifetime/capture.py"
for key in positive_basic ordinary_unmarked positive_early_return positive_direct_unwind \
           negative_wrong_marker negative_duplicate_marker negative_marker_outside_binding \
           negative_unknown_binding negative_nested_marker negative_malformed_marker \
           negative_type_name_after_cut negative_type_argument_after_cut \
           negative_typed_chunk_survives_cut negative_unclosed_fractional_access \
           negative_reserved_half_after_lifetime_end negative_end_lifetime_twice \
           opt-in-absent; do
  case_name=$key
  extra=()
  if [[ "$key" == opt-in-absent ]]; then
    case_name=positive_basic
    extra=(--without-opt-in)
  fi
  stage "new-tool-matrix/capture-$key" python3 "$capture" \
    --tool-home "$test_source" --out "$matrix/cases/$key" \
    --deadline-epoch "$deadline_epoch" --case "$case_name" "${extra[@]}"
done
stage new-tool-matrix-check python3 "$audit" matrix "${common[@]}" \
  --output "$evidence/new-tool-matrix-check.json"

fixture="$evidence/baseline/actual-sort4-fixture"
[[ -f "$fixture/verified/lib.rs" && -f "$fixture/original/lib.rs" ]] || exit 2
sha256sum "$fixture/verified/lib.rs" "$fixture/original/lib.rs" \
  > "$evidence/actual-source-before.sha256"
export SORT4_ACTUAL_AST_SCOPE_TEST=0
printf '%s\n' 'off: SORT4_ACTUAL_AST_SCOPE_TEST=0; SORT4_STRICT_LFT_CUT absent' \
  > "$evidence/actual-mode-env.txt"
stage test-off-full-verification bash -c \
  'cd "$1" && "$2" -rustc_args "--edition 2021" -verbose 1 verified/lib.rs' \
  bash "$fixture" "$test_source/bin/verifast" || true
export SORT4_ACTUAL_AST_SCOPE_TEST=1
export SORT4_STRICT_LFT_CUT=1
printf '%s\n' 'on: SORT4_ACTUAL_AST_SCOPE_TEST=1; SORT4_STRICT_LFT_CUT=1' \
  >> "$evidence/actual-mode-env.txt"
stage test-on-full-verification bash -c \
  'cd "$1" && "$2" -rustc_args "--edition 2021" -verbose 1 verified/lib.rs' \
  bash "$fixture" "$test_source/bin/verifast" || true
unset SORT4_ACTUAL_AST_SCOPE_TEST
unset SORT4_STRICT_LFT_CUT
sha256sum -c "$evidence/actual-source-before.sha256" \
  > "$evidence/actual-source-after-check.txt"
stage final-audit python3 "$audit" final "${common[@]}" \
  --output "$evidence/diagnostic-audit.json"
git -C "$production_source" diff --binary HEAD > "$evidence/production-after.patch"
cmp "$production_patch" "$evidence/production-after.patch"
printf '%s\n' FIRST_SCOPE_TEST_DIAGNOSTIC_ONLY_NOT_ACCEPTED \
  > "$evidence/PROFILE-STATUS.txt"
