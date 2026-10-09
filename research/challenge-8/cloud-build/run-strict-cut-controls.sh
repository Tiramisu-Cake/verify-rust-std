#!/usr/bin/env bash
# Cloud-only discovery controls against the already-built isolated strictCUT tool.
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
relocation_evidence=
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
    *) printf 'Unknown strictCUT controls argument: %s\n' "$1" >&2; exit 2 ;;
  esac
done
for path in "$production_source" "$production_patch" "$stock_home" "$compiler_sysroot" \
            "$evidence" "$proof_root" "$work_root" "$cloud_dir" "$relocation_evidence"; do
  [[ -n "$path" && "$path" == /workspace/* && "$path" != *'/../'* && "$path" != *'/./'* ]] || {
    printf 'strictCUT controls require absolute /workspace inputs: %s\n' "$path" >&2; exit 2;
  }
done
[[ "$deadline_epoch" =~ ^[0-9]+$ ]] || exit 2
[[ "${SMALLSORT_EXECUTION_PROVIDER:-}" == cloud-build && -z "${GITHUB_ACTIONS:-}" ]] || exit 2
[[ -d "$production_source/.git" && -d "$proof_root/.git" && -f "$production_patch" ]] || exit 2
[[ -f "$cloud_dir/provider.py" && -d "$compiler_sysroot/lib" ]] || exit 2
[[ ! -e "$evidence" ]] || { printf 'strictCUT controls evidence exists: %s\n' "$evidence" >&2; exit 2; }
relocation_source="$work_root/cut-relocation-isolated-source"
[[ -d "$relocation_source/.git" && -f "$relocation_source/bin/verifast" ]] || exit 2
[[ -f "$relocation_evidence/diagnostic-audit.json" ]] || exit 2
for relative in cut-relocate-audit.py cut-trace-provider-overlay.py \
                strict-cut-controls-audit.py provider.py; do
  [[ -f "$cloud_dir/$relative" ]] || exit 2
done
for relative in capture.py cases.rs verifast-strict-lft-cut-26.10.patch \
                verifast-cut-relocate-callback-TESTONLY.patch \
                verifast-cut-relocate-translated-ids-TEST.patch; do
  [[ -f "$proof_root/research/challenge-8/overnight-lifetime/$relative" ]] || exit 2
done

mkdir -p "$evidence/cases"
{
  printf 'profile=STRICT_CUT_CONTROLS_DISCOVERY_ONLY_NOT_ACCEPTED\n'
  printf 'proof_sha=%s\n' "$(git -C "$proof_root" rev-parse HEAD)"
  printf 'production_source_head=%s\n' "$(git -C "$production_source" rev-parse HEAD)"
  printf 'relocation_source_head=%s\n' "$(git -C "$relocation_source" rev-parse HEAD)"
  printf 'relocation_evidence=%s\n' "$relocation_evidence"
  printf 'deadline_epoch=%s\n' "$deadline_epoch"
  printf 'old_positive_f_bound=skipped;distinct_same_build_relocated_callback_required\n'
  printf 'all_negative_outcomes=candidates_for_full_source_MIR_log_review\n'
} > "$evidence/input-identity.txt"
for relative in capture.py cases.rs verifast-strict-lft-cut-26.10.patch \
                verifast-cut-relocate-callback-TESTONLY.patch \
                verifast-cut-relocate-translated-ids-TEST.patch; do
  sha256sum "$proof_root/research/challenge-8/overnight-lifetime/$relative"
done > "$evidence/required-proof-files-sha256.txt"
for relative in cut-relocate-audit.py cut-trace-provider-overlay.py \
                strict-cut-controls-audit.py provider.py; do
  sha256sum "$cloud_dir/$relative"
done > "$evidence/required-infrastructure-files-sha256.txt"

audit_args=(
  --production-source "$production_source"
  --production-applied-patch "$production_patch"
  --stock-home "$stock_home"
  --relocation-source "$relocation_source"
  --relocation-evidence "$relocation_evidence"
  --proof-root "$proof_root"
  --cloud-dir "$cloud_dir"
  --evidence "$evidence"
)
python3 "$cloud_dir/provider.py" > "$evidence/provider.json"
python3 - "$evidence/provider.json" <<'PROVIDER'
import json, sys
assert json.load(open(sys.argv[1]))["provider"] == "cloud-build"
PROVIDER
python3 "$cloud_dir/strict-cut-controls-audit.py" preflight \
  "${audit_args[@]}" --output "$evidence/preflight-audit.json"
python3 "$cloud_dir/cut-trace-provider-overlay.py" \
  --proof-root "$proof_root" --cloud-dir "$cloud_dir" --evidence "$evidence"

deps_home="$work_root/vfdeps-adf88dc"
[[ -d "$deps_home/bin" && -d "$deps_home/include" && -d "$deps_home/lib" ]] || exit 2
export PATH="$deps_home/bin:$relocation_source/bin:$PATH"
export CAPNP_INC_DIR="$deps_home/include"
export LD_LIBRARY_PATH="$compiler_sysroot/lib:$relocation_source/bin:$deps_home/lib:${LD_LIBRARY_PATH:-}"
export RUSTUP_TOOLCHAIN=nightly-2026-09-25
export SMALLSORT_CLOUD_PROVIDER_PATH="$cloud_dir/provider.py"
unset SORT4_STRICT_LFT_TRACE SORT4_STRICT_LFT_RELOCATE SORT4_HRTB_OUTPUT SORT4_HRTB_OUTPUT_TARGETS
for tool in capnp rustc; do
  command -v "$tool" >/dev/null || { printf 'Missing dependency: %s\n' "$tool" >&2; exit 2; }
done
[[ "$(rustc --print sysroot)" == "$compiler_sysroot" ]] || exit 2

capture="$proof_root/research/challenge-8/overnight-lifetime/capture.py"
cases=(positive_basic ordinary_unmarked positive_early_return positive_direct_unwind
       negative_wrong_marker negative_duplicate_marker negative_marker_outside_binding
       negative_unknown_binding negative_nested_marker negative_malformed_marker
       negative_type_name_after_cut negative_type_argument_after_cut
       negative_typed_chunk_survives_cut negative_unclosed_fractional_access
       negative_reserved_half_after_lifetime_end negative_end_lifetime_twice)
run_case() {
  local key=$1 case=$2 extra=$3 budget code=0
  budget=$((deadline_epoch - $(date +%s) - 30))
  if ((budget <= 0)); then
    code=124
    printf 'strictCUT controls deadline before %s\n' "$key" > "$evidence/capture-$key.log"
  else
    local args=(--tool-home "$relocation_source" --out "$evidence/cases/$key"
                --deadline-epoch "$deadline_epoch" --case "$case")
    [[ "$extra" == none ]] || args+=(--without-opt-in)
    /usr/bin/time -v -o "$evidence/capture-$key-resources.txt" \
      timeout --signal=TERM --kill-after=10s "${budget}s" \
      python3 "$capture" "${args[@]}" \
      > "$evidence/capture-$key.log" 2>&1 || code=$?
  fi
  printf '%s\n' "$code" > "$evidence/capture-$key-exit-code.txt"
  printf 'strictCUT control %s exit=%s\n' "$key" "$code"
}
for case in "${cases[@]}"; do
  run_case "$case" "$case" none
done
run_case opt-in-absent positive_basic off

python3 - "$evidence" "${cases[@]}" <<'CAPTURE_EXITS'
import json
from pathlib import Path
import sys
root = Path(sys.argv[1])
keys = [*sys.argv[2:], "opt-in-absent"]
codes = {key: int((root / f"capture-{key}-exit-code.txt").read_text()) for key in keys}
(root / "capture-exits.json").write_text(json.dumps(codes, indent=2, sort_keys=True) + "\n")
CAPTURE_EXITS
python3 "$cloud_dir/strict-cut-controls-audit.py" final \
  "${audit_args[@]}" --output "$evidence/diagnostic-audit.json"
printf '%s\n' 'STRICT_CUT_CONTROLS_DISCOVERY_ONLY_NOT_ACCEPTED' > "$evidence/PROFILE-STATUS.txt"
