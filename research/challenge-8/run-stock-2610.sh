#!/usr/bin/env bash
# Stock26.10 only. All executable work is GitHub-hosted.
set -euo pipefail
[[ "${GITHUB_ACTIONS:-}" == true && "${RUNNER_ENVIRONMENT:-}" == github-hosted && "${RUNNER_OS:-}" == Linux ]] || exit 2
[[ "$(git branch --show-current)" == research/stock-26.10-baseline || "${GITHUB_REF:-}" == refs/heads/research/stock-26.10-baseline ]] || exit 2
repo=$(git rev-parse --show-toplevel)
cd "$repo"
ev="$repo/research-results/stock-2610"
mkdir -p "$ev"
if [[ "${1:-}" != --inside ]]; then
    remaining=$((540 - $(date +%s) + STOCK_JOB_STARTED_EPOCH))
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
task_temp="$RUNNER_TEMP/stock-2610"
mkdir -p "$task_temp"
stock_archive="$task_temp/verifast-26.10-linux.tar.gz"
stock_home="$task_temp/verifast-26.10"
source_home="$task_temp/source"
printf 'Proof SHA: %s\nProfile: stock-26.10-baseline-v1\nEffective patches: NONE\n' "$(git rev-parse HEAD)" > "$ev/environment.txt"
stage download curl -fL --retry 2 -o "$stock_archive" https://github.com/verifast/verifast/releases/download/26.10/verifast-26.10-linux.tar.gz
printf '%s  %s\n' 5ad2a65997457fd5996a27f93107ef7e52c90c0d12b63b6e67f7acbc73e90efd "$stock_archive" | sha256sum -c -
stage extract tar -xzf "$stock_archive" -C "$task_temp"
stage source-checkout git clone --depth 1 --branch 26.10 https://github.com/verifast/verifast.git "$source_home"
[[ "$(git -C "$source_home" rev-parse HEAD)" == f76012fb518703b1d98e243ac4f487f16877cfcb ]] || exit 2
git -C "$source_home" diff --exit-code
printf '%s  %s\n' f48fcf29b99717c2e0cb37d4708b47eccaa3270b999e4a84093e37fbd51b7469 "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" | sha256sum -c -
stage packages sudo apt-get install --yes --no-install-recommends capnproto
stage compiler rustup toolchain install "$RUSTUP_TOOLCHAIN" --profile minimal --component rustc-dev --component llvm-tools-preview --component rust-src
compiler_sysroot=$(rustc --print sysroot)
export LD_LIBRARY_PATH="$compiler_sysroot/lib:$stock_home/bin:${LD_LIBRARY_PATH:-}"
# Read-only source/spec consistency: no make, patches, custom decoder or rebuild.
python3 - "$stock_home" "$source_home" "$ev" "$compiler_sysroot" <<'AUDIT'
import hashlib,json,pathlib,sys
home,src,ev,sysroot=map(pathlib.Path,sys.argv[1:])
hashfile=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows={}
for p in sorted((home/'bin/rust').rglob('*')):
 if p.is_file():
  rel=p.relative_to(home)
  if not (src/rel).is_file() or p.read_bytes()!=(src/rel).read_bytes(): raise SystemExit(f'stock specification source mismatch: {rel}')
  rows[str(rel)]=hashfile(p)
(ev/'stock-spec-hashes.json').write_text(json.dumps(rows,indent=2)+'\n')
components=['src/rust_frontend/vf_mir/vf_mir.capnp','src/rust_frontend/vf_mir_decoder/dune','src/rust_frontend/vf_mir_translator/vf_mir_translator.ml','src/rust_frontend/vf_mir_exporter/src/main.rs']
for path in ('src/rust_frontend/vf_mir_exporter','src/rust_frontend/vf_mir_decoder','src/refinement_checker'):
 for p in sorted((src/path).rglob('*')):
  if p.is_file(): rows[str(p.relative_to(src))]=hashfile(p)
for rel in components: rows[rel]=hashfile(src/rel)
(ev/'source-component-hashes.json').write_text(json.dumps(rows,indent=2)+'\n')
rows={str(p.relative_to(home)):hashfile(p) for p in sorted((home/'bin').iterdir()) if p.is_file()}
(ev/'binary-hashes.json').write_text(json.dumps(rows,indent=2)+'\n')
rows={}
for rel in ['core/src/mem/mod.rs','core/src/mem/manually_drop.rs','core/src/mem/maybe_uninit.rs','core/src/ptr/mod.rs','core/src/slice/sort/shared/smallsort.rs']:
 a=pathlib.Path('library')/rel; b=sysroot/'lib/rustlib/src/rust/library'/rel
 rows[rel]={'repo':hashfile(a),'sysroot':hashfile(b),'equal':a.read_bytes()==b.read_bytes()}
(ev/'std-export-source.json').write_text(json.dumps({'sysroot':str(sysroot),'fixture_body_source':'repository library/core/src/mem/mod.rs exact forget body; external std crate metadata from nightly sysroot, not repository std build','files':rows},indent=2)+'\n')
AUDIT
{
 rustc --version --verbose
 capnp --version
 sha256sum "$stock_archive" "$stock_home/bin/verifast" "$stock_home/bin/vf-rust-mir-exporter" "$stock_home/bin/refinement-checker" "$stock_home/bin/rust/std/lib.rsspec"
 cat "$source_home/rust-toolchain.toml"
} >> "$ev/environment.txt"
ldd "$stock_home/bin/verifast" > "$ev/console-ldd.txt"
if rg -q 'not found' "$ev/console-ldd.txt"; then exit 2; fi
stage baseline python3 research/challenge-8/check-stock-2610.py --tool-home "$stock_home" --schema "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" --compiler-sysroot "$compiler_sysroot" --evidence "$ev/cases" --deadline-epoch "$((STOCK_JOB_STARTED_EPOCH + 530))"
