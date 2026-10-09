#!/usr/bin/env bash
# Cloud-only O26 nested Drop proof-order TEST; never promotes production proof.
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
    *) printf 'Unknown proof-order TEST argument: %s\n' "$1" >&2; exit 2 ;;
  esac
done
for path in "$production_source" "$production_patch" "$stock_home" "$compiler_sysroot" \
            "$evidence" "$proof_root" "$work_root" "$cloud_dir"; do
  [[ -n "$path" && "$path" == /workspace/* && "$path" != *'/../'* && "$path" != *'/./'* ]] || exit 2
done
[[ "$deadline_epoch" =~ ^[0-9]+$ ]] || exit 2
[[ "${SMALLSORT_EXECUTION_PROVIDER:-}" == cloud-build && -z "${GITHUB_ACTIONS:-}" ]] || exit 2
[[ "$(git -C "$proof_root" rev-parse HEAD)" == "${PROOF_SHA:?PROOF_SHA is required}" ]] || exit 2
[[ -d "$production_source/.git" && -f "$production_source/bin/verifast" ]] || exit 2
[[ -f "$stock_home/bin/vf-rust-mir-exporter" && -f "$stock_home/bin/refinement-checker" ]] || exit 2
[[ "$(basename "$(dirname "$evidence")")" == cases ]] || exit 2
[[ ! -e "$evidence" ]] || exit 2
test_source="$work_root/nested-proof-order-test-source"
[[ ! -e "$test_source" ]] || exit 2
patch="$proof_root/research/challenge-8/overnight-assume-actual/verifast-nine-nested-proof-order-TEST.patch"
card="$proof_root/research/challenge-8/overnight-assume-actual/CLOUD-NESTED-PROOF-ORDER-TEST-CARD.md"
[[ -f "$patch" && -f "$card" && -f "$cloud_dir/nested-proof-order-audit.py" ]] || exit 2
mkdir -p "$evidence/cases/candidate" "$work_root"
current_stage=inputs
trap 'status=$?; python3 "$cloud_dir/nested-proof-order-audit.py" --evidence "$evidence" --output "$evidence/diagnostic-audit.json" --runner-exit "$status" --failed-stage "$current_stage" > "$evidence/audit.log" 2>&1 || true' EXIT

remaining() {
  local seconds=$((deadline_epoch - $(date +%s) - 20))
  ((seconds > 0)) || exit 124
  printf '%s' "$seconds"
}
stage() {
  local name=$1; shift
  current_stage=$name
  local code=0 budget
  budget=$(remaining)
  /usr/bin/time -v -o "$evidence/$name-resources.txt" \
    timeout --signal=TERM --kill-after=10s "${budget}s" "$@" \
    > "$evidence/$name.log" 2>&1 || code=$?
  printf '%s\n' "$code" > "$evidence/$name-exit-code.txt"
  cat "$evidence/$name.log"
  return "$code"
}

python3 - "$production_source" "$production_patch" "$patch" "$evidence" "$proof_root" <<'PINS'
import hashlib,json,pathlib,subprocess,sys
production,applied,delta,ev,proof=map(pathlib.Path,sys.argv[1:])
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
translator=production/'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml'
assert sha(translator)=='0862e635075edd06a827c567710a3e1125ac03aa122e95149db755a1fddce48a'
assert sha(delta)=='da3c79529a1b78fc6f9c22eb7695b908646b8acb4c6eafde1daf3e059ee3a482'
actual=subprocess.check_output(['git','-C',str(production),'diff'])
assert actual==applied.read_bytes()
profile=json.loads((proof/'research/challenge-8/overnight-assume-actual/O26-REFRESH-PROFILE.json').read_text())
assert profile['classification']=='EXPERIMENTAL_O26_REFRESH_17_20'
assert profile['refreshed_translator_sha256']==sha(translator)
frozen=json.loads((proof/'research/challenge-8/overnight-linkage/O26-PROFILE-MANIFEST.json').read_text())
for rel in ('bin/rust/std/lib.rsspec','src/rust_frontend/vf_mir_translator/rust_parser.ml'):
 assert sha(production/rel)==frozen['hosted_profile_hashes'][rel]
(ev/'input-identity.json').write_text(json.dumps({
 'classification':'O26_NESTED_PROOF_ORDER_TEST_ONLY',
 'production_translator_sha256':sha(translator),'production_applied_sha256':sha(applied),
 'test_patch_sha256':sha(delta),'proof_sha':subprocess.check_output(
   ['git','-C',str(proof),'rev-parse','HEAD'],text=True).strip()},indent=2)+'\n')
PINS
cp "$patch" "$evidence/test-order.patch"
current_stage=provider
python3 "$cloud_dir/provider.py" > "$evidence/provider.json"
snapshot=(snapshot --production-source "$production_source" --test-source "$test_source"
  --stock-home "$stock_home" --production-applied-patch "$production_patch" --evidence "$evidence")
stage production-before-snapshot python3 "$cloud_dir/nested-proof-order-audit.py" \
  "${snapshot[@]}" --phase production-before
# Fresh source pair is generated before the TEST console build, with no verifier opt-in.
stage source-preflight python3 "$cloud_dir/o26-refresh-recipe.py" preflight \
  --repo "$proof_root" --cloud-dir "$cloud_dir" --evidence "$evidence"
stage test-source-copy cp -a "$production_source" "$test_source"
stage test-patch-check git -C "$test_source" apply --check "$patch"
stage test-patch-apply git -C "$test_source" apply "$patch"
python3 - "$production_source" "$test_source" "$evidence" "$patch" <<'DELTA'
import hashlib,json,pathlib,subprocess,sys
production,test,ev,patch=map(pathlib.Path,sys.argv[1:])
rel='src/rust_frontend/vf_mir_translator/vf_mir_translator.ml'
p=production/rel;t=test/rel
assert p.read_bytes()!=t.read_bytes()
changed=subprocess.check_output(['git','-C',str(test),'diff','--name-only'],text=True).splitlines()
base=subprocess.check_output(['git','-C',str(production),'diff','--name-only'],text=True).splitlines()
assert changed==base and rel in changed
testdiff=subprocess.check_output(['git','-C',str(test),'diff'])
(ev/'test-applied.patch').write_bytes(testdiff)
(ev/'production-translator.ml').write_bytes(p.read_bytes())
(ev/'test-translator.ml').write_bytes(t.read_bytes())
(ev/'test-delta.json').write_text(json.dumps({'changed_paths':changed,
 'production_translator_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
 'test_translator_sha256':hashlib.sha256(t.read_bytes()).hexdigest(),
 'test_patch_sha256':hashlib.sha256(patch.read_bytes()).hexdigest()},indent=2)+'\n')
DELTA
stage test-delta-snapshot python3 "$cloud_dir/nested-proof-order-audit.py" \
  "${snapshot[@]}" --phase test-delta

deps_home="$work_root/vfdeps-adf88dc"
[[ -d "$deps_home/bin" && -d "$deps_home/include" && -d "$deps_home/lib" ]] || exit 2
export PATH="$deps_home/bin:$PATH"
export CAPNP_INC_DIR="$deps_home/include"
export RUSTUP_TOOLCHAIN=nightly-2026-09-25
export LD_LIBRARY_PATH="$compiler_sysroot/lib:$test_source/bin:$deps_home/lib:${LD_LIBRARY_PATH:-}"
for tool in make capnp capnpc-ocaml-decoder rustc; do command -v "$tool" >/dev/null || exit 2; done
[[ "$(rustc --print sysroot)" == "$compiler_sysroot" ]] || exit 2
rm "$test_source/bin/verifast"
stage test-console-build make -C "$test_source/src" ../bin/verifast WITHOUT_LABLGTK=yes VERBOSE=yes
ldd "$test_source/bin/verifast" > "$evidence/test-console-ldd.txt"
! rg -q 'not found' "$evidence/test-console-ldd.txt"
sha256sum "$production_source/bin/verifast" "$test_source/bin/verifast" \
  > "$evidence/console-sha256.txt"
[[ "$(sha256sum "$production_source/bin/verifast" | cut -d' ' -f1)" != \
   "$(sha256sum "$test_source/bin/verifast" | cut -d' ' -f1)" ]] || exit 2
for tool in vf-rust-mir-exporter refinement-checker; do cmp "$stock_home/bin/$tool" "$test_source/bin/$tool"; done

stage candidate-capture python3 "$proof_root/research/challenge-8/overnight-assume-actual/capture.py" \
  --tool-home "$test_source" --schema "$test_source/src/rust_frontend/vf_mir/vf_mir.capnp" \
  --compiler-sysroot "$compiler_sysroot" --evidence "$evidence/cases/candidate/capture" \
  --deadline-epoch "$deadline_epoch" --fingerprint
stage candidate-compare python3 "$cloud_dir/o26-refresh-recipe.py" compare --evidence "$evidence"
export SORT4_NESTED_PROOF_ORDER_TEST_ROOT="$proof_root"
stage test-full-proof python3 "$cloud_dir/o26-refresh-recipe.py" proof \
  --repo "$proof_root" --cloud-dir "$cloud_dir" --evidence "$evidence" \
  --tool-home "$test_source" --schema "$test_source/src/rust_frontend/vf_mir/vf_mir.capnp" \
  --compiler-sysroot "$compiler_sysroot" --deadline-epoch "$deadline_epoch"
unset SORT4_NESTED_PROOF_ORDER_TEST_ROOT
stage final-source-snapshot python3 "$cloud_dir/nested-proof-order-audit.py" \
  "${snapshot[@]}" --phase final
current_stage=audit
python3 "$cloud_dir/nested-proof-order-audit.py" --evidence "$evidence" \
  --output "$evidence/diagnostic-audit.json" --runner-exit 0 --failed-stage none
