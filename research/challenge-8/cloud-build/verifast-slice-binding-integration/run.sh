#!/usr/bin/env bash
# Cloud-only slice binding, Bool, native C1-C4, and ZST on one tool tree.
set -euo pipefail

[[ "${SMALLSORT_EXECUTION_PROVIDER:-}" == cloud-build &&
   "${LANE:-}" == verifast-slice-binding-integration && -z "${GITHUB_ACTIONS:-}" ]] || exit 2
proof_root=${PROOF_ROOT:-/workspace/proof}
infra_root=${INFRA_ROOT:-/workspace/infra}
cloud_dir=${INFRA_CLOUD_DIR:-$infra_root/research/challenge-8/cloud-build}
work_root=${WORK_ROOT:-/workspace/smallsort-work}
evidence_root=${EVIDENCE_ROOT:-/workspace/evidence}
deadline=${SMALLSORT_DEADLINE_EPOCH:?}
current_sha=${PROOF_SHA:?}
for path in "$proof_root" "$infra_root" "$cloud_dir" "$work_root" "$evidence_root"; do
  [[ "$path" == /workspace/* ]] || exit 2
done
[[ "$(git -C "$proof_root" rev-parse HEAD)" == "$current_sha" ]] || exit 2
[[ ! -e "$evidence_root/allprooflogs/cases/integration" ]] || exit 2
mkdir -p "$work_root" "$evidence_root/allprooflogs/cases/integration"
stage_ev="$evidence_root/allprooflogs"
ev="$stage_ev/cases/integration"
runner="$cloud_dir/verifast-c4-select-integration/driver.py"
native_runner="$cloud_dir/verifast-native-zst-integration/adapter.py"
slice_runner="$cloud_dir/verifast-slice-binding-integration/runner.py"
manifest="$proof_root/research/challenge-8/cloud-build/verifast-slice-binding-integration/manifest.json"
source_home="$work_root/verifast-slice-binding-source"
stock_home="$work_root/verifast-26.10"
schema="$source_home/src/rust_frontend/vf_mir/vf_mir.capnp"
export RUSTUP_HOME="$work_root/rustup" CARGO_HOME="$work_root/cargo"
export RUSTUP_TOOLCHAIN=nightly-2026-09-25 TMPDIR="$work_root/tmp"
export SORT4_SELECT_PROFILE=experimental-s6-26.10-v1
mkdir -p "$RUSTUP_HOME" "$CARGO_HOME" "$TMPDIR"
export PATH="$CARGO_HOME/bin:$PATH"
current_stage=preflight
trap 'code=$?; if [[ ! -f "$ev/result.json" && ! -f "$stage_ev/cases/native-zst-supplement/result.json" ]]; then python3 "$runner" failure --evidence "$ev" --stage "$current_stage" --exit-code "$code" || true; fi' EXIT

remaining() {
  local seconds=$((deadline - $(date +%s) - 20))
  (( seconds > 0 )) || exit 124
  printf '%s' "$seconds"
}
stage() {
  local name=$1 code=0; shift
  current_stage=$name
  /usr/bin/time -v -o "$stage_ev/$name-resources.txt" \
    timeout --signal=TERM --kill-after=10s "$(remaining)s" "$@" \
    > "$stage_ev/$name.log" 2>&1 || code=$?
  printf '%s\n' "$code" > "$stage_ev/$name-exit-code.txt"
  cat "$stage_ev/$name.log"
  (( code == 0 )) || return "$code"
}

stage provider env CLOUD_BUILD_ID="${CLOUD_BUILD_ID:?}" \
  CLOUD_BUILD_PROJECT_ID="${CLOUD_BUILD_PROJECT_ID:?}" \
  CLOUD_BUILD_REGION="${CLOUD_BUILD_REGION:?}" \
  python3 "$cloud_dir/provider.py"
cp "$stage_ev/provider.log" "$stage_ev/provider.json"
stage slice-source-delivery python3 "$slice_runner" materialize-slice \
  --proof-root "$proof_root" --cloud-dir "$cloud_dir" \
  --evidence "$ev" --manifest "$manifest"
stage input-preflight python3 "$runner" preflight --proof-root "$proof_root" \
  --manifest "$manifest" --evidence "$ev" --cloud-dir "$cloud_dir"
source_prepare_ev="$stage_ev/source-preparation"
[[ ! -e "$source_prepare_ev" && ! -L "$source_prepare_ev" ]] || exit 2
stage source-prepare python3 "$runner" source-prepare --proof-root "$proof_root" \
  --manifest "$manifest" --evidence "$source_prepare_ev" --cloud-dir "$cloud_dir"
stage native-source-prepare python3 "$native_runner" source-prepare \
  --proof-root "$proof_root" --cloud-dir "$cloud_dir" \
  --evidence "$source_prepare_ev/native" --manifest "$manifest"
stage slice-source-prepare python3 "$slice_runner" source-prepare \
  --proof-root "$proof_root" --cloud-dir "$cloud_dir" \
  --evidence "$source_prepare_ev/slice" --manifest "$manifest"
stage package-index apt-get update
stage packages-install apt-get install --yes --no-install-recommends \
  build-essential m4 patch unzip capnproto ripgrep time libgmp10 libmpfr6 \
  libgomp1 libffi8 libncurses6 libtinfo6 zlib1g libz3-4 libgtk-3-0 libgtksourceview-4-0
stage stock-download curl -fL --retry 2 -o "$work_root/verifast-26.10-linux.tar.gz" \
  https://github.com/verifast/verifast/releases/download/26.10/verifast-26.10-linux.tar.gz
printf '%s  %s\n' 5ad2a65997457fd5996a27f93107ef7e52c90c0d12b63b6e67f7acbc73e90efd \
  "$work_root/verifast-26.10-linux.tar.gz" | sha256sum -c - > "$ev/stock-sha256.log"
stage stock-extract tar -xzf "$work_root/verifast-26.10-linux.tar.gz" -C "$work_root"
stage source-checkout git clone --depth 1 --branch 26.10 \
  https://github.com/verifast/verifast.git "$source_home"
[[ "$(git -C "$source_home" rev-parse HEAD)" == f76012fb518703b1d98e243ac4f487f16877cfcb ]] || exit 2
[[ "$(sha256sum "$schema" | cut -d' ' -f1)" == f48fcf29b99717c2e0cb37d4708b47eccaa3270b999e4a84093e37fbd51b7469 ]] || exit 2
stage rustup-download curl -fL --retry 2 -o "$work_root/rustup-init-1.28.2" \
  https://static.rust-lang.org/rustup/archive/1.28.2/x86_64-unknown-linux-gnu/rustup-init
printf '%s  %s\n' 20a06e644b0d9bd2fbdbfd52d42540bdde820ea7df86e92e533c073da0cdd43c \
  "$work_root/rustup-init-1.28.2" | sha256sum -c - > "$ev/rustup-sha256.log"
chmod +x "$work_root/rustup-init-1.28.2"
stage rustup-init "$work_root/rustup-init-1.28.2" -y --no-modify-path --default-toolchain none --profile minimal
stage compiler rustup toolchain install "$RUSTUP_TOOLCHAIN" --profile minimal \
  --component rustc-dev --component llvm-tools-preview --component rust-src
compiler_sysroot=$(rustc --print sysroot)
rustc --version --verbose > "$ev/compiler-version.txt"
rg -q '^commit-hash: f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f$' "$ev/compiler-version.txt"
stage deps-download curl -fL --retry 2 -o "$work_root/vfdeps-adf88dc-linux.txz" \
  https://github.com/verifast/vfdeps/releases/download/25.01/vfdeps-adf88dc-linux.txz
printf '%s  %s\n' 8d022c93d51a1d13ec1e782d767c60462405f6865d5ee416f82d6234e93ee580 \
  "$work_root/vfdeps-adf88dc-linux.txz" | sha256sum -c - > "$ev/deps-sha256.log"
stage deps-extract tar -xjf "$work_root/vfdeps-adf88dc-linux.txz" -C "$work_root"
deps_home="$work_root/vfdeps-adf88dc"
[[ -d "$deps_home" ]] || exit 2
for prefix in /vfdeps-adf88dc /tmp/vfdeps-adf88dc; do
  if [[ ! -e "$prefix" ]]; then ln -s "$deps_home" "$prefix"
  elif [[ "$(readlink -f "$prefix")" != "$deps_home" ]]; then exit 2; fi
done
export PATH="$deps_home/bin:$PATH" CAPNP_INC_DIR="$deps_home/include"
stage numeric-transport-compile ocamlfind ocamlc -package num -linkpkg \
  -o "$work_root/numeric-transport-check" "$cloud_dir/verifast-c4-select-integration/numeric-transport-check.ml"
stage numeric-transport-check "$work_root/numeric-transport-check"
export LD_LIBRARY_PATH="$compiler_sysroot/lib:$source_home/bin:$deps_home/lib:${LD_LIBRARY_PATH:-}"
stage decoder-install cargo install --locked --git \
  https://github.com/btj/capnpc-ocaml-decoder \
  --rev 2d6606d9b59cd0c88a66729f3f076c10c0c8e0b2
stage tool-apply python3 "$runner" apply --proof-root "$proof_root" \
  --manifest "$manifest" --evidence "$ev" --tool-home "$source_home"
stage native-tool-apply python3 "$native_runner" apply \
  --proof-root "$proof_root" --cloud-dir "$cloud_dir" \
  --evidence "$ev/native-tool" --manifest "$manifest" --tool-home "$source_home"
stage console-build make -C "$source_home/src" ../bin/verifast WITHOUT_LABLGTK=yes VERBOSE=yes
cp -an "$stock_home/bin/." "$source_home/bin/"
if [[ -d "$stock_home/lib" ]]; then
  mkdir -p "$source_home/lib"
  cp -an "$stock_home/lib/." "$source_home/lib/"
fi
for binary in vf-rust-mir-exporter refinement-checker vf-cxx-ast-exporter libz3.so; do
  cmp "$stock_home/bin/$binary" "$source_home/bin/$binary"
done
stage tool-pin python3 "$runner" pin --proof-root "$proof_root" \
  --manifest "$manifest" --evidence "$ev" --tool-home "$source_home"
current_stage=slice-binding
set +e
python3 "$slice_runner" run --proof-root "$proof_root" --cloud-dir "$cloud_dir" \
  --manifest "$manifest" --evidence "$stage_ev/cases/slice-binding" \
  --tool-home "$source_home" --compiler-sysroot "$compiler_sysroot" \
  --work-root "$work_root" --deadline-epoch "$deadline"
slice_exit=$?
current_stage=integration
export SORT4_C4_SELECT_DIAGNOSTIC_STAGE=affected-gates
python3 "$runner" run --proof-root "$proof_root" --cloud-dir "$cloud_dir" \
  --manifest "$manifest" --evidence "$ev" --tool-home "$source_home" \
  --compiler-sysroot "$compiler_sysroot" --deadline-epoch "$deadline"
integration_exit=$?
python3 "$native_runner" run --proof-root "$proof_root" --cloud-dir "$cloud_dir" \
  --manifest "$manifest" --evidence "$stage_ev/cases/native-zst" \
  --tool-home "$source_home" --compiler-sysroot "$compiler_sysroot" \
  --deadline-epoch "$deadline"
native_exit=$?
set -e
current_stage=combined-audit
python3 "$slice_runner" audit --proof-root "$proof_root" --cloud-dir "$cloud_dir" \
  --manifest "$manifest" --evidence "$stage_ev/cases/slice-binding" \
  --slice-exit "$slice_exit" --integration-exit "$integration_exit" \
  --native-exit "$native_exit"
