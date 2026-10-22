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
   "${SORT4_R20_CALLEE_PHASE_ID:-}" == SORT4-ACTUAL-SELECT-2026-10-22-R20 ]] || exit 2
# The R20 certificate opt-in is per proof call only, never ambient.
[[ -z "${SORT4_R20_FINAL_SELECT_REPAIR:-}" ]] || exit 2
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
  python3 "$cloud_dir/select-callee-r20.py" audit --evidence "$ev" \
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
# R20 opt-in certificate refresh for the checked merged final-select repair;
# without SORT4_R20_FINAL_SELECT_REPAIR=1 the translator keeps the O26 pins.
r20_patch="$proof_root/research/challenge-8/overnight-assume-actual/verifast-r20-final-select-branch-26.10.patch"
[[ "$(sha256sum "$r20_patch" | cut -d' ' -f1)" == 74077492696785f0bdfaf4a74101356aa13d45034f8616591693f6d5d089831c ]] || exit 2
stage r20-refresh-check git -C "$source_home" apply --check "$r20_patch"
stage r20-refresh-apply git -C "$source_home" apply "$r20_patch"
[[ "$(sha256sum "$source_home/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml" | cut -d' ' -f1)" == 82741fb5bce3ee1ec46ebfad55dc0d1b743c2fd68917f20381dbd66553092b5f ]] || exit 2


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
# Baseline reproduction of the recorded blocker; its verifier exit is data.
stage candidate-proof python3 "$cloud_dir/o26-refresh-recipe.py" proof \
  --repo "$proof_root" --cloud-dir "$cloud_dir" --evidence "$ev" \
  --tool-home "$source_home" --schema "$schema" \
  --compiler-sysroot "$compiler_sysroot" --deadline-epoch "$deadline"
# Repair variants are not run here: the pinned nine-body certificates fix the
# exact verified source SHA and ghost list, so ghost-repaired copies would be
# refused before the final select. They need a reviewed certificate refresh.
# S3b: proof of the branch-repaired unit under the opt-in refreshed certificate,
# plus refusal controls (no opt-in; opt-in without repair), classified per row.
# The baseline candidate-proof runs on the patched translator with opt-in off.
stage r20-repair-proof python3 "$cloud_dir/select-callee-r20.py" proof \
  --repo "$proof_root" --cloud-dir "$cloud_dir" --evidence "$ev" \
  --tool-home "$source_home" --schema "$schema" \
  --compiler-sysroot "$compiler_sysroot" --deadline-epoch "$deadline"

current_stage=audit
audit_result 0 complete
