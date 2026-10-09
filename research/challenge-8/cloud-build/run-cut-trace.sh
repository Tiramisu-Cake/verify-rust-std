#!/usr/bin/env bash
# Cloud-only, single-case, unaccepted strict CUT entry diagnostic.
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
    *) printf 'Unknown CUT TRACE argument: %s\n' "$1" >&2; exit 2 ;;
  esac
done
for path in "$production_source" "$production_patch" "$stock_home" "$compiler_sysroot" "$evidence" "$proof_root" "$work_root" "$cloud_dir"; do
  [[ -n "$path" ]] || { printf 'CUT TRACE requires all nine arguments\n' >&2; exit 2; }
done
[[ "$deadline_epoch" =~ ^[0-9]+$ ]] || exit 2
[[ "${SMALLSORT_EXECUTION_PROVIDER:-}" == cloud-build && -z "${GITHUB_ACTIONS:-}" ]] || exit 2
for path in "$production_source" "$stock_home" "$compiler_sysroot" "$evidence" "$proof_root" "$work_root" "$cloud_dir"; do
  [[ "$path" == /workspace/* && "$path" != *'/../'* && "$path" != *'/./'* ]] || {
    printf 'CUT TRACE path outside /workspace: %s\n' "$path" >&2; exit 2;
  }
done
[[ "$production_patch" == /workspace/* ]] || exit 2
[[ -d "$production_source/.git" && -f "$production_patch" && -f "$production_source/bin/verifast" ]] || exit 2
[[ -f "$stock_home/bin/vf-rust-mir-exporter" && -d "$compiler_sysroot/lib" ]] || exit 2
[[ -d "$proof_root/.git" && -f "$cloud_dir/provider.py" ]] || exit 2
[[ ! -e "$evidence" ]] || { printf 'CUT TRACE evidence exists: %s\n' "$evidence" >&2; exit 2; }
required_proof_files=(
  research/challenge-8/overnight-lifetime/capture.py
  research/challenge-8/overnight-lifetime/cases.rs
  research/challenge-8/overnight-lifetime/verifast-strict-lft-cut-26.10.patch
  research/challenge-8/overnight-lifetime/verifast-strict-cut-entry-trace-TESTONLY.patch
)
for relative in "${required_proof_files[@]}"; do
  [[ -f "$proof_root/$relative" ]] || {
    printf 'CUT TRACE requires proof file: %s\n' "$relative" >&2; exit 2;
  }
done
for relative in cut-trace-audit.py cut-trace-provider-overlay.py provider.py; do
  [[ -f "$cloud_dir/$relative" ]] || {
    printf 'CUT TRACE requires infrastructure file: %s\n' "$relative" >&2; exit 2;
  }
done
mkdir -p "$evidence"
for relative in "${required_proof_files[@]}"; do
  sha256sum "$proof_root/$relative"
done > "$evidence/required-proof-files-sha256.txt"
{
  printf 'proof_sha=%s\n' "$(git -C "$proof_root" rev-parse HEAD)"
  printf 'production_source_head=%s\n' "$(git -C "$production_source" rev-parse HEAD)"
  printf 'deadline_epoch=%s\n' "$deadline_epoch"
  printf 'profile=STRICT_CUT_TRACE_DIAGNOSTIC_ONLY_NOT_ACCEPTED\n'
  printf 'fixture=positive_f_bound\n'
  printf 'normal_and_unwind_post=thread/type resources, both T cells/owners, comparator F cell/owner\n'
} > "$evidence/input-identity.txt"

# The production console has already been built by the caller. Source, specs,
# tool binaries and its exact applied patch are snapshotted before any copy.
git -C "$production_source" diff --binary HEAD > "$evidence/production-before.patch"
cmp "$production_patch" "$evidence/production-before.patch"
python3 "$cloud_dir/cut-trace-audit.py" snapshot \
  --production-source "$production_source" --output "$evidence/production-snapshot.json"
python3 "$cloud_dir/provider.py" > "$evidence/provider.json"
python3 - "$evidence/provider.json" <<'PROVIDER'
import json,sys
assert json.load(open(sys.argv[1]))['provider']=='cloud-build'
PROVIDER

cut_patch="$proof_root/research/challenge-8/overnight-lifetime/verifast-strict-lft-cut-26.10.patch"
trace_patch="$proof_root/research/challenge-8/overnight-lifetime/verifast-strict-cut-entry-trace-TESTONLY.patch"
printf '%s  %s\n' d557082b0c17771acd7386ad6caca7bc139877cf1ca513d9570da210b1b542d8 "$cut_patch" | sha256sum -c -
printf '%s  %s\n' bc129b381af7bfe8cd5ca56eef099d90312ad7695dbbf852864d0e28148a4c3b "$trace_patch" | sha256sum -c -
cut_source="$work_root/cut-trace-isolated-source"
[[ ! -e "$cut_source" ]] || { printf 'CUT TRACE isolated source exists: %s\n' "$cut_source" >&2; exit 2; }
mkdir -p "$work_root"

remaining() {
  local seconds=$((deadline_epoch - $(date +%s) - 30))
  (( seconds > 0 )) || { printf 'CUT TRACE deadline reached\n' >&2; exit 124; }
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

stage source-copy cp -a "$production_source" "$cut_source"
git -C "$cut_source" diff --binary HEAD > "$evidence/cut-before.patch"
cmp "$evidence/production-before.patch" "$evidence/cut-before.patch"
cmp "$production_source/bin/verifast" "$cut_source/bin/verifast"
stage cut-check git -C "$cut_source" apply --check "$cut_patch"
stage cut-apply git -C "$cut_source" apply "$cut_patch"
cp "$cut_source/src/verifast.ml" "$evidence/cut-verifast-before-trace.ml"
stage trace-check git -C "$cut_source" apply --check "$trace_patch"
stage trace-apply git -C "$cut_source" apply "$trace_patch"
git -C "$cut_source" diff --binary HEAD > "$evidence/trace-applied.patch"

# Reuse dependencies installed earlier in this same Cloud build. No package,
# network or compiler-tool installation is performed by this helper.
deps_home="$work_root/vfdeps-adf88dc"
[[ -d "$deps_home/bin" && -d "$deps_home/include" && -d "$deps_home/lib" ]] || {
  printf 'CUT TRACE requires existing vfdeps at %s\n' "$deps_home" >&2; exit 2;
}
export PATH="$deps_home/bin:$PATH"
export CAPNP_INC_DIR="$deps_home/include"
export RUSTUP_TOOLCHAIN=nightly-2026-09-25
export LD_LIBRARY_PATH="$compiler_sysroot/lib:$cut_source/bin:$deps_home/lib:${LD_LIBRARY_PATH:-}"
for tool in make capnp capnpc-ocaml-decoder rustc; do
  command -v "$tool" >/dev/null || { printf 'CUT TRACE dependency missing: %s\n' "$tool" >&2; exit 2; }
done
[[ "$(rustc --print sysroot)" == "$compiler_sysroot" ]] || exit 2
(( $(remaining) >= 60 )) || { printf 'Insufficient CUT TRACE build time\n' >&2; exit 124; }
rm "$cut_source/bin/verifast"
stage trace-console-build make -C "$cut_source/src" ../bin/verifast WITHOUT_LABLGTK=yes VERBOSE=yes
[[ -f "$cut_source/bin/verifast" ]] || exit 2
[[ "$(sha256sum "$cut_source/bin/verifast" | cut -d' ' -f1)" != "$(sha256sum "$production_source/bin/verifast" | cut -d' ' -f1)" ]] || exit 2
ldd "$cut_source/bin/verifast" > "$evidence/trace-console-ldd.txt"
! rg -q 'not found' "$evidence/trace-console-ldd.txt"
python3 "$cloud_dir/cut-trace-audit.py" compare \
  --production-source "$production_source" --snapshot "$evidence/production-snapshot.json" \
  --cut-source "$cut_source" --stock-home "$stock_home" \
  --before-trace "$evidence/cut-verifast-before-trace.ml" \
  --output "$evidence/source-audit.json"

# Only this disposable proof checkout receives the provider guard adaptation.
stage capture-provider-overlay python3 "$cloud_dir/cut-trace-provider-overlay.py" \
  --proof-root "$proof_root" --cloud-dir "$cloud_dir" --evidence "$evidence"
export SMALLSORT_CLOUD_PROVIDER_PATH="$cloud_dir/provider.py"
export SORT4_STRICT_LFT_TRACE=1
capture="$proof_root/research/challenge-8/overnight-lifetime/capture.py"
raw_capture_exit=0
stage positive-f-bound python3 "$capture" --case positive_f_bound \
  --tool-home "$cut_source" --out "$evidence/positive-f-bound" \
  --deadline-epoch "$deadline_epoch" || raw_capture_exit=$?
printf '%s\n' "$raw_capture_exit" > "$evidence/raw-capture-exit-code.txt"
python3 "$cloud_dir/cut-trace-audit.py" classify \
  --production-source "$production_source" --snapshot "$evidence/production-snapshot.json" \
  --cut-source "$cut_source" --stock-home "$stock_home" \
  --before-trace "$evidence/cut-verifast-before-trace.ml" \
  --capture "$evidence/positive-f-bound" --raw-exit "$raw_capture_exit" \
  --output "$evidence/diagnostic-audit.json"
git -C "$production_source" diff --binary HEAD > "$evidence/production-after.patch"
cmp "$production_patch" "$evidence/production-after.patch"
printf '%s\n' 'CUT_TRACE_DIAGNOSTIC_ONLY_NOT_ACCEPTED' > "$evidence/PROFILE-STATUS.txt"
