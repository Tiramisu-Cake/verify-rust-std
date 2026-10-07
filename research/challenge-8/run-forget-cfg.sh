#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0 OR MIT
# S7c physical-loc diagnosis and narrow CFG acceptance; hosted only.
set -euo pipefail
[[ "${GITHUB_ACTIONS:-}" == true && "${RUNNER_ENVIRONMENT:-}" == github-hosted && "${RUNNER_OS:-}" == Linux ]] || { echo 'requires GitHub-hosted Linux' >&2; exit 2; }
. /etc/os-release
[[ "$ID" == ubuntu && "$VERSION_ID" == 22.04 ]] || { echo 'requires Ubuntu22.04 build profile' >&2; exit 2; }
repo=$(git rev-parse --show-toplevel)
cd "$repo"
evidence="$repo/research-results/select-pointer"
budget=${1:?budget minutes required}
mode=${FORGET_CFG_MODE:?trace or accept required}
[[ "$mode" == trace || "$mode" == accept ]] || exit 2
ast_mode=1
[[ "$ast_mode" == 0 || "$ast_mode" == 1 ]] || { echo 'invalid generic AST selector' >&2; exit 2; }
export FORGET_GENERIC_AST="$ast_mode"
job_cap=${FORGET_CFG_JOB_CAP:?job cap required}
[[ "$job_cap" =~ ^[0-9]+$ ]] || exit 2
(( job_cap >= 3 && job_cap <= 7 )) || exit 2
[[ "$budget" == 30 ]] || { echo "requires workflow input 30; effective job cap $job_cap minutes" >&2; exit 2; }
if [[ "${2:-}" != --inside ]]; then
    [[ ! -e "$evidence" ]] || { echo 'refuse existing evidence' >&2; exit 2; }
    mkdir -p "$evidence"
    remaining=$((job_cap * 60 - 60))
    if [[ -n "${SORT4_CONSTRUCTOR_JOB_STARTED_EPOCH:-}" ]]; then
        [[ "$SORT4_CONSTRUCTOR_JOB_STARTED_EPOCH" =~ ^[0-9]+$ ]] || exit 2
        remaining=$((remaining - $(date +%s) + SORT4_CONSTRUCTOR_JOB_STARTED_EPOCH))
    fi
    (( remaining > 0 )) || exit 124
    set +e
    /usr/bin/time -v -o "$evidence/resources.txt" timeout --signal=TERM --kill-after=10s "${remaining}s" bash "$0" "$budget" --inside 2>&1 | tee "$evidence/execution.log"
    status=${PIPESTATUS[0]}
    set -e
    printf '%s\n' "$status" > "$evidence/exit-code.txt"
    exit "$status"
fi
[[ -d "$evidence" ]] || exit 2
run_stage() {
    local stage=$1
    shift
    set +e
    /usr/bin/time -v -o "$evidence/$stage-resources.txt" "$@" > "$evidence/$stage.log" 2>&1
    local result=$?
    set -e
    printf '%s\n' "$result" > "$evidence/$stage-exit-code.txt"
    cat "$evidence/$stage.log"
    return "$result"
}
diagnostic_status=0
run_diagnostic_stage() {
    local status=0
    run_stage "$@" || status=$?
    if (( status != 0 )); then diagnostic_status=1; fi
}
export RUSTUP_TOOLCHAIN=nightly-2026-02-05
source_pin=809de4596839b739dd999f9e462242c835e3af46
archive_sha=da1b619fa63ba73c12ce591638ced90fd2471add6f181d0e3310657fe4df98aa
deps_sha=8d022c93d51a1d13ec1e782d767c60462405f6865d5ee416f82d6234e93ee580
decoder_pin=2d6606d9b59cd0c88a66729f3f076c10c0c8e0b2
patch_file="$repo/research/challenge-8/verifast-select-pointer-drop.patch"
printf '%s  %s\n' c7cc08a995bac5879901f4fe08030f09d23bdfefb1a3ab5893be12a8dd1f8fc1 "$patch_file" | sha256sum -c -
task_temp="$RUNNER_TEMP/select-pointer"
[[ ! -e "$task_temp" ]] || exit 2
mkdir -p "$task_temp"
stock_archive="$task_temp/verifast-26.09-linux.tar.gz"
stock_home="$task_temp/verifast-26.09"
source_home="$task_temp/source"
{
    printf 'Source SHA: '; git rev-parse HEAD
    printf 'Profile: experimental-source-linked-select-pointer-drop-v4\nExperiment: S7c physical-loc diagnosis then narrow CFG acceptance, no actual redirect\nAST dump requested: %s\nBase source: %s\nCompiler: %s\nTarget: x86_64-unknown-linux-gnu\n' "$ast_mode" "$source_pin" "$RUSTUP_TOOLCHAIN"
    printf 'Budget: %s minutes including preparation/build/diagnostic; workflow input %s; cleanup reserve60 seconds\n' "$job_cap" "$budget"
    sha256sum "$patch_file" "$0" research/challenge-8/check-forget-generic.py research/challenge-8/forget-evidence-classifier.py research/challenge-8/SORT4-SELECT-FORGET-DESIGN.md
} > "$evidence/environment.txt"
run_stage python-syntax env PYTHONPYCACHEPREFIX="$task_temp/python-cache" python3 -m py_compile research/challenge-8/check-forget-generic.py research/challenge-8/forget-evidence-classifier.py
unset SORT4_MAYBEUNINIT_REPO_ROOT SORT4_SELECT_INTRINSIC_REPO_ROOT SORT4_POINTER_DROP_REPO_ROOT
export SORT4_SELECT_PROFILE=experimental-source-linked-select-pointer-drop-v4
run_stage construction-preflight python3 research/challenge-8/check-forget-generic.py --construction-preflight --evidence "$evidence/generic-construction-preflight"
run_stage stock-download curl -fL --retry 3 -o "$stock_archive" https://github.com/verifast/verifast/releases/download/26.09/verifast-26.09-linux.tar.gz
printf '%s  %s\n' "$archive_sha" "$stock_archive" | sha256sum -c -
run_stage stock-extract tar -xzf "$stock_archive" -C "$task_temp"
run_stage source-checkout git clone --depth 1 --branch 26.09 https://github.com/verifast/verifast.git "$source_home"
[[ "$(git -C "$source_home" rev-parse HEAD)" == "$source_pin" ]] || exit 2
run_stage patch-check git -C "$source_home" apply --check "$patch_file"
run_stage patch-apply git -C "$source_home" apply "$patch_file"
git -C "$source_home" diff > "$evidence/applied.patch"
git -C "$source_home" diff --name-only > "$evidence/modified-files.txt"
cmp "$evidence/applied.patch" "$patch_file"
# Reviewed translator + defined pointer-value predicate; no historical patches.
python3 - "$source_home" "$evidence" <<'PY'
import hashlib, pathlib, subprocess, sys, json
src,ev=map(pathlib.Path,sys.argv[1:])
allowed={'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml', 'bin/rust/std/lib.rsspec'}
changed=set((ev/'modified-files.txt').read_text().splitlines())
if changed != allowed: raise SystemExit(f'unexpected patch surface: {changed ^ allowed}')
identities={}
for rel in sorted(allowed):
 before=subprocess.check_output(['git','-C',str(src),'show',f'HEAD:{rel}'])
 after=(src/rel).read_bytes()
 identities[rel]={'before':hashlib.sha256(before).hexdigest(),'after':hashlib.sha256(after).hexdigest()}
(ev/'patch-source-identities.json').write_text(json.dumps(identities,indent=2)+'\n')
PY
run_stage compiler-install rustup toolchain install "$RUSTUP_TOOLCHAIN" --profile minimal --component rustc-dev --component llvm-tools-preview
run_stage build-apt bash -c 'sudo apt-get update && sudo apt-get install --yes --no-install-recommends build-essential git curl ca-certificates m4 patch unzip capnproto'
deps_archive="$task_temp/vfdeps-adf88dc-linux.txz"
run_stage vfdeps-download curl -fL --retry 3 -o "$deps_archive" https://github.com/verifast/vfdeps/releases/download/25.01/vfdeps-adf88dc-linux.txz
printf '%s  %s\n' "$deps_sha" "$deps_archive" | sha256sum -c -
[[ ! -e /vfdeps-adf88dc && ! -e /tmp/vfdeps-adf88dc ]] || exit 2
run_stage vfdeps-extract sudo tar -xjf "$deps_archive" -C /
ln -s /vfdeps-adf88dc /tmp/vfdeps-adf88dc
export PATH="/tmp/vfdeps-adf88dc/bin:$PATH"
export CAPNP_INC_DIR=/tmp/vfdeps-adf88dc/include
compiler_sysroot=$(rustc --print sysroot)
export LD_LIBRARY_PATH="$compiler_sysroot/lib:$source_home/bin:/tmp/vfdeps-adf88dc/lib:${LD_LIBRARY_PATH:-}"
run_stage decoder-install cargo install --locked --git https://github.com/btj/capnpc-ocaml-decoder --rev "$decoder_pin"
run_stage console-build make -C "$source_home/src" ../bin/verifast WITHOUT_LABLGTK=yes VERBOSE=yes
# Keep rebuilt console; copy unchanged stock exporter/support binaries/manifests.
# In particular C++ exporter/refinement checker/specifications remain stock.
cp -an "$stock_home/bin/." "$source_home/bin/"
if [[ -d "$stock_home/lib" ]]; then mkdir -p "$source_home/lib"; cp -an "$stock_home/lib/." "$source_home/lib/"; fi
cmp "$stock_home/bin/refinement-checker" "$source_home/bin/refinement-checker"
cmp "$stock_home/bin/vf-rust-mir-exporter" "$source_home/bin/vf-rust-mir-exporter"
printf '%s  %s\n' 7f3ebce320a33bcb956d51b8387754729e6516f4d15ba8dfdc61e6e36f90dfd9 "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" | sha256sum -c -
cmp "$stock_home/bin/vf-cxx-ast-exporter" "$source_home/bin/vf-cxx-ast-exporter"
# All stock specifications except the reviewed defined-predicate delta are exact.
set +e
diff -qr "$stock_home/bin/rust" "$source_home/bin/rust" > "$evidence/specifications-diff.txt"
spec_diff_status=$?
set -e
[[ "$spec_diff_status" == 1 ]] || exit 2
python3 - "$stock_home" "$source_home" "$evidence" <<'PY_SPEC'
import hashlib, pathlib, sys, json
stock,patched,ev=map(pathlib.Path,sys.argv[1:])
a={str(p.relative_to(stock/'bin/rust')): p.read_bytes() for p in (stock/'bin/rust').rglob('*') if p.is_file()}
b={str(p.relative_to(patched/'bin/rust')): p.read_bytes() for p in (patched/'bin/rust').rglob('*') if p.is_file()}
if a.keys()!=b.keys(): raise SystemExit('specification file inventory differs')
changed=[k for k in a if a[k]!=b[k]]
if changed!=['std/lib.rsspec']: raise SystemExit(f'unapproved spec changes: {changed}')
# The patch source audit above authenticates exact definition bytes; compare the
# baseline stock spec to the pinned source version independently.
import subprocess
base=subprocess.check_output(['git','-C',str(patched),'show','HEAD:bin/rust/std/lib.rsspec'])
if a['std/lib.rsspec']!=base: raise SystemExit('stock spec differs from source pin')
(ev/'specification-audit.json').write_text(json.dumps({'changed':changed,'all_other_specs_identical':True,'stock_spec_source_exact':True},indent=2)+'\n')
PY_SPEC
{
    rustc --version --verbose
    capnp --version
    ocamlc -version
    dune --version
    printf 'Schema and effective profile hashes:\n'
    sha256sum "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" "$source_home/bin/verifast" "$source_home/bin/vf-rust-mir-exporter" "$source_home/bin/refinement-checker" "$source_home/bin/vf-cxx-ast-exporter" "$source_home/bin/libz3.so"
    printf 'Stock identities:\n'
    sha256sum "$stock_home/bin/verifast" "$stock_home/bin/vf-rust-mir-exporter" "$stock_home/bin/refinement-checker"
    find "$source_home/bin/rust" -type f -name '*.rsspec' -print0 | sort -z | xargs -0 sha256sum
} >> "$evidence/environment.txt"
ldd "$source_home/bin/verifast" > "$evidence/console-ldd.txt"
rg -F "libz3.so => $source_home/bin/libz3.so " "$evidence/console-ldd.txt"
if rg -q 'not found' "$evidence/console-ldd.txt"; then exit 2; fi
[[ "$(git hash-object library/core/src/slice/sort/shared/smallsort.rs)" == e555fce440872898e47fd5114f32eb15401d07df ]] || exit 2
unset SORT4_MAYBEUNINIT_REPO_ROOT SORT4_SELECT_INTRINSIC_REPO_ROOT SORT4_POINTER_DROP_REPO_ROOT
ast_args=()
if [[ "$ast_mode" == 1 ]]; then ast_args=(--dump-ast-with-locs); fi
run_stage old-plain-generic python3 research/challenge-8/check-forget-generic.py --tool-home "$source_home" --schema "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" --compiler-sysroot "$compiler_sysroot" --preflight-manifest "$evidence/generic-construction-preflight/construction-preflight.json" --evidence "$evidence/old-plain-generic" "${ast_args[@]}"
if [[ "$mode" == trace ]]; then
    trace_patch="$repo/research/challenge-8/verifast-dead-code-loc-trace.patch"
    run_stage trace-patch-check git -C "$source_home" apply --check "$trace_patch"
    run_stage trace-patch-apply git -C "$source_home" apply "$trace_patch"
    git -C "$source_home" diff > "$evidence/traced-effective.patch"
    run_stage trace-console-build make -C "$source_home/src" ../bin/verifast WITHOUT_LABLGTK=yes VERBOSE=yes
    sha256sum "$source_home/bin/verifast" "$trace_patch" > "$evidence/traced-tool-hashes.txt"
    run_stage traced-generic env VF_DEAD_CODE_LOC_TRACE=1 python3 research/challenge-8/check-forget-generic.py --tool-home "$source_home" --schema "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" --compiler-sysroot "$compiler_sysroot" --preflight-manifest "$evidence/generic-construction-preflight/construction-preflight.json" --evidence "$evidence/traced-generic" --dump-ast-with-locs
else
    cfg_patch="$repo/research/challenge-8/verifast-manuallydrop-new-cfg.patch"
    printf '%s  %s\n' 89b0d80bd1e6382a9bf5be2f1ed208bae6aac5e907a21dd782c4c22307578da7 "$cfg_patch" | sha256sum -c -
    run_stage cfg-patch-check git -C "$source_home" apply --check "$cfg_patch"
    run_stage cfg-patch-apply git -C "$source_home" apply "$cfg_patch"
    git -C "$source_home" diff > "$evidence/cfg-effective.patch"
    run_stage cfg-console-build make -C "$source_home/src" ../bin/verifast WITHOUT_LABLGTK=yes VERBOSE=yes
    sha256sum "$source_home/bin/verifast" "$cfg_patch" > "$evidence/cfg-tool-hashes.txt"
    git -C "$source_home" diff --name-only > "$evidence/cfg-modified-files.txt"
    [[ "$(cat "$evidence/cfg-modified-files.txt")" == "$(cat "$evidence/modified-files.txt")" ]] || exit 2
    # Authenticate overlay and retain exact source hashes, separate from base profile.
    sha256sum "$source_home/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml" "$source_home/bin/rust/std/lib.rsspec" >> "$evidence/cfg-tool-hashes.txt"
    git -C "$source_home" apply --reverse --check "$cfg_patch"
    git -C "$source_home" apply --reverse "$cfg_patch"
    git -C "$source_home" diff > "$evidence/cfg-base-restored.patch"
    cmp "$evidence/cfg-base-restored.patch" "$patch_file"
    git -C "$source_home" apply "$cfg_patch"
    # No instrumentation may enter the acceptance binary.
    for path in src/verify_expr.ml src/vfconsole/vfconsole.ml src/frontend/ast.ml; do
        git -C "$source_home" diff --exit-code -- "$path"
    done
    export SORT4_SELECT_PROFILE=experimental-manuallydrop-new-cfg-v1
    acceptance_remaining=$((job_cap * 60 - 70 - $(date +%s) + SORT4_CONSTRUCTOR_JOB_STARTED_EPOCH))
    (( acceptance_remaining >= 60 )) || exit 124
    run_stage cfg-acceptance python3 research/challenge-8/check-forget-cfg.py --stock-home "$stock_home" --tool-home "$source_home" --schema "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" --compiler-sysroot "$compiler_sysroot" --baseline-evidence "$evidence/old-plain-generic" --evidence "$evidence/cfg-acceptance" --budget-seconds "$acceptance_remaining"
fi
exit 0
