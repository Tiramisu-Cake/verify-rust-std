#!/usr/bin/env bash
set -euo pipefail
[[ "${GITHUB_ACTIONS:-}" == true && "${RUNNER_ENVIRONMENT:-}" == github-hosted && "${RUNNER_OS:-}" == Linux ]] || exit 2
[[ "${GITHUB_REF:-}" == refs/heads/research/overnight-select-sort4-26.10 ]] || exit 2
repo=$(git rev-parse --show-toplevel)
cd "$repo"
ev="$repo/research-results/overnight-s6"
mkdir -p "$ev"
if [[ "${1:-}" != --inside ]]; then
 remaining=$((1080 - $(date +%s) + OVERNIGHT_JOB_STARTED_EPOCH))
 (( remaining > 0 )) || exit 124
 set +e
 timeout --signal=TERM --kill-after=10s "${remaining}s" bash "$0" --inside 2>&1 | tee "$ev/execution.log"
 code=${PIPESTATUS[0]}
 printf '%s\n' "$code" > "$ev/exit-code.txt"
 exit "$code"
fi
stage() {
 local name=$1; shift
 local code=0
 /usr/bin/time -v -o "$ev/$name-resources.txt" "$@" > "$ev/$name.log" 2>&1 || code=$?
 printf '%s\n' "$code" > "$ev/$name-exit-code.txt"
 cat "$ev/$name.log"
 return "$code"
}
export RUSTUP_TOOLCHAIN=nightly-2026-09-25
task_temp="$RUNNER_TEMP/overnight-s6"
mkdir -p "$task_temp"
stock_archive="$task_temp/verifast-26.10-linux.tar.gz"
stock_home="$task_temp/verifast-26.10"
source_home="$task_temp/source"
patch_file="$repo/research/challenge-8/overnight-s6/verifast-s6-26.10-candidate.patch"
cfg_patch="$repo/research/challenge-8/verifast-manuallydrop-new-cfg-2610.patch"
printf 'Proof SHA: %s\nProfile: experimental-s6-26.10-v1+cfg\n' "$(git rev-parse HEAD)" > "$ev/environment.txt"
sha256sum "$patch_file" >> "$ev/environment.txt"
stage download curl -fL --retry 2 -o "$stock_archive" https://github.com/verifast/verifast/releases/download/26.10/verifast-26.10-linux.tar.gz
printf '%s  %s\n' 5ad2a65997457fd5996a27f93107ef7e52c90c0d12b63b6e67f7acbc73e90efd "$stock_archive" | sha256sum -c -
stage extract tar -xzf "$stock_archive" -C "$task_temp"
stage source-checkout git clone --depth 1 --branch 26.10 https://github.com/verifast/verifast.git "$source_home"
[[ "$(git -C "$source_home" rev-parse HEAD)" == f76012fb518703b1d98e243ac4f487f16877cfcb ]] || exit 2
printf '%s  %s\n' f48fcf29b99717c2e0cb37d4708b47eccaa3270b999e4a84093e37fbd51b7469 "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" | sha256sum -c -
stage packages sudo apt-get install --yes --no-install-recommends build-essential m4 patch unzip capnproto
stage compiler rustup toolchain install "$RUSTUP_TOOLCHAIN" --profile minimal --component rustc-dev --component llvm-tools-preview --component rust-src
compiler_sysroot=$(rustc --print sysroot)
export LD_LIBRARY_PATH="$compiler_sysroot/lib:$stock_home/bin:${LD_LIBRARY_PATH:-}"
stage stock-baseline python3 research/challenge-8/check-stock-2610.py --tool-home "$stock_home" --schema "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" --compiler-sysroot "$compiler_sysroot" --evidence "$ev/stock/cases" --deadline-epoch "$((OVERNIGHT_JOB_STARTED_EPOCH+1000))"
export SORT4_SELECT_PROFILE=experimental-s6-26.10-v1
stage s6-stock-capture python3 research/challenge-8/overnight-s6/diagnose-s6.py --tool-home "$stock_home" --schema "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" --compiler-sysroot "$compiler_sysroot" --evidence "$ev/s6-stock-capture"
stage patch-check git -C "$source_home" apply --check "$patch_file"
stage patch-apply git -C "$source_home" apply "$patch_file"
stage cfg-patch-check git -C "$source_home" apply --check "$cfg_patch"
stage cfg-patch-apply git -C "$source_home" apply "$cfg_patch"
git -C "$source_home" diff > "$ev/applied.patch"
printf '%s\n' bin/rust/std/lib.rsspec src/rust_frontend/vf_mir_translator/vf_mir_translator.ml > "$ev/allowed-files.txt"
git -C "$source_home" diff --name-only > "$ev/modified-files.txt"
cmp "$ev/allowed-files.txt" "$ev/modified-files.txt"
deps_archive="$task_temp/vfdeps-adf88dc-linux.txz"
stage deps-download curl -fL --retry 2 -o "$deps_archive" https://github.com/verifast/vfdeps/releases/download/25.01/vfdeps-adf88dc-linux.txz
printf '%s  %s\n' 8d022c93d51a1d13ec1e782d767c60462405f6865d5ee416f82d6234e93ee580 "$deps_archive" | sha256sum -c -
stage deps-extract sudo tar -xjf "$deps_archive" -C /
ln -s /vfdeps-adf88dc /tmp/vfdeps-adf88dc
export PATH="/tmp/vfdeps-adf88dc/bin:$PATH"
export CAPNP_INC_DIR=/tmp/vfdeps-adf88dc/include
export LD_LIBRARY_PATH="$compiler_sysroot/lib:$source_home/bin:/tmp/vfdeps-adf88dc/lib:${LD_LIBRARY_PATH:-}"
stage decoder-install cargo install --locked --git https://github.com/btj/capnpc-ocaml-decoder --rev 2d6606d9b59cd0c88a66729f3f076c10c0c8e0b2
stage console-build make -C "$source_home/src" ../bin/verifast WITHOUT_LABLGTK=yes VERBOSE=yes
cp -an "$stock_home/bin/." "$source_home/bin/"
if [[ -d "$stock_home/lib" ]]; then mkdir -p "$source_home/lib"; cp -an "$stock_home/lib/." "$source_home/lib/"; fi
for binary in vf-rust-mir-exporter refinement-checker vf-cxx-ast-exporter libz3.so; do cmp "$stock_home/bin/$binary" "$source_home/bin/$binary"; done
python3 - "$stock_home" "$source_home" "$ev" <<'AUDIT'
import hashlib,json,pathlib,sys
stock,src,ev=map(pathlib.Path,sys.argv[1:]); h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a={str(p.relative_to(stock)):p for p in (stock/'bin/rust').rglob('*.rsspec')}
b={str(p.relative_to(src)):p for p in (src/'bin/rust').rglob('*.rsspec')}
assert a.keys()==b.keys()
assert all(a[k].read_bytes()==b[k].read_bytes() for k in a if k!='bin/rust/std/lib.rsspec')
assert a['bin/rust/std/lib.rsspec'].read_bytes()!=b['bin/rust/std/lib.rsspec'].read_bytes()
(ev/'spec-audit.json').write_text(json.dumps({k:h(a[k]) for k in a},indent=2)+'\n')
(ev/'profile-hashes.json').write_text(json.dumps({k:h(src/k) for k in ['bin/verifast','bin/vf-rust-mir-exporter','bin/refinement-checker','bin/rust/std/lib.rsspec','src/rust_frontend/vf_mir/vf_mir.capnp','src/rust_frontend/vf_mir_translator/vf_mir_translator.ml']},indent=2)+'\n')
AUDIT
{
 rustc --version --verbose
 capnp --version
 ocamlc -version
 dune --version
 sha256sum "$stock_archive" "$patch_file" "$source_home/bin/verifast" "$stock_home/bin/verifast"
} >> "$ev/environment.txt"
ldd "$source_home/bin/verifast" > "$ev/console-ldd.txt"
if rg -q 'not found' "$ev/console-ldd.txt"; then exit 2; fi
export SORT4_SELECT_PROFILE=experimental-s6-26.10-v1
stage s6-diagnostic python3 research/challenge-8/overnight-s6/diagnose-s6.py --tool-home "$source_home" --schema "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" --compiler-sysroot "$compiler_sysroot" --evidence "$ev/s6-diagnostic"
