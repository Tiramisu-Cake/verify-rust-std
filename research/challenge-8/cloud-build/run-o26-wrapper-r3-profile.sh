#!/usr/bin/env bash
# Isolated R2-delta/R3 input-relation admission and controls, Cloud only.
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
    *) printf 'unknown R3 profile argument: %s\n' "$1" >&2; exit 2 ;;
  esac
done
for path in "$production_source" "$production_patch" "$stock_home" \
            "$compiler_sysroot" "$evidence" "$proof_root" "$work_root" \
            "$cloud_dir"; do
  [[ -n "$path" && "$path" == /workspace/* &&
     "$path" != *'/../'* && "$path" != *'/./'* ]] || exit 2
done
[[ "$deadline_epoch" =~ ^[0-9]+$ ]] || exit 2
[[ "${SMALLSORT_EXECUTION_PROVIDER:-}" == cloud-build && -z "${GITHUB_ACTIONS:-}" &&
   ( "${LANE:-}" == o26-wrapper-input-relation-r3 ||
     "${LANE:-}" == o26-wrapper-r3-nested-diagnostics ) ]] || exit 2
[[ "$(git -C "$proof_root" rev-parse HEAD)" == "${PROOF_SHA:?}" &&
   -d "$production_source/.git" && -f "$production_patch" &&
   -f "$production_source/bin/verifast" ]] || exit 2
[[ "$(basename "$(dirname "$evidence")")" == cases && ! -e "$evidence" ]] || exit 2
for name in o26-r3-profile.py o26-r3-controls.py o26-r3-audit.py \
            o26-wrapper-profile.py o26-recipe.py provider.py; do
  [[ -f "$cloud_dir/$name" ]] || exit 2
done

r2_source="$work_root/o26-r3-r2-unbuilt-source"
r3_source="$work_root/o26-r3-profile-source"
[[ ! -e "$r2_source" && ! -e "$r3_source" ]] || exit 2
mkdir -p "$evidence"
common=(--production-source "$production_source" --production-patch "$production_patch"
        --r2-source "$r2_source" --r3-source "$r3_source"
        --stock-home "$stock_home" --compiler-sysroot "$compiler_sysroot"
        --evidence "$evidence" --deadline-epoch "$deadline_epoch"
        --proof-root "$proof_root" --cloud-dir "$cloud_dir")
profile="$cloud_dir/o26-r3-profile.py"
current_stage=preflight
stage() {
  local name=$1; shift
  local seconds code=0
  current_stage=$name
  seconds=$((deadline_epoch - $(date +%s) - 25))
  ((seconds > 0)) || { printf 'R3 deadline before %s\n' "$name" >&2; return 124; }
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
    python3 "$cloud_dir/o26-r3-audit.py" \
      --evidence "$evidence" --output "$evidence/diagnostic-audit.json" \
      --runner-exit "$status" --failed-stage "$current_stage" || true
  fi
}
trap write_inconclusive EXIT

stage profile-preflight python3 "$profile" preflight "${common[@]}"
stage r2-copy cp -a "$production_source" "$r2_source"
cmp "$production_patch" <(git -C "$r2_source" diff --binary HEAD)
r2_patch="$proof_root/research/challenge-8/overnight-assume-actual/verifast-o26-wrapper-rebase-profile-26.10.patch"
stage r2-patch-check git -C "$r2_source" apply --check "$r2_patch"
stage r2-patch-apply git -C "$r2_source" apply "$r2_patch"
[[ "$(sha256sum "$r2_source/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml" | cut -d ' ' -f 1)" == \
   2a9d9fc989dcf5564c16dc5a4f8df90755257138a9f4cadde1ff9d7c7ae9fef5 ]] || exit 2
cmp "$production_source/bin/verifast" "$r2_source/bin/verifast"
stage r2-snapshot python3 "$profile" r2-snapshot "${common[@]}"
stage r3-copy cp -a "$r2_source" "$r3_source"
r3_patch="$proof_root/research/challenge-8/overnight-assume-actual/verifast-o26-wrapper-input-relation-profile-26.10.patch"
stage r3-patch-check git -C "$r3_source" apply --check "$r3_patch"
stage r3-patch-apply git -C "$r3_source" apply "$r3_patch"
[[ "$(git -C "$r3_source" rev-parse HEAD)" == f76012fb518703b1d98e243ac4f487f16877cfcb ]] || exit 2
deps_home="$work_root/vfdeps-adf88dc"
[[ -d "$deps_home/bin" && -d "$deps_home/include" && -d "$deps_home/lib" ]] || exit 2
export PATH="$deps_home/bin:$PATH"
export CAPNP_INC_DIR="$deps_home/include"
export RUSTUP_TOOLCHAIN=nightly-2026-09-25
export LD_LIBRARY_PATH="$compiler_sysroot/lib:$r3_source/bin:$deps_home/lib:${LD_LIBRARY_PATH:-}"
rm "$r3_source/bin/verifast"
stage r3-console-build make -C "$r3_source/src" ../bin/verifast WITHOUT_LABLGTK=yes VERBOSE=yes
[[ -f "$r3_source/bin/verifast" ]] || exit 2
ldd "$r3_source/bin/verifast" > "$evidence/r3-console-ldd.txt"
! rg -q 'not found' "$evidence/r3-console-ldd.txt"
stage r3-tool-identity python3 "$profile" tool-identity "${common[@]}"
stage r3-fresh-capture python3 \
  "$proof_root/research/challenge-8/overnight-assume-actual/capture.py" \
  --tool-home "$r3_source" \
  --schema "$r3_source/src/rust_frontend/vf_mir/vf_mir.capnp" \
  --compiler-sysroot "$compiler_sysroot" --evidence "$evidence/capture" \
  --deadline-epoch "$deadline_epoch" --wrapper-input-relation --fingerprint
stage r3-capture-check python3 "$profile" capture-check "${common[@]}"
stage r3-proofs python3 "$profile" proofs "${common[@]}"
stage r3-controls python3 "$cloud_dir/o26-r3-controls.py" \
  --proof-root "$proof_root" --cloud-dir "$cloud_dir" \
  --r3-source "$r3_source" --compiler-sysroot "$compiler_sysroot" \
  --evidence "$evidence" --deadline-epoch "$deadline_epoch"
stage r3-final-identity python3 "$profile" final-identity "${common[@]}"
current_stage=audit
python3 "$cloud_dir/o26-r3-audit.py" --evidence "$evidence" \
  --output "$evidence/diagnostic-audit.json" \
  --runner-exit 0 --failed-stage complete
printf '%s\n' 'WRAPPER_R3_DIAGNOSTIC_ONLY_NOT_ACCEPTED' > "$evidence/PROFILE-STATUS.txt"
