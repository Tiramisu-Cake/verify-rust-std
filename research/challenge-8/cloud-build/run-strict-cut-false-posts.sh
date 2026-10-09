#!/usr/bin/env bash
# Cloud-only false-post negatives after same-build strictCUT matrix discovery.
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
controls_evidence=
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
    *) printf 'Unknown strictCUT false-post argument: %s\n' "$1" >&2; exit 2 ;;
  esac
done
for path in "$production_source" "$production_patch" "$stock_home" "$compiler_sysroot" \
            "$evidence" "$proof_root" "$work_root" "$cloud_dir" \
            "$relocation_evidence" "$controls_evidence"; do
  [[ -n "$path" && "$path" == /workspace/* &&
     "$path" != *'/../'* && "$path" != *'/./'* ]] || exit 2
done
[[ "$deadline_epoch" =~ ^[0-9]+$ ]] || exit 2
[[ "${SMALLSORT_EXECUTION_PROVIDER:-}" == cloud-build && -z "${GITHUB_ACTIONS:-}" ]] || exit 2
[[ -d "$production_source/.git" && -d "$proof_root/.git" && -f "$production_patch" ]] || exit 2
[[ -f "$controls_evidence/diagnostic-audit.json" &&
   -f "$relocation_evidence/diagnostic-audit.json" ]] || exit 2
[[ ! -e "$evidence" ]] || { printf 'false-post evidence exists: %s\n' "$evidence" >&2; exit 2; }
relocation_source="$work_root/cut-relocation-isolated-source"
[[ -d "$relocation_source/.git" && -f "$relocation_source/bin/verifast" ]] || exit 2
for name in strict-cut-controls-audit.py strict-cut-false-posts-prepare.py \
            strict-cut-false-posts-capture.py strict-cut-false-posts-audit.py \
            cut-relocate-audit.py provider.py; do
  [[ -f "$cloud_dir/$name" ]] || exit 2
done
mkdir -p "$evidence"
{
  printf 'profile=STRICT_CUT_FALSE_POSTS_DIAGNOSTIC_ONLY_NOT_ACCEPTED\n'
  printf 'proof_sha=%s\n' "$(git -C "$proof_root" rev-parse HEAD)"
  printf 'production_source_head=%s\n' "$(git -C "$production_source" rev-parse HEAD)"
  printf 'deadline_epoch=%s\n' "$deadline_epoch"
  printf 'parent_controls=%s\n' "$controls_evidence"
  printf 'parent_relocation=%s\n' "$relocation_evidence"
} > "$evidence/input-identity.txt"
python3 "$cloud_dir/provider.py" > "$evidence/provider.json"
python3 - "$evidence/provider.json" <<'PROVIDER'
import json,sys
assert json.load(open(sys.argv[1]))['provider']=='cloud-build'
PROVIDER
python3 "$cloud_dir/strict-cut-controls-audit.py" final \
  --production-source "$production_source" \
  --production-applied-patch "$production_patch" \
  --stock-home "$stock_home" \
  --relocation-source "$relocation_source" \
  --relocation-evidence "$relocation_evidence" \
  --proof-root "$proof_root" --cloud-dir "$cloud_dir" \
  --evidence "$controls_evidence" \
  --output "$evidence/prior-controls-audit.json"
python3 "$cloud_dir/strict-cut-false-posts-prepare.py" \
  --proof-root "$proof_root" --controls-evidence "$controls_evidence" \
  --evidence "$evidence"

deps_home="$work_root/vfdeps-adf88dc"
[[ -d "$deps_home/bin" && -d "$deps_home/include" && -d "$deps_home/lib" &&
   -d "$compiler_sysroot/lib" ]] || exit 2
export PATH="$deps_home/bin:$relocation_source/bin:$PATH"
export CAPNP_INC_DIR="$deps_home/include"
export LD_LIBRARY_PATH="$compiler_sysroot/lib:$relocation_source/bin:$deps_home/lib:${LD_LIBRARY_PATH:-}"
export RUSTUP_TOOLCHAIN=nightly-2026-09-25
unset SORT4_STRICT_LFT_TRACE SORT4_STRICT_LFT_RELOCATE SORT4_HRTB_OUTPUT SORT4_HRTB_OUTPUT_TARGETS
for tool in capnp rustc; do
  command -v "$tool" >/dev/null || exit 2
done
[[ "$(rustc --print sysroot)" == "$compiler_sysroot" ]] || exit 2

run_case() {
  local key=$1 budget code=0
  budget=$((deadline_epoch - $(date +%s) - 30))
  if ((budget <= 0)); then
    code=124
    printf 'false-post controls deadline before %s\n' "$key" > "$evidence/capture-$key.log"
  else
    /usr/bin/time -v -o "$evidence/capture-$key-resources.txt" \
      timeout --signal=TERM --kill-after=10s "${budget}s" \
      python3 "$cloud_dir/strict-cut-false-posts-capture.py" \
        --case "$key" --tool-home "$relocation_source" \
        --proof-root "$proof_root" --cloud-dir "$cloud_dir" \
        --evidence "$evidence" --compiler-sysroot "$compiler_sysroot" \
        --deadline-epoch "$deadline_epoch" \
      > "$evidence/capture-$key.log" 2>&1 || code=$?
  fi
  printf '%s\n' "$code" > "$evidence/capture-$key-exit-code.txt"
  printf 'strictCUT false-post %s exit=%s\n' "$key" "$code"
}
run_case normal-false
run_case unwind-false
python3 - "$evidence" <<'CAPTURE_EXITS'
import json,sys
from pathlib import Path
root=Path(sys.argv[1])
keys=('normal-false','unwind-false')
codes={key:int((root/f'capture-{key}-exit-code.txt').read_text()) for key in keys}
(root/'capture-exits.json').write_text(json.dumps(codes,indent=2,sort_keys=True)+'\n')
CAPTURE_EXITS
python3 "$cloud_dir/strict-cut-false-posts-audit.py" \
  --proof-root "$proof_root" --controls-evidence "$controls_evidence" \
  --evidence "$evidence" --cloud-dir "$cloud_dir" \
  --output "$evidence/diagnostic-audit.json"
printf '%s\n' 'STRICT_CUT_FALSE_POSTS_DISCOVERY_ONLY_NOT_ACCEPTED' \
  > "$evidence/PROFILE-STATUS.txt"
