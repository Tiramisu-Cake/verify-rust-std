#!/usr/bin/env bash
# Compile-only preflight for an already prepared, profile-pinned source tree.
# This script never runs VeriFast, a proof runner, or any proof fixture.
set -euo pipefail

candidate=${1:?prepared candidate source home}
evidence=${2:?new compile-preflight evidence directory}
for path in "$candidate" "$evidence"; do
  [[ "$path" == /workspace/* ]] || exit 2
done
[[ ! -e "$evidence" ]] || exit 2
mkdir -p "$evidence"
stage=preflight-setup
finished=0
write_manifest() {
  local rc=$?
  trap - EXIT
  if [[ "$finished" == 1 && "$rc" == 0 ]]; then
    exit 0
  fi
  python3 - "$evidence" "$stage" "$rc" "$finished" <<'MANIFEST' || true
import json, pathlib, sys
directory, stage, rc, finished = sys.argv[1:]
report = {
 'schema':'smallsort-compile-preflight-v1',
 'classification':'COMPILE_ONLY_NO_PROOF_CREDIT',
 'accepted':False,
 'proof_attempted':False,
 'result':'success' if finished == '1' and rc == '0' else 'failure',
 'failed_stage':None if finished == '1' and rc == '0' else stage,
 'exit_code':int(rc),
}
report['stages'] = {name: {'exit_code': int((pathlib.Path(directory)/(name+'-exit-code.txt')).read_text().strip())
                         if (pathlib.Path(directory)/(name+'-exit-code.txt')).is_file() else None, 'log': name+'.log'}
                    for name in ('exporter-build','decoder-build','translator-build','console-build','refiner-build')}
(pathlib.Path(directory)/'compile-preflight.json').write_text(json.dumps(report,indent=2)+'\n')
MANIFEST
  exit "$rc"
}
trap write_manifest EXIT

python3 "${SMALLSORT_PROVIDER_FILE:?}" >/dev/null
[[ "${SMALLSORT_EXECUTION_PROVIDER:-}" == cloud-build ]] || exit 2
[[ "${RUSTUP_TOOLCHAIN:-}" == nightly-2026-09-25 ]] || exit 2

[[ -d "$candidate/src/rust_frontend/vf_mir_exporter" && -d "$candidate/src" ]] || exit 2

here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
repo=$(git -C "$here" rev-parse --show-toplevel)
onecell="$repo/research/challenge-8/merge/overnight/guard-ownership/insertion-onecell"
profile="${SMALLSORT_MERGE_PROFILE:-$onecell/PROFILE.json}"

# Confirm the prepared source tree and the exact existing profile patches before
# invoking either compiler. A mismatch is a preflight refusal, never proof credit.
python3 - "$candidate" "$profile" "$onecell" "$here" <<'PINS'
import hashlib, json, pathlib, subprocess, sys
home, profile_path, onecell, origin_layout = map(pathlib.Path, sys.argv[1:])
p = json.loads(profile_path.read_text())
assert p['schema'] == 'smallsort-tracked-md-profile-v1' and p['accepted'] is False
assert subprocess.check_output(['git', '-C', str(home), 'rev-parse', 'HEAD'], text=True).strip() == p['verifast_commit']
sources = {
 'src/rust_frontend/vf_mir_exporter/src/lib.rs':'exporter_source_sha256',
 'src/rust_frontend/vf_mir/vf_mir.capnp':'schema_sha256',
 'src/refinement_checker/main.ml':'refiner_main_source_sha256',
 'src/refinement_checker/refinement_checker.ml':'refiner_core_source_sha256',
 'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml':'translator_sha256',
 'src/rust_frontend/vf_mir_translator/rust_parser.ml':'parser_sha256',
 'src/frontend/ast.ml':'ast_sha256',
 'src/frontend/ocaml_expr_of_ast.ml':'emitter_sha256',
 'src/SExpressionEmitter.ml':'sexpression_sha256',
 'src/verifast.ml':'kernel_sha256',
 'src/verifast1.ml':'model_sha256',
 'src/verify_expr.ml':'verify_expr_sha256',
 'bin/rust/prelude_core.rsspec':'prelude_sha256',
 'bin/rust/std/lib.rsspec':'stdlib_sha256',
}
for rel, key in sources.items():
    actual = hashlib.sha256((home/rel).read_bytes()).hexdigest()
    assert actual == p[key], (rel, key, actual, p[key])
patches = [
 (onecell/'tracked-md.patch', 'patch_sha256'),
 (onecell/'allocation-span.patch', 'allocation_span_patch_sha256'),
 (origin_layout/'unit-layout.patch', 'unit_layout_patch_sha256'),
 (origin_layout/'guard-layout.patch', 'guard_layout_patch_sha256'),
]
for path, key in patches:
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    assert actual == p[key], (str(path), key, actual, p[key])
PINS

export PATH="/tmp/vfdeps-adf88dc/bin:$PATH"
export CAPNP_INC_DIR=/tmp/vfdeps-adf88dc/include
# The full console also depends on cxx_frontend/stubs, whose pinned Dune
# rule names the same real include directory CAPNP_INCLUDE (not CAPNP_INC_DIR).
export CAPNP_INCLUDE="$CAPNP_INC_DIR"
[[ -d "$CAPNP_INC_DIR/capnp" ]] || exit 2
printf 'CAPNP_INC_DIR=%s\nCAPNP_INCLUDE=%s\n' "$CAPNP_INC_DIR" "$CAPNP_INCLUDE" \
  > "$evidence/capnp-generator-environment.txt"
export LD_LIBRARY_PATH="$candidate/bin:/tmp/vfdeps-adf88dc/lib:${LD_LIBRARY_PATH:-}"
export CARGO_BUILD_JOBS=1

# Mirror the GNUmakefile's findlib-based Z3 DLL directory resolution. The
# pinned profile uses WITHOUT_LABLGTK=yes, so it does not export OCAMLPATH or
# OCAMLOPT_CCLIB_FLAGS; leave both ambient values untouched here as well.
z3_ocaml=$(ocamlfind query -qe Z3 2>/dev/null || true)
if [[ -n "$z3_ocaml" ]]; then
  z3_dll_dir=$(realpath -e "$z3_ocaml/../..")
else
  z3_ocaml=$(ocamlfind query z3)
  z3_dll_dir=$(realpath -e "$z3_ocaml")
fi
export Z3_DLL_DIR="$z3_dll_dir"
printf '%s\n' "$Z3_DLL_DIR" >"$evidence/z3-dll-dir.txt"

run_step() {
  local name=$1; shift
  local rc
  stage=$name
  set +e
  timeout --signal=TERM --kill-after=15s 900s \
    /usr/bin/time -v -o "$evidence/$name-time.txt" \
    "$@" >"$evidence/$name.log" 2>&1
  rc=$?
  set -e
  printf '%s\n' "$rc" >"$evidence/$name-exit-code.txt"
  cat "$evidence/$name.log"
  if (( rc != 0 )); then
    return "$rc"
  fi
}

# Build the exact exporter source first. Rustc-dev's LLVM is in the pinned
# sysroot lib directory; Cargo otherwise misses it on this Cloud image.
exporter_sysroot=$(rustc --print sysroot)
printf '%s\n' "$exporter_sysroot" >"$evidence/exporter-compiler-sysroot.txt"
run_step exporter-build env RUSTFLAGS="-L native=$exporter_sysroot/lib" \
  bash -c 'cd "$1/src/rust_frontend/vf_mir_exporter" && cargo build --locked --jobs 1' bash "$candidate"
cp "$candidate/src/rust_frontend/vf_mir_exporter/target/debug/vf_mir_exporter" \
  "$candidate/bin/vf-rust-mir-exporter"

# Dune dependency order: schema-derived decoder (also builds vf_mir's generated
# OCaml), then translator, then the console target to compile all remaining
# verifier/AST/emitter OCaml that the real console depends on. Keep one job.
run_step decoder-build bash -c \
  'cd "$1/src" && dune build -j 1 rust_frontend/vf_mir_decoder/vf_mir_decoder.cma' \
  bash "$candidate"
run_step translator-build bash -c \
  'cd "$1/src" && dune build -j 1 rust_frontend/vf_mir_translator/vf_mir_translator.cma' \
  bash "$candidate"
run_step console-build bash -c \
  'cd "$1/src" && dune build -j 1 vfconsole/vfconsole.exe && cp _build/default/vfconsole/vfconsole.exe ../bin/verifast' \
  bash "$candidate"

run_step refiner-build bash -c \
  'cd "$1/src" && dune build -j 1 refinement_checker/main.exe && cp _build/default/refinement_checker/main.exe ../bin/refinement-checker' \
  bash "$candidate"

run_step postbuild-source-hash-check python3 - "$candidate" "$profile" <<'POSTPINS'
import hashlib, json, pathlib, sys
home, profile_path = map(pathlib.Path, sys.argv[1:])
p = json.loads(profile_path.read_text())
sources = {
 'src/rust_frontend/vf_mir_exporter/src/lib.rs':'exporter_source_sha256',
 'src/rust_frontend/vf_mir/vf_mir.capnp':'schema_sha256',
 'src/refinement_checker/main.ml':'refiner_main_source_sha256',
 'src/refinement_checker/refinement_checker.ml':'refiner_core_source_sha256',
 'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml':'translator_sha256',
 'src/rust_frontend/vf_mir_translator/rust_parser.ml':'parser_sha256',
 'src/frontend/ast.ml':'ast_sha256',
 'src/frontend/ocaml_expr_of_ast.ml':'emitter_sha256',
 'src/SExpressionEmitter.ml':'sexpression_sha256',
 'src/verifast.ml':'kernel_sha256',
 'src/verifast1.ml':'model_sha256',
 'src/verify_expr.ml':'verify_expr_sha256',
 'bin/rust/prelude_core.rsspec':'prelude_sha256',
 'bin/rust/std/lib.rsspec':'stdlib_sha256',
}
for rel, key in sources.items():
    actual = hashlib.sha256((home/rel).read_bytes()).hexdigest()
    assert actual == p[key], (rel, key, actual, p[key])
POSTPINS

stage=report-generation
python3 - "$candidate" "$profile" "$evidence" <<'REPORT'
import hashlib, json, pathlib, sys, os, runpy
home, profile_path, evidence = map(pathlib.Path, sys.argv[1:])
p = json.loads(profile_path.read_text())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
report = {
 'schema':'smallsort-compile-preflight-v1',
 'classification':'COMPILE_ONLY_NO_PROOF_CREDIT',
 'accepted':False,
 'proof_attempted':False,
 'candidate_head':__import__('subprocess').check_output(['git','-C',str(home),'rev-parse','HEAD'],text=True).strip(),
 'profile':p['profile'],
 'profile_sha256':sha(profile_path),
 'stages':{},
 'artifacts':{},
}
for stage in ('exporter-build','decoder-build','translator-build','console-build','refiner-build'):
 code_path=evidence/(stage+'-exit-code.txt')
 report['stages'][stage]={'exit_code':int(code_path.read_text().strip()) if code_path.exists() else None,
                          'log':stage+'.log'}
for rel, key in [('src/rust_frontend/vf_mir_exporter/src/lib.rs','exporter_source_sha256'),
                 ('src/rust_frontend/vf_mir/vf_mir.capnp','schema_sha256'),
                 ('src/rust_frontend/vf_mir_translator/vf_mir_translator.ml','translator_sha256'),
                 ('src/refinement_checker/main.ml','refiner_main_source_sha256'),
                 ('src/refinement_checker/refinement_checker.ml','refiner_core_source_sha256')]:
 report['artifacts'][rel]={'profile_sha256':p[key],'sha256':sha(home/rel)}
for rel in ('src/rust_frontend/vf_mir_exporter/target/debug/vf_mir_exporter','bin/vf-rust-mir-exporter','bin/verifast','bin/refinement-checker'):
 path=home/rel
 if path.is_file(): report['artifacts'][rel]={'sha256':sha(path),'executable':bool(path.stat().st_mode & 0o111)}
(evidence/'compile-preflight.json').write_text(json.dumps(report,indent=2)+'\n')
# A compiler receipt binds actual built binaries, the same source profile and
# this Cloud provider. It grants no native/proof/layout observation credit.
profile_build = dict(p)
profile_build.update(exporter_sha256=sha(home/'bin/vf-rust-mir-exporter'),
    exporter_build_exit=0, console_sha256=sha(home/'bin/verifast'),
    proof_sha=os.environ['PROOF_SHA'],
    baseline_build_manifest_sha256=sha(evidence.parent/'build/console-cache-profile.txt'),
    provider=runpy.run_path(os.environ['SMALLSORT_PROVIDER_FILE'])['require_supported_provider'](),
    build_exit=0, compile_only=True, proof_attempted=False,
    compile_preflight_sha256=sha(evidence/'compile-preflight.json'))
for rel,key in [('bin/libz3.so','z3_sha256')]:
    assert sha(home/rel)==p[key], (rel,key)
profile_build.update(refiner_sha256=sha(home/'bin/refinement-checker'), refiner_build_exit=0, refiner_built_from_source=True, refiner_main_source_sha256=sha(home/'src/refinement_checker/main.ml'), refiner_core_source_sha256=sha(home/'src/refinement_checker/refinement_checker.ml'))
(evidence/'profile-build.json').write_text(json.dumps(profile_build,indent=2)+'\n')

REPORT
finished=1
stage=complete
