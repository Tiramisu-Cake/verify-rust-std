#!/usr/bin/env bash
# Experimental O26 refreshed certificate Cloud run. Diagnostics are distinct from proof.
set -euo pipefail

proof_root=${PROOF_ROOT:-/workspace/proof}
infra_root=${INFRA_ROOT:-/workspace/infra}
cloud_dir=${INFRA_CLOUD_DIR:-$infra_root/research/challenge-8/cloud-build}
work_root=${WORK_ROOT:-/workspace/smallsort-work}
evidence_root=${EVIDENCE_ROOT:-/workspace/evidence}
deadline=${SMALLSORT_DEADLINE_EPOCH:?SMALLSORT_DEADLINE_EPOCH is required}
current_sha=${PROOF_SHA:?PROOF_SHA is required}
relocate_mode=${O26_WITH_CUT_RELOCATE:-0}
[[ "$relocate_mode" == 0 || "$relocate_mode" == 1 ]] || exit 2
strict_cut_controls_mode=${O26_WITH_STRICT_CUT_CONTROLS:-0}
[[ "$strict_cut_controls_mode" == 0 || "$strict_cut_controls_mode" == 1 ]] || exit 2
[[ "$strict_cut_controls_mode" == 0 ||
   ( ( "${LANE:-}" == o26-strict-cut-controls ||
       "${LANE:-}" == o26-strict-cut-false-posts ||
       "${LANE:-}" == o26-strict-cut-reuse-false-posts ||
       "${LANE:-}" == o26-sort4-scope-tests ) && "$relocate_mode" == 1 ) ]] || exit 2
strict_cut_false_posts_mode=${O26_WITH_STRICT_CUT_FALSE_POSTS:-0}
[[ "$strict_cut_false_posts_mode" == 0 || "$strict_cut_false_posts_mode" == 1 ]] || exit 2
[[ "$strict_cut_false_posts_mode" == 0 ||
   ( ( "${LANE:-}" == o26-strict-cut-false-posts ||
       "${LANE:-}" == o26-strict-cut-reuse-false-posts ||
       "${LANE:-}" == o26-sort4-scope-tests ) && "$strict_cut_controls_mode" == 1 ) ]] || exit 2
reuse_strict_matrix_mode=${O26_REUSE_STRICT_MATRIX:-0}
[[ "$reuse_strict_matrix_mode" == 0 || "$reuse_strict_matrix_mode" == 1 ]] || exit 2
[[ "$reuse_strict_matrix_mode" == 0 ||
   ( "${LANE:-}" == o26-strict-cut-reuse-false-posts &&
     "$strict_cut_controls_mode" == 1 && "$strict_cut_false_posts_mode" == 1 &&
     "$relocate_mode" == 1 ) ]] || exit 2
[[ "${LANE:-}" != o26-strict-cut-reuse-false-posts ||
   "$reuse_strict_matrix_mode" == 1 ]] || exit 2
controls_mode=${O26_WITH_OWNER_CONTROLS:-0}
[[ "$controls_mode" == 0 || "$controls_mode" == 1 ]] || exit 2
sort4_mode=${O26_WITH_SORT4_CAPTURE:-0}
[[ "$sort4_mode" == 0 || "$sort4_mode" == 1 ]] || exit 2
a1_mode=${O26_WITH_A1_ISOLATED_TEST:-0}
[[ "$a1_mode" == 0 || "$a1_mode" == 1 ]] || exit 2
coordination_mode=${O26_WITH_COORDINATION_REGRESSION:-0}
[[ "$coordination_mode" == 0 || "$coordination_mode" == 1 ]] || exit 2
nested_order_mode=${O26_WITH_NESTED_PROOF_ORDER_TEST:-0}
[[ "$nested_order_mode" == 0 || "$nested_order_mode" == 1 ]] || exit 2
ast_probe_mode=${O26_WITH_SORT4_AST_PROBE:-0}
[[ "$ast_probe_mode" == 0 || "$ast_probe_mode" == 1 ]] || exit 2
wrapper_rebase_mode=${O26_WITH_WRAPPER_REBASE_CAPTURE:-0}
[[ "$wrapper_rebase_mode" == 0 || "$wrapper_rebase_mode" == 1 ]] || exit 2
input_relation_mode=${O26_WITH_WRAPPER_INPUT_RELATION_CAPTURE:-0}
[[ "$input_relation_mode" == 0 || "$input_relation_mode" == 1 ]] || exit 2
[[ "$input_relation_mode" == 0 || "${LANE:-}" == o26-input-relation-capture ]] || exit 2
input_relation_shadow_mode=${O26_WITH_WRAPPER_INPUT_RELATION_SHADOW_CAPTURE:-0}
[[ "$input_relation_shadow_mode" == 0 || "$input_relation_shadow_mode" == 1 ]] || exit 2
[[ "$input_relation_shadow_mode" == 0 ||
   "${LANE:-}" == o26-input-relation-shadow-capture ||
   "${LANE:-}" == o26-shadow-generic-sort4-diagnostics ]] || exit 2
input_relation_frame_mode=${O26_WITH_WRAPPER_INPUT_RELATION_FRAME_CAPTURE:-0}
[[ "$input_relation_frame_mode" == 0 || "$input_relation_frame_mode" == 1 ]] || exit 2
[[ "$input_relation_frame_mode" == 0 ||
   "${LANE:-}" == o26-input-relation-frame-capture ]] || exit 2
[[ "$input_relation_frame_mode" == 0 ||
   ( "$input_relation_mode" == 0 && "$input_relation_shadow_mode" == 0 ) ]] || exit 2
generic_new_mode=${O26_WITH_GENERIC_NEW_CAPTURE:-0}
[[ "$generic_new_mode" == 0 || "$generic_new_mode" == 1 ]] || exit 2
[[ "$generic_new_mode" == 0 || "${LANE:-}" == o26-generic-new-capture ||
   "${LANE:-}" == o26-generic-sort4-postmark-diagnostics ||
   "${LANE:-}" == o26-shadow-generic-sort4-diagnostics ]] || exit 2
postmark_mode=${O26_WITH_SORT4_POSTMARK_PRINT_TEST:-0}
[[ "$postmark_mode" == 0 || "$postmark_mode" == 1 ]] || exit 2
[[ "$postmark_mode" == 0 ||
   ( ( "${LANE:-}" == o26-generic-sort4-postmark-diagnostics ||
       "${LANE:-}" == o26-shadow-generic-sort4-diagnostics ) && "$generic_new_mode" == 1 ) ]] || exit 2
r3_profile_mode=${O26_WITH_R3_PROFILE:-0}
[[ "$r3_profile_mode" == 0 || "$r3_profile_mode" == 1 ]] || exit 2
[[ "$r3_profile_mode" == 0 || "${LANE:-}" == o26-wrapper-input-relation-r3 ||
   "${LANE:-}" == o26-wrapper-r3-nested-diagnostics ||
   "${LANE:-}" == o26-r3-ghost-scope-test ]] || exit 2
ghost_scope_mode=${O26_WITH_R3_GHOST_SCOPE_TEST:-0}
[[ "$ghost_scope_mode" == 0 || "$ghost_scope_mode" == 1 ]] || exit 2
[[ "$ghost_scope_mode" == 0 ||
   ( "${LANE:-}" == o26-r3-ghost-scope-test && "$r3_profile_mode" == 1 ) ]] || exit 2
[[ "${LANE:-}" != o26-r3-ghost-scope-test || "$ghost_scope_mode" == 1 ]] || exit 2
r3_nested_mode=${O26_WITH_R3_NESTED_ORDER_TEST:-0}
[[ "$r3_nested_mode" == 0 || "$r3_nested_mode" == 1 ]] || exit 2
[[ "$r3_nested_mode" == 0 ||
   ( "${LANE:-}" == o26-wrapper-r3-nested-diagnostics && "$r3_profile_mode" == 1 ) ]] || exit 2
wrapper_profile_mode=${O26_WITH_WRAPPER_REBASE_PROFILE:-0}
[[ "$wrapper_profile_mode" == 0 || "$wrapper_profile_mode" == 1 ]] || exit 2
comp19_mode=${O26_WITH_WRAPPER_COMP19_TEST:-0}
[[ "$comp19_mode" == 0 || "$comp19_mode" == 1 ]] || exit 2
[[ "$comp19_mode" == 0 || "$wrapper_profile_mode" == 1 ]] || exit 2
[[ "$comp19_mode" == 0 || "${LANE:-}" == o26-wrapper-controls ]] || exit 2
if [[ "$input_relation_frame_mode" == 1 ]]; then
  [[ "${LANE:-}" == o26-input-relation-frame-capture &&
     "$relocate_mode" == 0 && "$strict_cut_controls_mode" == 0 &&
     "$strict_cut_false_posts_mode" == 0 && "$reuse_strict_matrix_mode" == 0 &&
     "$controls_mode" == 0 && "$sort4_mode" == 0 && "$a1_mode" == 0 &&
     "$coordination_mode" == 0 && "$nested_order_mode" == 0 &&
     "$ast_probe_mode" == 0 && "$wrapper_rebase_mode" == 0 &&
     "$input_relation_mode" == 0 && "$input_relation_shadow_mode" == 0 &&
     "$generic_new_mode" == 0 && "$postmark_mode" == 0 &&
     "$r3_profile_mode" == 0 && "$ghost_scope_mode" == 0 &&
     "$r3_nested_mode" == 0 && "$wrapper_profile_mode" == 0 &&
     "$comp19_mode" == 0 ]] || exit 2
fi
for path in "$proof_root" "$infra_root" "$work_root" "$evidence_root"; do
  [[ "$path" == /workspace/* ]] || { printf 'path outside /workspace: %s\n' "$path" >&2; exit 2; }
done
[[ "${SMALLSORT_EXECUTION_PROVIDER:-}" == cloud-build ]] || exit 2
[[ -z "${GITHUB_ACTIONS:-}" ]] || { printf 'fake GitHub identity prohibited\n' >&2; exit 2; }
[[ "$(git -C "$proof_root" rev-parse HEAD)" == "$current_sha" ]] || exit 2
[[ -d "$cloud_dir" ]] || exit 2
mkdir -p "$work_root" "$evidence_root"
ev="$evidence_root/allprooflogs"
[[ ! -e "$ev" ]] || { printf 'O26 refresh evidence already exists: %s\n' "$ev" >&2; exit 2; }
mkdir "$ev"
mkdir "$ev/cases"
current_stage=provider
audit_result() {
  local status=$1 failed=$2
  if [[ "$comp19_mode" == 1 ]]; then
    python3 "$cloud_dir/o26-refresh-audit.py" --evidence "$ev" \
      --output "$evidence_root/profile-proof-audit.json" \
      --runner-exit "$status" --failed-stage "$failed"
    python3 "$cloud_dir/o26-wrapper-controls-audit.py" --evidence "$ev" \
      --base "$evidence_root/profile-proof-audit.json" \
      --output "$evidence_root/proof-audit.json"
  else
    python3 "$cloud_dir/o26-refresh-audit.py" --evidence "$ev" \
      --output "$evidence_root/proof-audit.json" \
      --runner-exit "$status" --failed-stage "$failed"
  fi
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
import hashlib,json,pathlib,sys
m=json.load(open(sys.argv[1])); root=pathlib.Path(sys.argv[2]); out=pathlib.Path(sys.argv[3])
rows={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in m['hosted_profile_hashes']}
for path in rows:
 if path not in ('bin/verifast','src/rust_frontend/vf_mir_translator/vf_mir_translator.ml') and rows[path]!=m['hosted_profile_hashes'][path]:
  raise SystemExit(f'frozen O26 tool/spec pin differs: {path}')
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
case_dir="$ev/cases/candidate/capture/nine-body-a1-owned-forget"
stage candidate-proof python3 "$cloud_dir/o26-refresh-recipe.py" proof \
  --repo "$proof_root" --cloud-dir "$cloud_dir" --evidence "$ev" \
  --tool-home "$source_home" --schema "$schema" \
  --compiler-sysroot "$compiler_sysroot" --deadline-epoch "$deadline"

if [[ "$generic_new_mode" == 1 ]]; then
  printf '{"requested":true}\n' > "$ev/cases/generic-new-capture-request.json"
  generic_new_status=0
  stage generic-new-prepare python3 \
    "$proof_root/research/challenge-8/overnight-generic-select/prepare.py" \
    --proof-root "$proof_root" --cloud-dir "$cloud_dir" \
    --evidence "$ev/cases/generic-new-capture" || generic_new_status=$?
  if [[ "$generic_new_status" == 0 ]]; then
    stage generic-new-capture python3 \
      "$proof_root/research/challenge-8/overnight-generic-select/capture.py" \
      --cloud-dir "$cloud_dir" --evidence "$ev/cases/generic-new-capture" \
      --tool-home "$source_home" --compiler-sysroot "$compiler_sysroot" \
      --deadline-epoch "$deadline" || generic_new_status=$?
  fi
  printf '%s\n' "$generic_new_status" \
    > "$ev/cases/generic-new-capture-helper-exit-code.txt"
fi

if [[ "$postmark_mode" == 1 ]]; then
  printf '{"requested":true}\n' > "$ev/cases/sort4-postmark-print-test-request.json"
  postmark_status=0
  stage sort4-postmark-print-test bash "$cloud_dir/run-sort4-postmark-print-test.sh" \
    --production-source "$source_home" --production-applied-patch "$ev/refreshed-applied.patch" \
    --stock-home "$stock_home" --compiler-sysroot "$compiler_sysroot" \
    --evidence "$ev/cases/sort4-postmark-print-test" --deadline-epoch "$deadline" \
    --proof-root "$proof_root" --work-root "$work_root" --cloud-dir "$cloud_dir" || postmark_status=$?
  printf '%s\n' "$postmark_status" > "$ev/cases/sort4-postmark-print-test-helper-exit-code.txt"
fi

if [[ "$r3_profile_mode" == 1 ]]; then
  printf '{"requested":true}\n' > "$ev/cases/wrapper-r3-profile-request.json"
  r3_status=0
  stage wrapper-r3-profile bash "$cloud_dir/run-o26-wrapper-r3-profile.sh" \
    --production-source "$source_home" --production-applied-patch "$ev/refreshed-applied.patch" \
    --stock-home "$stock_home" --compiler-sysroot "$compiler_sysroot" \
    --evidence "$ev/cases/wrapper-r3-profile" --deadline-epoch "$deadline" \
    --proof-root "$proof_root" --work-root "$work_root" --cloud-dir "$cloud_dir" || r3_status=$?
  printf '%s\n' "$r3_status" > "$ev/cases/wrapper-r3-profile-helper-exit-code.txt"
fi

if [[ "$ghost_scope_mode" == 1 ]]; then
  printf '{"requested":true}\n' > "$ev/cases/r3-ghost-scope-test-request.json"
  ghost_scope_status=0
  stage r3-ghost-scope-test bash "$cloud_dir/run-o26-r3-ghost-scope-test.sh" \
    --r3-source "$work_root/o26-r3-profile-source" \
    --r3-evidence "$ev/cases/wrapper-r3-profile" \
    --compiler-sysroot "$compiler_sysroot" \
    --evidence "$ev/cases/r3-ghost-scope-test" --deadline-epoch "$deadline" \
    --proof-root "$proof_root" || ghost_scope_status=$?
  printf '%s\n' "$ghost_scope_status" > "$ev/cases/r3-ghost-scope-test-helper-exit-code.txt"
fi

if [[ "$r3_nested_mode" == 1 ]]; then
  printf '{"requested":true}\n' > "$ev/cases/r3-nested-order-test-request.json"
  r3_nested_status=0
  stage r3-nested-order-test bash "$cloud_dir/run-o26-r3-nested-order-test.sh" \
    --r3-source "$work_root/o26-r3-profile-source" \
    --r3-evidence "$ev/cases/wrapper-r3-profile" --compiler-sysroot "$compiler_sysroot" \
    --evidence "$ev/cases/r3-nested-order-test" --deadline-epoch "$deadline" \
    --proof-root "$proof_root" --work-root "$work_root" --cloud-dir "$cloud_dir" || r3_nested_status=$?
  printf '%s\n' "$r3_nested_status" > "$ev/cases/r3-nested-order-test-helper-exit-code.txt"
fi

if [[ "$wrapper_profile_mode" == 1 ]]; then
  printf '{"requested":true}\n' > "$ev/cases/wrapper-profile-request.json"
  profile_status=0
  stage wrapper-profile bash "$cloud_dir/run-o26-wrapper-profile.sh" \
    --production-source "$source_home" --production-applied-patch "$ev/refreshed-applied.patch" \
    --stock-home "$stock_home" --compiler-sysroot "$compiler_sysroot" \
    --evidence "$ev/cases/wrapper-profile" --deadline-epoch "$deadline" \
    --proof-root "$proof_root" --work-root "$work_root" --cloud-dir "$cloud_dir" || profile_status=$?
  printf '%s\n' "$profile_status" > "$ev/cases/wrapper-profile-helper-exit-code.txt"
fi

if [[ "$wrapper_rebase_mode" == 1 ]]; then
  printf '{"requested":true}\n' > "$ev/cases/wrapper-rebase-capture-request.json"
  rebase_status=0
  stage wrapper-rebase-capture python3 "$proof_root/research/challenge-8/overnight-assume-actual/capture.py" \
    --tool-home "$source_home" --schema "$schema" \
    --compiler-sysroot "$compiler_sysroot" --evidence "$ev/cases/wrapper-rebase-capture" \
    --deadline-epoch "$deadline" --wrapper-rebase --fingerprint || rebase_status=$?
  printf '%s\n' "$rebase_status" > "$ev/cases/wrapper-rebase-capture-helper-exit-code.txt"
fi

if [[ "$input_relation_mode" == 1 ]]; then
  printf '{"requested":true}\n' > "$ev/cases/wrapper-input-relation-capture-request.json"
  input_relation_status=0
  stage wrapper-input-relation-capture python3 "$proof_root/research/challenge-8/overnight-assume-actual/capture.py" \
    --tool-home "$source_home" --schema "$schema" \
    --compiler-sysroot "$compiler_sysroot" --evidence "$ev/cases/wrapper-input-relation-capture" \
    --deadline-epoch "$deadline" --wrapper-input-relation --fingerprint || input_relation_status=$?
  printf '%s\n' "$input_relation_status" > "$ev/cases/wrapper-input-relation-capture-helper-exit-code.txt"
fi

if [[ "$input_relation_frame_mode" == 1 ]]; then
  printf '{"requested":true}\n' > "$ev/cases/wrapper-input-relation-frame-capture-request.json"
  input_relation_frame_status=0
  stage wrapper-input-relation-frame-capture python3 "$proof_root/research/challenge-8/overnight-assume-actual/capture.py" \
    --tool-home "$source_home" --schema "$schema" \
    --compiler-sysroot "$compiler_sysroot" --evidence "$ev/cases/wrapper-input-relation-frame-capture" \
    --deadline-epoch "$deadline" --wrapper-input-relation-frame --fingerprint || input_relation_frame_status=$?
  printf '%s\n' "$input_relation_frame_status" > "$ev/cases/wrapper-input-relation-frame-capture-helper-exit-code.txt"
fi

if [[ "$input_relation_shadow_mode" == 1 ]]; then
  printf '{"requested":true}\n' > "$ev/cases/wrapper-input-relation-shadow-capture-request.json"
  input_relation_shadow_status=0
  stage wrapper-input-relation-shadow-capture python3 "$proof_root/research/challenge-8/overnight-assume-actual/capture.py" \
    --tool-home "$source_home" --schema "$schema" \
    --compiler-sysroot "$compiler_sysroot" --evidence "$ev/cases/wrapper-input-relation-shadow-capture" \
    --deadline-epoch "$deadline" --wrapper-input-relation-shadow --fingerprint || input_relation_shadow_status=$?
  printf '%s\n' "$input_relation_shadow_status" > "$ev/cases/wrapper-input-relation-shadow-capture-helper-exit-code.txt"
fi

if [[ "$coordination_mode" == 1 ]]; then
  printf '{"requested":true}\n' > "$ev/cases/coordination-regression-request.json"
  coordination_status=0
  stage coordination-regression python3 "$cloud_dir/coordination-regression.py" \
    --cloud-dir "$cloud_dir" --work-root "$work_root/coordination-regression" \
    --output "$ev/cases/coordination-regression" || coordination_status=$?
  printf '%s\n' "$coordination_status" > "$ev/cases/coordination-regression-helper-exit-code.txt"
fi

if [[ "$nested_order_mode" == 1 ]]; then
  printf '{"requested":true}\n' > "$ev/cases/nested-proof-order-test-request.json"
  nested_status=0
  stage nested-proof-order-test bash "$cloud_dir/run-nested-proof-order-test.sh" \
    --production-source "$source_home" --production-applied-patch "$ev/refreshed-applied.patch" \
    --stock-home "$stock_home" --compiler-sysroot "$compiler_sysroot" \
    --evidence "$ev/cases/nested-proof-order-test" --deadline-epoch "$deadline" \
    --proof-root "$proof_root" --work-root "$work_root" --cloud-dir "$cloud_dir" || nested_status=$?
  printf '%s\n' "$nested_status" > "$ev/cases/nested-proof-order-test-helper-exit-code.txt"
fi

if [[ "$ast_probe_mode" == 1 ]]; then
  printf '{"requested":true}\n' > "$ev/cases/sort4-ast-probe-request.json"
  ast_status=0
  stage sort4-ast-probe bash "$cloud_dir/run-sort4-ast-probe.sh" \
    --production-source "$source_home" --production-applied-patch "$ev/refreshed-applied.patch" \
    --stock-home "$stock_home" --compiler-sysroot "$compiler_sysroot" \
    --evidence "$ev/cases/sort4-ast-probe" --deadline-epoch "$deadline" \
    --proof-root "$proof_root" --work-root "$work_root" --cloud-dir "$cloud_dir" || ast_status=$?
  printf '%s\n' "$ast_status" > "$ev/cases/sort4-ast-probe-helper-exit-code.txt"
fi

if [[ "$controls_mode" == 1 ]]; then
  printf '{"requested":true}\n' > "$ev/cases/owner17-controls-request.json"
  controls_status=0
  stage owner17-controls python3 "$cloud_dir/o26-refresh-controls.py" \
    --repo "$proof_root" --cloud-dir "$cloud_dir" --evidence "$ev" \
    --tool-home "$source_home" --schema "$schema" \
    --compiler-sysroot "$compiler_sysroot" --deadline-epoch "$deadline" || controls_status=$?
  printf '%s\n' "$controls_status" > "$ev/cases/owner17-controls-helper-exit-code.txt"
fi

if [[ "$a1_mode" == 1 ]]; then
  printf '{"requested":true}\n' > "$ev/cases/a1-isolated-test-request.json"
  a1_status=0
  stage a1-isolated-test bash "$cloud_dir/run-a1-isolated-test.sh" \
    --production-source "$source_home" --production-applied-patch "$ev/refreshed-applied.patch" \
    --stock-home "$stock_home" --compiler-sysroot "$compiler_sysroot" \
    --evidence "$ev/cases/a1-isolated-test" --deadline-epoch "$deadline" \
    --proof-root "$proof_root" --work-root "$work_root" --cloud-dir "$cloud_dir" || a1_status=$?
  printf '%s\n' "$a1_status" > "$ev/cases/a1-isolated-test-helper-exit-code.txt"
fi

if [[ "$relocate_mode" == 1 ]]; then
  printf '{"requested":true}\n' > "$ev/cases/cut-relocate-request.json"
  relocate_status=0
  stage cut-relocate bash "$cloud_dir/run-cut-relocate.sh" \
    --production-source "$source_home" --production-applied-patch "$ev/refreshed-applied.patch" \
    --stock-home "$stock_home" --compiler-sysroot "$compiler_sysroot" \
    --evidence "$ev/cases/cut-relocate" --deadline-epoch "$deadline" \
    --proof-root "$proof_root" --work-root "$work_root" --cloud-dir "$cloud_dir" || relocate_status=$?
  printf '%s\n' "$relocate_status" > "$ev/cases/cut-relocate-helper-exit-code.txt"
fi

if [[ "$strict_cut_controls_mode" == 1 ]]; then
  printf '{"requested":true}\n' > "$ev/cases/strict-cut-controls-request.json"
  strict_cut_controls_status=0
  if [[ "$relocate_status" == 0 ]]; then
    strict_cut_controls_runner="$cloud_dir/run-strict-cut-controls.sh"
    if [[ "$reuse_strict_matrix_mode" == 1 ]]; then
      strict_cut_controls_runner="$cloud_dir/run-strict-cut-reuse-controls.sh"
    fi
    stage strict-cut-controls bash "$strict_cut_controls_runner" \
      --production-source "$source_home" --production-applied-patch "$ev/refreshed-applied.patch" \
      --stock-home "$stock_home" --compiler-sysroot "$compiler_sysroot" \
      --evidence "$ev/cases/strict-cut-controls" --deadline-epoch "$deadline" \
      --proof-root "$proof_root" --work-root "$work_root" --cloud-dir "$cloud_dir" \
      --relocation-evidence "$ev/cases/cut-relocate" || strict_cut_controls_status=$?
  else
    printf 'CUT relocation prerequisite failed: exit=%s\n' "$relocate_status" \
      > "$ev/strict-cut-controls.log"
    strict_cut_controls_status=2
  fi
  printf '%s\n' "$strict_cut_controls_status" \
    > "$ev/cases/strict-cut-controls-helper-exit-code.txt"
fi

if [[ "$strict_cut_false_posts_mode" == 1 ]]; then
  printf '{"requested":true}\n' > "$ev/cases/strict-cut-false-posts-request.json"
  strict_cut_false_posts_status=0
  if [[ "$strict_cut_controls_status" == 0 ]]; then
    stage strict-cut-false-posts bash "$cloud_dir/run-strict-cut-false-posts.sh" \
      --production-source "$source_home" --production-applied-patch "$ev/refreshed-applied.patch" \
      --stock-home "$stock_home" --compiler-sysroot "$compiler_sysroot" \
      --evidence "$ev/cases/strict-cut-false-posts" --deadline-epoch "$deadline" \
      --proof-root "$proof_root" --work-root "$work_root" --cloud-dir "$cloud_dir" \
      --relocation-evidence "$ev/cases/cut-relocate" \
      --controls-evidence "$ev/cases/strict-cut-controls" || strict_cut_false_posts_status=$?
  else
    printf 'strictCUT controls prerequisite failed: exit=%s\n' "$strict_cut_controls_status" \
      > "$ev/strict-cut-false-posts.log"
    strict_cut_false_posts_status=2
  fi
  printf '%s\n' "$strict_cut_false_posts_status" \
    > "$ev/cases/strict-cut-false-posts-helper-exit-code.txt"
fi

if [[ "$sort4_mode" == 1 ]]; then
  printf '{"requested":true}\n' > "$ev/cases/actual-sort4-request.json"
  sort4_status=0
  stage actual-sort4 python3 "$cloud_dir/actual-sort4-capture.py" \
    --proof-root "$proof_root" --cloud-dir "$cloud_dir" --tool-home "$source_home" \
    --schema "$schema" --compiler-sysroot "$compiler_sysroot" \
    --evidence "$ev/cases/actual-sort4" --deadline-epoch "$deadline" || sort4_status=$?
  printf '%s\n' "$sort4_status" > "$ev/cases/actual-sort4-helper-exit-code.txt"
fi

current_stage=audit
audit_result 0 complete
