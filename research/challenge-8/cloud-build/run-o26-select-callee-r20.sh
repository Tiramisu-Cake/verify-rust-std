#!/usr/bin/env bash
# R20 Select callee lane: nine-body actual select_unpredictable unit only.
# Reuses the reviewed O26 refresh tool build, provider-guard overlay, source
# preflight, capture, compare and baseline proof stages (blocker diagnostic).
# Diagnostics only: no actual-body route, no acceptance, no proof credit.
set -euo pipefail

proof_root=${PROOF_ROOT:-/workspace/proof}
infra_root=${INFRA_ROOT:-/workspace/infra}
cloud_dir=${INFRA_CLOUD_DIR:-$infra_root/research/challenge-8/cloud-build}
work_root=${WORK_ROOT:-/workspace/smallsort-work}
evidence_root=${EVIDENCE_ROOT:-/workspace/evidence}
deadline=${SMALLSORT_DEADLINE_EPOCH:?SMALLSORT_DEADLINE_EPOCH is required}
current_sha=${PROOF_SHA:?PROOF_SHA is required}
[[ "$#" == 1 && "$1" == o26-select-callee-r20 &&
   "${LANE:-}" == o26-select-callee-r20 &&
   ( "${SORT4_R20_CALLEE_PHASE_ID:-}" == SORT4-ACTUAL-SELECT-2026-10-22-R20 ||
     "${SORT4_R20_CALLEE_PHASE_ID:-}" == SORT4-ACTUAL-SELECT-2026-10-23-R21 ) ]] || exit 2
# The R20 certificate opt-in is per proof call only, never ambient.
[[ -z "${SORT4_R20_FINAL_SELECT_REPAIR:-}" ]] || exit 2
[[ ! -v SORT4_R24_CHECKED_POINTER_OUTCOMES ]] || exit 2
while IFS= read -r route_env_key; do
  [[ "$route_env_key" != SORT4_R21_FRACTIONAL* ]] || exit 2
done < <(compgen -e)
for path in "$proof_root" "$infra_root" "$work_root" "$evidence_root"; do
  [[ "$path" == /workspace/* ]] || { printf 'path outside /workspace: %s\n' "$path" >&2; exit 2; }
done
[[ "${SMALLSORT_EXECUTION_PROVIDER:-}" == cloud-build ]] || exit 2
[[ -z "${GITHUB_ACTIONS:-}" ]] || { printf 'fake GitHub identity prohibited\n' >&2; exit 2; }
positive_ast_args=()
target_map_args=()
if [[ -n "${SORT4_R24_SESSION_PHASE_ID:-}" ]]; then
  [[ "${SORT4_R24_SESSION_PHASE_ID}" == SORT4-ACTUAL-SELECT-2026-10-24-R24 ]] || exit 2
  positive_ast_args=(--positive-ast-inventory --checked-pointer-outcomes)
  target_map_path="$proof_root/research/challenge-8/task-history/select-callee-r24/CONTROL-TARGETS.json"
  [[ "$(sha256sum "$target_map_path" | cut -d' ' -f1)" == a6bde55bf08490352cae04fbaa61aa85f33a94890d52e8fe3147f50859e588dc ]] || exit 2
  target_map_args=(--target-map "$target_map_path")
fi
[[ "$(git -C "$proof_root" rev-parse HEAD)" == "$current_sha" ]] || exit 2
[[ -d "$cloud_dir" ]] || exit 2
mkdir -p "$work_root" "$evidence_root"
ev="$evidence_root/allprooflogs"
[[ ! -e "$ev" ]] || { printf 'O26 refresh evidence already exists: %s\n' "$ev" >&2; exit 2; }
mkdir "$ev"
mkdir "$ev/cases"
current_stage=provider
audit_result() {
  python3 "$cloud_dir/select-callee-r21-proof-audit.py" --evidence "$ev" \
    --output "$evidence_root/proof-audit.json" \
    --runner-exit "$1" --failed-stage "$2"
}
trap 'status=$?; if [[ ! -f "$evidence_root/proof-audit.json" ]]; then audit_result "$status" "$current_stage" || true; fi' EXIT

CLOUD_BUILD_ID=${CLOUD_BUILD_ID:?} \
CLOUD_BUILD_PROJECT_ID=${CLOUD_BUILD_PROJECT_ID:?} \
CLOUD_BUILD_REGION=${CLOUD_BUILD_REGION:?} \
  python3 "$cloud_dir/provider.py" > "$ev/provider.json"

remaining() {
  local seconds=$((deadline - $(date +%s)))
  (( seconds > 0 )) || { printf 'deadline elapsed\n' >&2; exit 124; }
  printf '%s' "$seconds"
}
stage() {
  local name=$1; shift
  current_stage=$name
  local budget code=0
  budget=$(remaining)
  /usr/bin/time -v -o "$ev/$name-resources.txt" \
    timeout --signal=TERM --kill-after=10s "${budget}s" "$@" \
    > "$ev/$name.log" 2>&1 || code=$?
  printf '%s\n' "$code" > "$ev/$name-exit-code.txt"
  cat "$ev/$name.log"
  (( code == 0 )) || return "$code"
}

# Source-only stages first: a missing closure file fails before the tool build.
stage provider-overlays python3 "$cloud_dir/o26-refresh-recipe.py" overlay \
  --repo "$proof_root" --cloud-dir "$cloud_dir" --evidence "$ev"
stage source-preflight python3 "$cloud_dir/o26-refresh-recipe.py" preflight \
  --repo "$proof_root" --cloud-dir "$cloud_dir" --evidence "$ev"


export RUSTUP_HOME="$work_root/rustup"
export CARGO_HOME="$work_root/cargo"
export PATH="$CARGO_HOME/bin:$PATH"
export RUSTUP_TOOLCHAIN=nightly-2026-09-25
export SORT4_SELECT_PROFILE=experimental-s6-26.10-v1
export TMPDIR="$work_root/tmp"
mkdir -p "$RUSTUP_HOME" "$CARGO_HOME" "$TMPDIR"
task_temp="$work_root/o26-refresh"
mkdir -p "$task_temp"
stock_archive="$task_temp/verifast-26.10-linux.tar.gz"
stock_home="$task_temp/verifast-26.10"
source_home="$task_temp/source"
schema="$source_home/src/rust_frontend/vf_mir/vf_mir.capnp"
manifest="$proof_root/research/challenge-8/overnight-linkage/O26-PROFILE-MANIFEST.json"

python3 - "$manifest" "$proof_root" "$ev" <<'INPUTS'
import hashlib,json,pathlib,sys
m=pathlib.Path(sys.argv[1]); proof,ev=map(pathlib.Path,sys.argv[2:])
data=json.loads(m.read_text()); h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert data['proof_sha']=='c19e4c50470d32199178d5229a2819554fc6b2f1'
assert len(data['patches_in_application_order'])==20
assert data['kernel_modified'] is False
assert data['status']=='EXPERIMENTAL_O26_MAIN20_NOT_HELPER_ACCEPTANCE'
for i,row in enumerate(data['patches_in_application_order'],1):
 assert row['component']==i
 path=proof/'research/challenge-8'/row['path']
 assert h(path)==row['sha256'],f'patch pin mismatch {row["path"]}'
(ev/'frozen-profile.json').write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
INPUTS

stage package-index apt-get update
stage packages-install apt-get install --yes --no-install-recommends \
  build-essential m4 patch unzip capnproto ripgrep time libgmp10 libmpfr6 \
  libgomp1 libffi8 libncurses6 libtinfo6 zlib1g libz3-4 libgtk-3-0 libgtksourceview-4-0
stage download curl -fL --retry 2 -o "$stock_archive" \
  https://github.com/verifast/verifast/releases/download/26.10/verifast-26.10-linux.tar.gz
printf '%s  %s\n' 5ad2a65997457fd5996a27f93107ef7e52c90c0d12b63b6e67f7acbc73e90efd \
  "$stock_archive" | sha256sum -c - > "$ev/archive-sha256.log"
stage extract tar -xzf "$stock_archive" -C "$task_temp"
stage source-checkout git clone --depth 1 --branch 26.10 \
  https://github.com/verifast/verifast.git "$source_home"
[[ "$(git -C "$source_home" rev-parse HEAD)" == f76012fb518703b1d98e243ac4f487f16877cfcb ]] || exit 2
[[ "$(sha256sum "$schema" | cut -d' ' -f1)" == f48fcf29b99717c2e0cb37d4708b47eccaa3270b999e4a84093e37fbd51b7469 ]] || exit 2
rustup_init="$work_root/rustup-init-1.28.2"
stage rustup-init-download curl -fL --retry 2 -o "$rustup_init" \
  https://static.rust-lang.org/rustup/archive/1.28.2/x86_64-unknown-linux-gnu/rustup-init
printf '%s  %s\n' 20a06e644b0d9bd2fbdbfd52d42540bdde820ea7df86e92e533c073da0cdd43c \
  "$rustup_init" | sha256sum -c - > "$ev/rustup-init-sha256.log"
chmod +x "$rustup_init"
stage rustup-init "$rustup_init" -y --no-modify-path --default-toolchain none --profile minimal
stage compiler rustup toolchain install "$RUSTUP_TOOLCHAIN" --profile minimal \
  --component rustc-dev --component llvm-tools-preview --component rust-src
compiler_sysroot=$(rustc --print sysroot)
rustc --version --verbose > "$ev/compiler-version.txt"
rg -q '^commit-hash: f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f$' "$ev/compiler-version.txt"
export LD_LIBRARY_PATH="$compiler_sysroot/lib:$stock_home/bin:${LD_LIBRARY_PATH:-}"

mapfile -t patch_rows < <(python3 - "$manifest" <<'PATCHES'
import json,sys
for row in json.load(open(sys.argv[1]))['patches_in_application_order']:
 print(f"{row['component']} {row['path']} {row['sha256']}")
PATCHES
)
for row in "${patch_rows[@]}"; do
  read -r number relative expected <<< "$row"
  patch="$proof_root/research/challenge-8/$relative"
  [[ "$(sha256sum "$patch" | cut -d' ' -f1)" == "$expected" ]] || exit 2
  stage "patch-$number-check" git -C "$source_home" apply --check "$patch"
  stage "patch-$number-apply" git -C "$source_home" apply "$patch"
done
git -C "$source_home" diff --name-only > "$ev/modified-files.txt"
python3 - "$manifest" "$ev/modified-files.txt" <<'NAMES'
import json,pathlib,sys
m=json.load(open(sys.argv[1])); actual=pathlib.Path(sys.argv[2]).read_text().splitlines()
assert actual==sorted(m['production_modified_files']),(actual,m['production_modified_files'])
NAMES
git -C "$source_home" diff > "$ev/applied.patch"
[[ "$(sha256sum "$ev/applied.patch" | cut -d' ' -f1)" == 6c4c5a7708af3bdec585abd308d37383a7de522a1aaecf2c01e1f94181324c25 ]] || exit 2
cp "$ev/applied.patch" "$ev/frozen20-applied.patch"
profile="$proof_root/research/challenge-8/overnight-assume-actual/O26-REFRESH-PROFILE.json"
python3 - "$profile" "$proof_root" "$ev" <<'REFRESH'
import hashlib,json,pathlib,sys
m=json.load(open(sys.argv[1]));root=pathlib.Path(sys.argv[2]);ev=pathlib.Path(sys.argv[3])
assert m['classification']=='EXPERIMENTAL_O26_REFRESH_17_20'
assert m['historical20_applied_diff_sha256']=='6c4c5a7708af3bdec585abd308d37383a7de522a1aaecf2c01e1f94181324c25'
assert len(m['refresh_patches'])==2
for row in m['refresh_patches']:
 path=root/'research/challenge-8'/row['path']
 assert hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256']
(ev/'refresh-profile.json').write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
REFRESH
mapfile -t refresh_rows < <(python3 - "$profile" <<'PATCHES'
import json,sys
for row in json.load(open(sys.argv[1]))['refresh_patches']:
 print(f"{row['component']} {row['path']} {row['sha256']}")
PATCHES
)
for row in "${refresh_rows[@]}"; do
  read -r number relative expected <<< "$row"
  patch="$proof_root/research/challenge-8/$relative"
  [[ "$(sha256sum "$patch" | cut -d' ' -f1)" == "$expected" ]] || exit 2
  stage "refresh-$number-check" git -C "$source_home" apply --check "$patch"
  stage "refresh-$number-apply" git -C "$source_home" apply "$patch"
done
git -C "$source_home" diff --name-only > "$ev/refreshed-modified-files.txt"
cmp "$ev/modified-files.txt" "$ev/refreshed-modified-files.txt"
git -C "$source_home" diff > "$ev/refreshed-applied.patch"
[[ "$(sha256sum "$source_home/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml" | cut -d' ' -f1)" == 0862e635075edd06a827c567710a3e1125ac03aa122e95149db755a1fddce48a ]] || exit 2
# R21 opt-in certificate refresh for the branch-selected final-select repair;
# without SORT4_R20_FINAL_SELECT_REPAIR=1 the translator keeps the O26 pins.
branch_patch="$proof_root/research/challenge-8/overnight-assume-actual/verifast-r21-final-select-branch-selected-26.10.patch"
[[ "$(sha256sum "$branch_patch" | cut -d' ' -f1)" == 78079210a5548fee87e200996920bfb012bcb0cd17b0b574eb926806a46e7ab6 ]] || exit 2
stage branch-refresh-check git -C "$source_home" apply --check "$branch_patch"
stage branch-refresh-apply git -C "$source_home" apply "$branch_patch"
[[ "$(sha256sum "$source_home/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml" | cut -d' ' -f1)" == 606235c66c76412d2fdcef5f30436c342771ad5a087b343f618cfb7c8a2344d2 ]] || exit 2
fractional_patch="$proof_root/research/challenge-8/overnight-assume-actual/verifast-r23-fractional-forget-26.10.patch"
current_stage=fractional-patch-identity
[[ "$(sha256sum "$fractional_patch" | cut -d' ' -f1)" == f954fb593665b71b2042d9e1476fbc0d1b8de124861fb8f48aed4be8d791d084 ]] || exit 2
stage fractional-refresh-check git -C "$source_home" apply --check "$fractional_patch"
stage fractional-refresh-apply git -C "$source_home" apply "$fractional_patch"
[[ "$(sha256sum "$source_home/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml" | cut -d' ' -f1)" == 2d6f1950bd95b655560c767c54af8facfecde724f29a72c4218b65b6c6438c19 ]] || exit 2
# R23 exact fractional MIR coordinates, after full source/unit/body admission.
layout_patch="$proof_root/research/challenge-8/overnight-assume-actual/verifast-r23-fractional-mir-layout-26.10.patch"
current_stage=fractional-layout-identity
[[ "$(sha256sum "$layout_patch" | cut -d' ' -f1)" == 68810eb486d494cb49e158a13eab55b19464fad1b724bd9025cf5960b6c5bc17 ]] || exit 2
stage fractional-layout-check git -C "$source_home" apply --check "$layout_patch"
stage fractional-layout-apply git -C "$source_home" apply "$layout_patch"
[[ "$(sha256sum "$source_home/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml" | cut -d' ' -f1)" == cadaa80ab55e6fb3f53ccfcae1ab05dc953a2cb69a17616654d49dad6350478f ]] || exit 2
# UNBUILT next-window candidate: align erased ghost-call AST successors.
ghost_cfg_patch="$proof_root/research/challenge-8/task-history/select-callee-r23/ghost-cleanup-successor-fractional.patch"
current_stage=ghost-cfg-identity
[[ "$(sha256sum "$ghost_cfg_patch" | cut -d' ' -f1)" == 03f91fb5fe7cb25deabe5d6d7ab4e224e5559823b0c88b75a3c717dba088567d ]] || exit 2
stage ghost-cfg-check git -C "$source_home" apply --check "$ghost_cfg_patch"
stage ghost-cfg-apply git -C "$source_home" apply "$ghost_cfg_patch"
[[ "$(sha256sum "$source_home/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml" | cut -d' ' -f1)" == 103a34afa6b403760454ab42462040805f34f0cf42576b8179bc5ff368505e44 ]] || exit 2
# R22 parser-only fix: a one-element coefficient before `<T>.pred(..)` in an
# assertion is parsed as CoefAsn instead of a `<` comparison on a list.
parser_patch="$proof_root/research/challenge-8/overnight-assume-actual/verifast-r22-coef-typepred-parser-26.10.patch"
current_stage=parser-patch-identity
[[ "$(sha256sum "$parser_patch" | cut -d' ' -f1)" == dfdaff604314ecf0e27c44320811096f05a8bd8833910c59321fdec33de7b0e5 ]] || exit 2
[[ "$(sha256sum "$source_home/src/rust_frontend/vf_mir_translator/rust_parser.ml" | cut -d' ' -f1)" == 7bf12f1205ecf033e3bf66f11b4326c20d2876d68e19006d5db59f3e45ae91c2 ]] || exit 2
stage parser-refresh-check git -C "$source_home" apply --check "$parser_patch"
stage parser-refresh-apply git -C "$source_home" apply "$parser_patch"
[[ "$(sha256sum "$source_home/src/rust_frontend/vf_mir_translator/rust_parser.ml" | cut -d' ' -f1)" == 6a866aa5d469a1677ae1ac1bcdd675e4c059dcde449872b9cd1700d4b2e51246 ]] || exit 2
[[ "$(sha256sum "$source_home/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml" | cut -d' ' -f1)" == 103a34afa6b403760454ab42462040805f34f0cf42576b8179bc5ff368505e44 ]] || exit 2


# R24 dump-only utility support; verifier/translator semantics remain unchanged.
if (( ${#positive_ast_args[@]} > 0 )); then
  ast_serializer_patch="$proof_root/research/challenge-8/cloud-build/sort4-caller-entry-native/merge-fractions-ast-dump-r15.patch"
  ast_serializer_manifest="$proof_root/research/challenge-8/cloud-build/sort4-caller-entry-native/MERGE-FRACTIONS-AST-DUMP-R15-MANIFEST.json"
  current_stage=ast-serializer-identity
  [[ "$(sha256sum "$ast_serializer_patch" | cut -d' ' -f1)" == f08f1c391aa62e6cbeb0ad80e73958b1b6dcfd38f40b3d7d87802d12c4a534ba ]] || exit 2
  [[ "$(sha256sum "$ast_serializer_manifest" | cut -d' ' -f1)" == c529a3a45dc78a3f6f914d55f4e2e6cca29b7383f69827db1e20904d2db4b43b ]] || exit 2
  [[ "$(sha256sum "$source_home/src/frontend/ocaml_expr_of_ast.ml" | cut -d' ' -f1)" == 898203bf8fe5802478fdfd41456b49ad07f1e6fedf0535c3d303d4ec2081c9ff ]] || exit 2
  stage ast-serializer-check git -C "$source_home" apply --check "$ast_serializer_patch"
  stage ast-serializer-apply git -C "$source_home" apply "$ast_serializer_patch"
  [[ "$(sha256sum "$source_home/src/frontend/ocaml_expr_of_ast.ml" | cut -d' ' -f1)" == f32f1a9abd3f31c211b3ac633eca130e3298ab6e8fe39e5b489c69401efc1f94 ]] || exit 2
  git -C "$source_home" diff --name-only > "$ev/r24-final-tool-modified-files.txt"
  python3 - "$manifest" "$ev/r24-final-tool-modified-files.txt" <<'R24_SCOPE'
import json,pathlib,sys
m=json.load(open(sys.argv[1]))
expected=sorted(m['production_modified_files']+['src/frontend/ocaml_expr_of_ast.ml'])
actual=pathlib.Path(sys.argv[2]).read_text().splitlines()
assert actual==expected,(actual,expected)
R24_SCOPE
fi


# R24 exact checked pointer outcomes; enabled only around ordinary proof calls.
if (( ${#positive_ast_args[@]} > 0 )); then
  checked_outcomes_patch="$proof_root/research/challenge-8/task-history/select-callee-r24/checked-pointer-outcomes-r24.patch"
  current_stage=checked-outcomes-identity
  [[ "$(sha256sum "$checked_outcomes_patch" | cut -d' ' -f1)" == 81c5e18b5f754298aae94940a98a8fa3495b9d73b179d2697493b1c704070ddc ]] || exit 2
  [[ "$(sha256sum "$source_home/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml" | cut -d' ' -f1)" == 103a34afa6b403760454ab42462040805f34f0cf42576b8179bc5ff368505e44 ]] || exit 2
  stage checked-outcomes-check git -C "$source_home" apply --check "$checked_outcomes_patch"
  stage checked-outcomes-apply git -C "$source_home" apply "$checked_outcomes_patch"
  [[ "$(sha256sum "$source_home/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml" | cut -d' ' -f1)" == 6a710d26c41d69accd17aeb637e719ce7eabc321990d465a6d956ca0d0d7d93c ]] || exit 2
  checked_outcomes_scope_patch="$proof_root/research/challenge-8/task-history/select-callee-r24/checked-pointer-outcomes-scope-r24.patch"
  current_stage=checked-outcomes-scope-identity
  [[ "$(sha256sum "$checked_outcomes_scope_patch" | cut -d' ' -f1)" == 3f342a74bd855cc4dd4e8e639fbd6d96790d14c76e718fed1b475e673a275563 ]] || exit 2
  stage checked-outcomes-scope-check git -C "$source_home" apply --check "$checked_outcomes_scope_patch"
  stage checked-outcomes-scope-apply git -C "$source_home" apply "$checked_outcomes_scope_patch"
  [[ "$(sha256sum "$source_home/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml" | cut -d' ' -f1)" == e3c99165c2e5fc8ef5700dbaa3885c81310d26868e5e5ca61ecb019c4205d5db ]] || exit 2
  checked_outcomes_nine_patch="$proof_root/research/challenge-8/task-history/select-callee-r24/checked-pointer-outcomes-nine-gate-r24.patch"
  current_stage=checked-outcomes-nine-gate-identity
  [[ "$(sha256sum "$checked_outcomes_nine_patch" | cut -d' ' -f1)" == 90ad23d24b3806690887e396cb2ec4b10e25ae53df8115cba00649aa26889a3a ]] || exit 2
  stage checked-outcomes-nine-gate-check git -C "$source_home" apply --check "$checked_outcomes_nine_patch"
  stage checked-outcomes-nine-gate-apply git -C "$source_home" apply "$checked_outcomes_nine_patch"
  [[ "$(sha256sum "$source_home/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml" | cut -d' ' -f1)" == c8f5ce1da4f88a4b029b8ed12cc7667a0e227836b1843a1590f78769e073201e ]] || exit 2
  git -C "$source_home" diff --name-only > "$ev/r24-checked-outcomes-modified-files.txt"
  cmp "$ev/r24-final-tool-modified-files.txt" "$ev/r24-checked-outcomes-modified-files.txt"
fi


deps_archive="$task_temp/vfdeps-adf88dc-linux.txz"
stage deps-download curl -fL --retry 2 -o "$deps_archive" \
  https://github.com/verifast/vfdeps/releases/download/25.01/vfdeps-adf88dc-linux.txz
printf '%s  %s\n' 8d022c93d51a1d13ec1e782d767c60462405f6865d5ee416f82d6234e93ee580 \
  "$deps_archive" | sha256sum -c - > "$ev/deps-sha256.log"
stage deps-extract tar -xjf "$deps_archive" -C "$work_root"
deps_home="$work_root/vfdeps-adf88dc"
[[ -d "$deps_home" ]] || exit 2
for prefix in /vfdeps-adf88dc /tmp/vfdeps-adf88dc; do
  if [[ ! -e "$prefix" ]]; then ln -s "$deps_home" "$prefix"
  elif [[ "$(readlink -f "$prefix")" != "$deps_home" ]]; then exit 2; fi
done
export PATH="$deps_home/bin:$PATH"
export CAPNP_INC_DIR="$deps_home/include"
export LD_LIBRARY_PATH="$compiler_sysroot/lib:$source_home/bin:$deps_home/lib:${LD_LIBRARY_PATH:-}"
stage decoder-install cargo install --locked --git \
  https://github.com/btj/capnpc-ocaml-decoder \
  --rev 2d6606d9b59cd0c88a66729f3f076c10c0c8e0b2
stage console-build make -C "$source_home/src" ../bin/verifast \
  WITHOUT_LABLGTK=yes VERBOSE=yes
cp -an "$stock_home/bin/." "$source_home/bin/"
if [[ -d "$stock_home/lib" ]]; then
  mkdir -p "$source_home/lib"
  cp -an "$stock_home/lib/." "$source_home/lib/"
fi
for binary in vf-rust-mir-exporter refinement-checker vf-cxx-ast-exporter libz3.so; do
  cmp "$stock_home/bin/$binary" "$source_home/bin/$binary"
done
python3 - "$manifest" "$source_home" "$ev/profile-hashes.json" <<'HASHES'
import hashlib,json,os,pathlib,sys
m=json.load(open(sys.argv[1])); root=pathlib.Path(sys.argv[2]); out=pathlib.Path(sys.argv[3])
rows={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in m['hosted_profile_hashes']}
for path in rows:
 if path=='src/rust_frontend/vf_mir_translator/rust_parser.ml':
  if rows[path]!='6a866aa5d469a1677ae1ac1bcdd675e4c059dcde449872b9cd1700d4b2e51246':
   raise SystemExit(f'R22 parser pin differs: {path}')
 elif path not in ('bin/verifast','src/rust_frontend/vf_mir_translator/vf_mir_translator.ml') and rows[path]!=m['hosted_profile_hashes'][path]:
  raise SystemExit(f'frozen O26 tool/spec pin differs: {path}')
if os.environ.get('SORT4_R24_SESSION_PHASE_ID') == 'SORT4-ACTUAL-SELECT-2026-10-24-R24':
 if rows['src/rust_frontend/vf_mir_translator/vf_mir_translator.ml']!='c8f5ce1da4f88a4b029b8ed12cc7667a0e227836b1843a1590f78769e073201e':
  raise SystemExit('R24 checked outcomes translator pin differs')
 path='src/frontend/ocaml_expr_of_ast.ml'
 rows[path]=hashlib.sha256((root/path).read_bytes()).hexdigest()
 if rows[path]!='f32f1a9abd3f31c211b3ac633eca130e3298ab6e8fe39e5b489c69401efc1f94':
  raise SystemExit('R24 AST serializer pin differs')
out.write_text(json.dumps({'actual':rows,'historical':m['hosted_profile_hashes'],
 'console_byte_identical':rows['bin/verifast']==m['hosted_profile_hashes']['bin/verifast']},indent=2)+'\n')
HASHES
ldd "$source_home/bin/verifast" > "$ev/console-ldd.txt"
! rg -q 'not found' "$ev/console-ldd.txt"

mkdir -p "$ev/cases/candidate"
stage candidate-capture python3 "$proof_root/research/challenge-8/overnight-assume-actual/capture.py" \
  --tool-home "$source_home" --schema "$schema" \
  --compiler-sysroot "$compiler_sysroot" --evidence "$ev/cases/candidate/capture" \
  --deadline-epoch "$deadline" --fingerprint
stage candidate-source-compare python3 "$cloud_dir/o26-refresh-recipe.py" compare \
  --evidence "$ev"
# Baseline reproduction of the recorded blocker; its verifier exit is data.
stage candidate-proof python3 "$cloud_dir/o26-refresh-recipe.py" proof \
  --repo "$proof_root" --cloud-dir "$cloud_dir" --evidence "$ev" \
  --tool-home "$source_home" --schema "$schema" \
  --compiler-sysroot "$compiler_sysroot" --deadline-epoch "$deadline"
# Fresh R23 fingerprint pins bind the unchanged reviewed R22b release ghosts.
stage r21-fractional-proof python3 "$cloud_dir/select-callee-r21-fractional-proof-entry.py" "${positive_ast_args[@]}" "${target_map_args[@]}" \
  --repo "$proof_root" --cloud-dir "$cloud_dir" --evidence "$ev" \
  --tool-home "$source_home" --schema "$schema" \
  --compiler-sysroot "$compiler_sysroot" --deadline-epoch "$deadline" \
  --pins-json "$proof_root/research/challenge-8/task-history/select-callee-r23/FRACTIONAL-FINGERPRINT-INPUT.json"

current_stage=audit
audit_result 0 complete
