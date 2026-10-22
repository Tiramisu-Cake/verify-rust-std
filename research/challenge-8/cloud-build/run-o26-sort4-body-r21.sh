#!/usr/bin/env bash
# R21 isolated full actual sort4-body transport lane. Source-only candidate;
# all setup, extraction, compilation, export, reconstruction and verification
# occur only when this runner is dispatched in the authorized Cloud lane.
set -euo pipefail

proof_root=${PROOF_ROOT:-/workspace/proof}
infra_root=${INFRA_ROOT:-/workspace/infra}
cloud_dir=${INFRA_CLOUD_DIR:-$infra_root/research/challenge-8/cloud-build}
work_root=${WORK_ROOT:-/workspace/smallsort-work}
evidence_root=${EVIDENCE_ROOT:-/workspace/evidence}
deadline=${SMALLSORT_DEADLINE_EPOCH:?SMALLSORT_DEADLINE_EPOCH is required}
current_sha=${PROOF_SHA:?PROOF_SHA is required}
infra_sha=${INFRA_SHA:?INFRA_SHA is required}

[[ "$#" == 1 && "$1" == o26-sort4-body-r21 &&
   "${LANE:-}" == o26-sort4-body-r21 &&
   "${SORT4_R21_BODY_PHASE_ID:-}" == SORT4-ACTUAL-SELECT-2026-10-23-R21 ]] || exit 2
[[ "${SORT4_A1_PHASE_ID:-}" == SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17 &&
   "${SORT4_A1_AUTHORIZATION_PHASE_ID:-}" == SORT4-ACTUAL-C2-2026-10-21-R17 &&
   "${SORT4_A1_CHECKED_TRAIT_CONTRACT:-}" == 1 &&
   "${SORT4_A1_PROFILE_SHA256:-}" =~ ^[0-9a-f]{64}$ ]] || exit 2
[[ "${SMALLSORT_EXECUTION_PROVIDER:-}" == cloud-build && -z "${GITHUB_ACTIONS:-}" ]] || exit 2

# Only the four declared backend protocol/profile variables and this fresh
# execution marker may select an A1 route. Refuse ambient summaries and every
# unrelated R20/R17/R16 actual-body route marker.
while IFS= read -r name; do
  case "$name" in
    SORT4_A1_PHASE_ID|SORT4_A1_AUTHORIZATION_PHASE_ID|\
    SORT4_A1_CHECKED_TRAIT_CONTRACT|SORT4_A1_PROFILE_SHA256|\
    SORT4_R21_BODY_PHASE_ID) ;;
    SORT4_A1_*|SORT4_R*|SORT4_ACTUAL_*)
      printf 'ambient unrelated A1/actual route marker refused: %s\n' "$name" >&2
      exit 2
      ;;
  esac
done < <(compgen -e)

for path in "$proof_root" "$infra_root" "$work_root" "$evidence_root"; do
  [[ "$path" == /workspace/* ]] || { printf 'path outside /workspace: %s\n' "$path" >&2; exit 2; }
done
[[ "$(git -C "$proof_root" rev-parse HEAD)" == "$current_sha" &&
   "$(git -C "$infra_root" rev-parse HEAD)" == "$infra_sha" && -d "$cloud_dir" ]] || exit 2

mkdir -p "$work_root" "$evidence_root"
ev="$evidence_root/allprooflogs"
[[ ! -e "$ev" ]] || { printf 'R21 body evidence already exists: %s\n' "$ev" >&2; exit 2; }
mkdir "$ev"
current_stage=preflight
audit_result() {
  python3 "$cloud_dir/body-route-r21.py" audit --proof-root "$proof_root" \
    --infra-root "$infra_root" \
    --evidence "$ev" --output "$evidence_root/proof-audit.json" \
    --profile-sha256 "$SORT4_A1_PROFILE_SHA256" \
    --runner-exit "$1" --failed-stage "$2"
}
on_exit() {
  status=$?
  if [[ ! -f "$evidence_root/proof-audit.json" ]]; then
    audit_result "$status" "$current_stage" || true
  fi
  exit "$status"
}
trap on_exit EXIT
mkdir "$ev/cases"

stage() {
  local name=$1; shift
  current_stage=$name
  local seconds code=0
  seconds=$((deadline - $(date +%s)))
  (( seconds > 0 )) || { printf 'deadline elapsed\n' >&2; exit 124; }
  /usr/bin/time -v -o "$ev/$name-resources.txt" \
    timeout --signal=TERM --kill-after=10s "${seconds}s" "$@" \
    > "$ev/$name.log" 2>&1 || code=$?
  printf '%s\n' "$code" > "$ev/$name-exit-code.txt"
  cat "$ev/$name.log"
  (( code == 0 )) || return "$code"
}

CLOUD_BUILD_ID=${CLOUD_BUILD_ID:?} \
CLOUD_BUILD_PROJECT_ID=${CLOUD_BUILD_PROJECT_ID:?} \
CLOUD_BUILD_REGION=${CLOUD_BUILD_REGION:?} \
  python3 "$cloud_dir/provider.py" > "$ev/provider.json"

# Validate fresh profile, source and implementation pins before package work.
python3 "$cloud_dir/body-route-r21.py" preflight --proof-root "$proof_root" \
  --infra-root "$infra_root" \
  --profile-sha256 "$SORT4_A1_PROFILE_SHA256" --evidence "$ev"

# Retain the O26 provider-guard overlay and source-only preflight from the R20
# setup. Neither applies the branch-selected certificate refresh patch.
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

current_stage=frozen-manifest
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
current_stage=stock-archive-checksum
printf '%s  %s\n' 5ad2a65997457fd5996a27f93107ef7e52c90c0d12b63b6e67f7acbc73e90efd \
  "$stock_archive" | sha256sum -c - > "$ev/archive-sha256.log"
stage extract tar -xzf "$stock_archive" -C "$task_temp"
stage source-checkout git clone --depth 1 --branch 26.10 \
  https://github.com/verifast/verifast.git "$source_home"
current_stage=tool-source-identity
[[ "$(git -C "$source_home" rev-parse HEAD)" == f76012fb518703b1d98e243ac4f487f16877cfcb ]] || exit 2
[[ "$(sha256sum "$schema" | cut -d' ' -f1)" == f48fcf29b99717c2e0cb37d4708b47eccaa3270b999e4a84093e37fbd51b7469 ]] || exit 2
rustup_init="$work_root/rustup-init-1.28.2"
stage rustup-init-download curl -fL --retry 2 -o "$rustup_init" \
  https://static.rust-lang.org/rustup/archive/1.28.2/x86_64-unknown-linux-gnu/rustup-init
current_stage=rustup-init-checksum
printf '%s  %s\n' 20a06e644b0d9bd2fbdbfd52d42540bdde820ea7df86e92e533c073da0cdd43c \
  "$rustup_init" | sha256sum -c - > "$ev/rustup-init-sha256.log"
chmod +x "$rustup_init"
stage rustup-init "$rustup_init" -y --no-modify-path --default-toolchain none --profile minimal
stage compiler rustup toolchain install "$RUSTUP_TOOLCHAIN" --profile minimal \
  --component rustc-dev --component llvm-tools-preview --component rust-src
current_stage=compiler-identity
compiler_sysroot=$(rustc --print sysroot)
rustc --version --verbose > "$ev/compiler-version.txt"
rg -q '^commit-hash: f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f$' "$ev/compiler-version.txt"
export LD_LIBRARY_PATH="$compiler_sysroot/lib:$stock_home/bin:${LD_LIBRARY_PATH:-}"

current_stage=frozen-patch-inventory
mapfile -t patch_rows < <(python3 - "$manifest" <<'PATCHES'
import json,sys
for row in json.load(open(sys.argv[1]))['patches_in_application_order']:
 print(f"{row['component']} {row['path']} {row['sha256']}")
PATCHES
)
for row in "${patch_rows[@]}"; do
  read -r number relative expected <<< "$row"
  patch="$proof_root/research/challenge-8/$relative"
  current_stage="patch-$number-identity"
  [[ "$(sha256sum "$patch" | cut -d' ' -f1)" == "$expected" ]] || exit 2
  stage "patch-$number-check" git -C "$source_home" apply --check "$patch"
  stage "patch-$number-apply" git -C "$source_home" apply "$patch"
done
current_stage=frozen-applied-identity
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
current_stage=refresh-manifest
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
  current_stage="patch-$number-identity"
  [[ "$(sha256sum "$patch" | cut -d' ' -f1)" == "$expected" ]] || exit 2
  stage "refresh-$number-check" git -C "$source_home" apply --check "$patch"
  stage "refresh-$number-apply" git -C "$source_home" apply "$patch"
done
current_stage=refreshed-source-identity
git -C "$source_home" diff --name-only > "$ev/refreshed-modified-files.txt"
cmp "$ev/modified-files.txt" "$ev/refreshed-modified-files.txt"
git -C "$source_home" diff > "$ev/refreshed-applied.patch"
[[ "$(sha256sum "$source_home/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml" | cut -d' ' -f1)" == 0862e635075edd06a827c567710a3e1125ac03aa122e95149db755a1fddce48a ]] || exit 2

deps_archive="$task_temp/vfdeps-adf88dc-linux.txz"
stage deps-download curl -fL --retry 2 -o "$deps_archive" \
  https://github.com/verifast/vfdeps/releases/download/25.01/vfdeps-adf88dc-linux.txz
current_stage=deps-archive-checksum
printf '%s  %s\n' 8d022c93d51a1d13ec1e782d767c60462405f6865d5ee416f82d6234e93ee580 \
  "$deps_archive" | sha256sum -c - > "$ev/deps-sha256.log"
stage deps-extract tar -xjf "$deps_archive" -C "$work_root"
current_stage=deps-layout
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
current_stage=stock-binary-identity
cp -an "$stock_home/bin/." "$source_home/bin/"
if [[ -d "$stock_home/lib" ]]; then
  mkdir -p "$source_home/lib"
  cp -an "$stock_home/lib/." "$source_home/lib/"
fi
for binary in vf-rust-mir-exporter refinement-checker vf-cxx-ast-exporter libz3.so; do
  cmp "$stock_home/bin/$binary" "$source_home/bin/$binary"
done
current_stage=tool-spec-identity
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
current_stage=console-linkage
ldd "$source_home/bin/verifast" > "$ev/console-ldd.txt"
! rg -q 'not found' "$ev/console-ldd.txt"

mkdir -p "$ev/body-route"
stage actual-body-entry python3 "$cloud_dir/sort4-caller-entry-native/a1-entry-r21.py" \
  --production-source "$source_home" \
  --production-applied-patch "$ev/refreshed-applied.patch" \
  --stock-home "$stock_home" --compiler-sysroot "$compiler_sysroot" \
  --evidence "$ev/body-route" --proof-root "$proof_root" \
  --work-root "$work_root" --cloud-dir "$cloud_dir" \
  --deadline-epoch "$deadline"

current_stage=audit
audit_result 0 complete
