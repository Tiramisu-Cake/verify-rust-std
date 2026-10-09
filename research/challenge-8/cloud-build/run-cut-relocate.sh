#!/usr/bin/env bash
# Cloud-only strict CUT declaration-relocation TEST. Never an accepted profile.
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
    *) printf 'Unknown CUT relocation argument: %s\n' "$1" >&2; exit 2 ;;
  esac
done
for path in "$production_source" "$production_patch" "$stock_home" "$compiler_sysroot" "$evidence" "$proof_root" "$work_root" "$cloud_dir"; do
  [[ -n "$path" ]] || { printf 'CUT relocation requires all nine arguments\n' >&2; exit 2; }
done
[[ "$deadline_epoch" =~ ^[0-9]+$ ]] || exit 2
[[ "${SMALLSORT_EXECUTION_PROVIDER:-}" == cloud-build && -z "${GITHUB_ACTIONS:-}" ]] || exit 2
for path in "$production_source" "$stock_home" "$compiler_sysroot" "$evidence" "$proof_root" "$work_root" "$cloud_dir"; do
  [[ "$path" == /workspace/* && "$path" != *'/../'* && "$path" != *'/./'* ]] || {
    printf 'CUT relocation path outside /workspace: %s\n' "$path" >&2; exit 2;
  }
done
[[ "$production_patch" == /workspace/* ]] || exit 2
[[ -d "$production_source/.git" && -f "$production_patch" && -f "$production_source/bin/verifast" ]] || exit 2
[[ -f "$stock_home/bin/vf-rust-mir-exporter" && -d "$compiler_sysroot/lib" ]] || exit 2
[[ -d "$proof_root/.git" && -f "$cloud_dir/provider.py" ]] || exit 2
[[ ! -e "$evidence" ]] || { printf 'CUT relocation evidence exists: %s\n' "$evidence" >&2; exit 2; }
required_proof_files=(
  research/challenge-8/overnight-lifetime/capture.py
  research/challenge-8/overnight-lifetime/capture-relocate.py
  research/challenge-8/overnight-lifetime/cases.rs
  research/challenge-8/overnight-lifetime/verifast-strict-lft-cut-26.10.patch
  research/challenge-8/overnight-lifetime/verifast-cut-relocate-callback-TESTONLY.patch
  research/challenge-8/overnight-lifetime/verifast-cut-relocate-translated-ids-TEST.patch
  research/challenge-8/overnight-lifetime/CLOUD-RELOCATE-IDS-TEST-CARD.md
)
for relative in "${required_proof_files[@]}"; do
  [[ -f "$proof_root/$relative" ]] || {
    printf 'CUT relocation requires proof file: %s\n' "$relative" >&2; exit 2;
  }
done
for relative in cut-relocate-audit.py cut-relocate-provider-overlay.py provider.py; do
  [[ -f "$cloud_dir/$relative" ]] || {
    printf 'CUT relocation requires infrastructure file: %s\n' "$relative" >&2; exit 2;
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
  printf 'profile=STRICT_CUT_RELOCATION_TRANSLATED_IDS_TEST_DIAGNOSTIC_ONLY_NOT_ACCEPTED\n'
  printf 'patch_chain=d557082b+e7189430+fa862fe8\n'
  printf 'fixture=callback_positive_from_positive_f_bound\n'
  printf 'normal_and_unwind_post=thread/type resources, both T cells/owners, comparator F cell/owner\n'
  printf 'unwind=direct Continue; StorageDead at line 103 is not assumed on unwind\n'
} > "$evidence/input-identity.txt"

git -C "$production_source" diff --binary HEAD > "$evidence/production-before.patch"
cmp "$production_patch" "$evidence/production-before.patch"
python3 "$cloud_dir/cut-relocate-audit.py" snapshot \
  --production-source "$production_source" --output "$evidence/production-snapshot.json"
python3 "$cloud_dir/provider.py" > "$evidence/provider.json"
python3 - "$evidence/provider.json" <<'PROVIDER'
import json,sys
assert json.load(open(sys.argv[1]))['provider']=='cloud-build'
PROVIDER

cut_patch="$proof_root/research/challenge-8/overnight-lifetime/verifast-strict-lft-cut-26.10.patch"
relocation_patch="$proof_root/research/challenge-8/overnight-lifetime/verifast-cut-relocate-callback-TESTONLY.patch"
translated_ids_patch="$proof_root/research/challenge-8/overnight-lifetime/verifast-cut-relocate-translated-ids-TEST.patch"
printf '%s  %s\n' d557082b0c17771acd7386ad6caca7bc139877cf1ca513d9570da210b1b542d8 "$cut_patch" | sha256sum -c -
printf '%s  %s\n' e7189430eca9a48ed49d280131bd22987af8d05ed43a88f9c4a5c9767e57bb9e "$relocation_patch" | sha256sum -c -
printf '%s  %s\n' fa862fe86406d95eb921f2935b2e4f6cf048c5366ece8d8836e5fcd7b41a9145 "$translated_ids_patch" | sha256sum -c -
relocation_source="$work_root/cut-relocation-isolated-source"
[[ ! -e "$relocation_source" ]] || { printf 'CUT relocation source exists: %s\n' "$relocation_source" >&2; exit 2; }
mkdir -p "$work_root"

remaining() {
  local seconds=$((deadline_epoch - $(date +%s) - 30))
  (( seconds > 0 )) || { printf 'CUT relocation deadline reached\n' >&2; exit 124; }
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

stage source-copy cp -a "$production_source" "$relocation_source"
git -C "$relocation_source" diff --binary HEAD > "$evidence/cut-before.patch"
cmp "$evidence/production-before.patch" "$evidence/cut-before.patch"
cmp "$production_source/bin/verifast" "$relocation_source/bin/verifast"
stage cut-check git -C "$relocation_source" apply --check "$cut_patch"
stage cut-apply git -C "$relocation_source" apply "$cut_patch"
cp "$relocation_source/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml" \
  "$evidence/cut-translator-before-relocation.ml"
cp "$relocation_source/src/verifast.ml" "$evidence/cut-verifast-before-relocation.ml"
stage relocation-check git -C "$relocation_source" apply --check "$relocation_patch"
stage relocation-apply git -C "$relocation_source" apply "$relocation_patch"
cp "$relocation_source/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml" \
  "$evidence/relocation-translator-before-translated-ids.ml"
stage translated-ids-check git -C "$relocation_source" apply --check "$translated_ids_patch"
stage translated-ids-apply git -C "$relocation_source" apply "$translated_ids_patch"
cmp "$evidence/cut-verifast-before-relocation.ml" "$relocation_source/src/verifast.ml"
git -C "$relocation_source" diff --binary HEAD > "$evidence/relocation-applied.patch"

# All dependencies come from the earlier production build in this Cloud job.
deps_home="$work_root/vfdeps-adf88dc"
[[ -d "$deps_home/bin" && -d "$deps_home/include" && -d "$deps_home/lib" ]] || {
  printf 'CUT relocation requires existing vfdeps at %s\n' "$deps_home" >&2; exit 2;
}
export PATH="$deps_home/bin:$PATH"
export CAPNP_INC_DIR="$deps_home/include"
export RUSTUP_TOOLCHAIN=nightly-2026-09-25
export LD_LIBRARY_PATH="$compiler_sysroot/lib:$relocation_source/bin:$deps_home/lib:${LD_LIBRARY_PATH:-}"
for tool in make capnp capnpc-ocaml-decoder rustc; do
  command -v "$tool" >/dev/null || { printf 'CUT relocation dependency missing: %s\n' "$tool" >&2; exit 2; }
done
[[ "$(rustc --print sysroot)" == "$compiler_sysroot" ]] || exit 2
(( $(remaining) >= 60 )) || { printf 'Insufficient CUT relocation build time\n' >&2; exit 124; }
rm "$relocation_source/bin/verifast"
stage relocation-console-build make -C "$relocation_source/src" ../bin/verifast WITHOUT_LABLGTK=yes VERBOSE=yes
[[ -f "$relocation_source/bin/verifast" ]] || exit 2
decoder="$relocation_source/src/_build/default/rust_frontend/vf_mir_decoder/vf_mir_decoder.ml"
[[ -f "$decoder" ]] || exit 2
cp "$decoder" "$evidence/vf_mir_decoder.ml"
[[ "$(sha256sum "$relocation_source/bin/verifast" | cut -d' ' -f1)" != "$(sha256sum "$production_source/bin/verifast" | cut -d' ' -f1)" ]] || exit 2
ldd "$relocation_source/bin/verifast" > "$evidence/relocation-console-ldd.txt"
! rg -q 'not found' "$evidence/relocation-console-ldd.txt"
python3 "$cloud_dir/cut-relocate-audit.py" compare \
  --production-source "$production_source" --snapshot "$evidence/production-snapshot.json" \
  --relocation-source "$relocation_source" --stock-home "$stock_home" \
  --before-relocation "$evidence/cut-translator-before-relocation.ml" \
  --cut-verifast "$evidence/cut-verifast-before-relocation.ml" \
  --output "$evidence/source-audit.json"

stage capture-provider-overlay python3 "$cloud_dir/cut-relocate-provider-overlay.py" \
  --proof-root "$proof_root" --cloud-dir "$cloud_dir" --evidence "$evidence"
export SMALLSORT_CLOUD_PROVIDER_PATH="$cloud_dir/provider.py"
unset SORT4_STRICT_LFT_TRACE SORT4_STRICT_LFT_RELOCATE
capture="$proof_root/research/challenge-8/overnight-lifetime/capture-relocate.py"
raw_capture_exit=0
stage relocation-diagnostic python3 "$capture" \
  --tool-home "$relocation_source" --out "$evidence/relocation" \
  --deadline-epoch "$deadline_epoch" || raw_capture_exit=$?
printf '%s\n' "$raw_capture_exit" > "$evidence/raw-capture-exit-code.txt"
if [[ -f "$evidence/relocation/summary.json" ]]; then
  cat "$evidence/relocation/summary.json"
fi
for proof_log in "$evidence/relocation/callback-positive/baseline-verification.log" \
                 "$evidence/relocation/callback-positive/relocated-verification.log"; do
  if [[ -f "$proof_log" ]]; then
    cat "$proof_log"
  fi
done
python3 "$cloud_dir/cut-relocate-audit.py" classify \
  --production-source "$production_source" --snapshot "$evidence/production-snapshot.json" \
  --relocation-source "$relocation_source" --stock-home "$stock_home" \
  --before-relocation "$evidence/cut-translator-before-relocation.ml" \
  --cut-verifast "$evidence/cut-verifast-before-relocation.ml" \
  --capture "$evidence/relocation" --raw-exit "$raw_capture_exit" \
  --output "$evidence/diagnostic-audit.json"
git -C "$production_source" diff --binary HEAD > "$evidence/production-after.patch"
cmp "$production_patch" "$evidence/production-after.patch"
printf '%s\n' 'CUT_RELOCATION_TEST_DIAGNOSTIC_ONLY_NOT_ACCEPTED' > "$evidence/PROFILE-STATUS.txt"
