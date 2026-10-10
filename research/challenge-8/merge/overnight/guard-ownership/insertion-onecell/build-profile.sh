#!/usr/bin/env bash
# Cloud-only opt-in exact rebase; original six-profile tool remains unchanged.
set -euo pipefail
python3 "${SMALLSORT_PROVIDER_FILE:?}" >/dev/null
[[ "${SMALLSORT_EXECUTION_PROVIDER:-}" == cloud-build ]] || exit 2
base_home=${1:?six-profile source home}
new_home=${2:?fresh tracked-MD source home}
evidence=${3:?fresh evidence directory}
base_evidence=${4:?six-profile build evidence}
for target in "$base_home" "$new_home" "$evidence" "$base_evidence"; do
  [[ "$target" == /workspace/* ]] || exit 2
done
[[ ! -e "$new_home" && ! -e "$evidence" ]] || exit 2
here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
[[ "$(git -C "$base_home" rev-parse HEAD)" == f76012fb518703b1d98e243ac4f487f16877cfcb ]] || exit 2
[[ "$(cat "$base_evidence/source-build-exit-code.txt")" == 0 ]] || exit 2
mkdir -p "$evidence"
cp -a "$base_home" "$new_home"
python3 - "$here" "$base_home" "$new_home" "$evidence" <<'BOOTSTRAP'
import hashlib,json,pathlib,shutil,sys
here,base,home,evidence=map(pathlib.Path,sys.argv[1:])
pins=json.loads((here/'PROFILE.json').read_text())
# The console cache contract restores only bin/verifast.  Keep the two frozen
# helpers sourced from the same pinned 26.10 release archive used by run.sh;
# fill only omissions, and never replace a present but mismatched dependency.
release=base.parent/'verifast-26.10'
deps={'bin/vf-rust-mir-exporter':'baseline_exporter_sha256',
      'bin/refinement-checker':'refiner_sha256'}
report={'schema':'onecell-frozen-dependency-bootstrap-v1',
        'release_home':str(release),'dependencies':{}}
for relative,key in deps.items():
    target=home/relative
    source=release/relative
    expected=pins[key]
    def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
    if target.exists():
        before=sha(target)
        assert before==expected,(relative,'present baseline dependency has wrong SHA-256',before,expected)
        action='baseline-present'
    else:
        assert source.is_file() and source.stat().st_mode & 0o111,(relative,'pinned release dependency missing or not executable')
        source_sha=sha(source)
        assert source_sha==expected,(relative,'release dependency has wrong SHA-256',source_sha,expected)
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,target)
        action='copied-from-pinned-release'
    after=sha(target)
    assert after==expected,(relative,'bootstrapped dependency has wrong SHA-256',after,expected)
    report['dependencies'][relative]={'action':action,'expected_sha256':expected,
                                      'sha256':after,'executable':bool(target.stat().st_mode & 0o111)}
    assert report['dependencies'][relative]['executable'],(relative,'dependency is not executable')
# Restore only missing C++ dependencies from the same already SHA-pinned release.
# Present mismatches still fail; Rust trusted sources and helper pins stay unchanged.
for relative in ('bin/vf-cxx-ast-exporter','bin/prelude_cxx.h'):
    target=home/relative
    source=release/relative
    assert source.is_file(),(relative,'frozen release C++ dependency missing')
    expected=sha(source)
    action='baseline-present'
    if not target.exists():
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,target)
        action='copied-from-pinned-release'
    assert target.is_file() and sha(target)==expected,(relative,'C++ dependency differs from frozen release')
    if relative.endswith('vf-cxx-ast-exporter'):
        assert target.stat().st_mode & 0o111,(relative,'C++ exporter is not executable')
    report['dependencies'][relative]={'action':action,
        'expected_sha256':expected,'sha256':sha(target),
        'executable':bool(target.stat().st_mode & 0o111),
        'domain':'frozen-release C++ diagnostic only'}
(evidence/'frozen-dependency-bootstrap.json').write_text(json.dumps(report,indent=2)+'\n')
BOOTSTRAP
python3 - "$here" "$new_home" "$evidence" <<'PINS'
import hashlib,json,pathlib,sys
here,home,evidence=map(pathlib.Path,sys.argv[1:])
pins=json.loads((here/'PROFILE.json').read_text())
assert pins['schema']=='smallsort-tracked-md-profile-v1' and not pins['accepted']
paths={'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml':'baseline_translator_sha256','src/verifast.ml':'baseline_kernel_sha256','src/verifast1.ml':'model_baseline_sha256','src/rust_frontend/vf_mir_translator/rust_parser.ml':'parser_sha256','bin/rust/prelude_core.rsspec':'prelude_sha256','bin/rust/std/lib.rsspec':'stdlib_sha256','bin/vf-rust-mir-exporter':'baseline_exporter_sha256','bin/refinement-checker':'refiner_sha256','bin/libz3.so':'z3_sha256','src/frontend/ocaml_expr_of_ast.ml':'baseline_emitter_sha256'}
for path,key in paths.items():
 assert hashlib.sha256((home/path).read_bytes()).hexdigest()==pins[key],(path,key)
assert hashlib.sha256((here/'tracked-md.patch').read_bytes()).hexdigest()==pins['patch_sha256']
(evidence/'profile-input.json').write_text(json.dumps(pins,indent=2)+'\n')
PINS
git -C "$new_home" apply --check "$here/tracked-md.patch"
git -C "$new_home" apply --whitespace=error "$here/tracked-md.patch"
cp "$here/tracked-md.patch" "$evidence/tracked-md.patch"
python3 - "$here" <<'SPANPIN'
import hashlib,json,pathlib,sys
h=pathlib.Path(sys.argv[1]);p=json.loads((h/'PROFILE.json').read_text())
assert hashlib.sha256((h/'allocation-span.patch').read_bytes()).hexdigest()==p['allocation_span_patch_sha256']
SPANPIN
git -C "$new_home" -c core.whitespace=cr-at-eol apply --check "$here/allocation-span.patch"
git -C "$new_home" -c core.whitespace=cr-at-eol apply --whitespace=error "$here/allocation-span.patch"
cp "$here/allocation-span.patch" "$evidence/allocation-span.patch"
layout_patch="$here/../../../../cloud-build/origin-layout/unit-layout.patch"
python3 - "$here" "$layout_patch" <<'LAYOUTPIN'
import hashlib,json,pathlib,sys
h,p=map(pathlib.Path,sys.argv[1:]);pins=json.loads((h/'PROFILE.json').read_text())
assert hashlib.sha256(p.read_bytes()).hexdigest()==pins['unit_layout_patch_sha256']
LAYOUTPIN
git -C "$new_home" -c core.whitespace=cr-at-eol apply --check "$layout_patch"
git -C "$new_home" -c core.whitespace=cr-at-eol apply --whitespace=error "$layout_patch"
cp "$layout_patch" "$evidence/unit-layout.patch"
guard_patch="$here/../../../../cloud-build/origin-layout/guard-layout.patch"
python3 - "$here" "$guard_patch" <<'GUARDPIN'
import hashlib,json,pathlib,sys
h,p=map(pathlib.Path,sys.argv[1:]);pins=json.loads((h/'PROFILE.json').read_text())
assert hashlib.sha256(p.read_bytes()).hexdigest()==pins['guard_layout_patch_sha256']
GUARDPIN
git -C "$new_home" -c core.whitespace=cr-at-eol apply --check "$guard_patch"
git -C "$new_home" -c core.whitespace=cr-at-eol apply --whitespace=error "$guard_patch"
cp "$guard_patch" "$evidence/guard-layout.patch"
export PATH="/tmp/vfdeps-adf88dc/bin:$PATH"
export CAPNP_INC_DIR=/tmp/vfdeps-adf88dc/include
export LD_LIBRARY_PATH="$new_home/bin:/tmp/vfdeps-adf88dc/lib:${LD_LIBRARY_PATH:-}"
# Same pinned compiler builds the reviewed exporter from source; helpers/refiner
# and retained-six source remain frozen. No binary is adopted by a prior pin.
# capnproto-rust is a pinned regular Git tree at the source baseline.
exporter_sysroot=$(rustc --print sysroot)
printf '%s\n' "$exporter_sysroot" > "$evidence/exporter-compiler-sysroot.txt"
# rustc-dev links LLVM from the same pinned toolchain's top-level lib directory;
# Cargo's default native search covers rustlib/target/lib but not this directory.
set +e
/usr/bin/time -v -o "$evidence/exporter-build-resources.txt" \
  env RUSTFLAGS="-L native=$exporter_sysroot/lib" \
  bash -c 'cd "$1/src/rust_frontend/vf_mir_exporter"; cargo build --locked' bash "$new_home" \
  > "$evidence/exporter-build.log" 2>&1
exporter_build_status=$?
set -e
printf '%s\n' "$exporter_build_status" > "$evidence/exporter-build-exit-code.txt"
cat "$evidence/exporter-build.log"
(( exporter_build_status == 0 )) || exit "$exporter_build_status"
cp "$new_home/src/rust_frontend/vf_mir_exporter/target/debug/vf_mir_exporter" "$new_home/bin/vf-rust-mir-exporter"
set +e
/usr/bin/time -v -o "$evidence/console-build-resources.txt" \
  make -C "$new_home/src" ../bin/verifast WITHOUT_LABLGTK=yes VERBOSE=yes \
  > "$evidence/console-build.log" 2>&1
build_status=$?
set -e
printf '%s\n' "$build_status" > "$evidence/console-build-exit-code.txt"
cat "$evidence/console-build.log"
(( build_status == 0 )) || exit "$build_status"
python3 - "$here" "$new_home" "$evidence" "$base_evidence" <<'FINAL'
import hashlib,json,os,pathlib,runpy,sys
here,home,evidence,base_evidence=map(pathlib.Path,sys.argv[1:])
pins=json.loads((here/'PROFILE.json').read_text())
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
paths={'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml':'translator_sha256','src/verifast.ml':'kernel_sha256','src/verifast1.ml':'model_sha256','src/rust_frontend/vf_mir_translator/rust_parser.ml':'parser_sha256','bin/rust/prelude_core.rsspec':'prelude_sha256','bin/rust/std/lib.rsspec':'stdlib_sha256','src/rust_frontend/vf_mir_exporter/src/lib.rs':'exporter_source_sha256','src/rust_frontend/vf_mir/vf_mir.capnp':'schema_sha256','bin/refinement-checker':'refiner_sha256','bin/libz3.so':'z3_sha256','src/frontend/ocaml_expr_of_ast.ml':'emitter_sha256','src/frontend/ast.ml':'ast_sha256','src/SExpressionEmitter.ml':'sexpression_sha256','src/verify_expr.ml':'verify_expr_sha256'}
for path,key in paths.items(): assert h(home/path)==pins[key],(path,key)
pins.update(exporter_sha256=h(home/'bin/vf-rust-mir-exporter'),exporter_build_exit=0,console_sha256=h(home/'bin/verifast'),proof_sha=os.environ['PROOF_SHA'],baseline_build_manifest_sha256=h(base_evidence/'console-cache-profile.txt'),provider=runpy.run_path(os.environ['SMALLSORT_PROVIDER_FILE'])['require_supported_provider'](),build_exit=0)
(evidence/'profile-build.json').write_text(json.dumps(pins,indent=2)+'\n')
(evidence/'translator.patched.ml').write_bytes((home/'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml').read_bytes())
(evidence/'emitter.patched.ml').write_bytes((home/'src/frontend/ocaml_expr_of_ast.ml').read_bytes())
(evidence/'kernel.patched.ml').write_bytes((home/'src/verifast.ml').read_bytes())
(evidence/'model.patched.ml').write_bytes((home/'src/verifast1.ml').read_bytes())
FINAL

# Native regression for ordinary prototypes with the historical marker spelling.
set +e
timeout --signal=TERM --kill-after=5s 35s "$new_home/bin/verifast" -c \
  "$new_home/tests/rust_storage_marker_name_calls.c" \
  > "$evidence/native-origin.log" 2>&1
native_status=$?
set -e
printf '%s\n' "$native_status" > "$evidence/native-origin-exit-code.txt"
cat "$evidence/native-origin.log"
# Record diagnostics separately; never promote failed native test to PASS.

# Dialect isolation: exact unit spelling in C/C++ retains ordinary positive size.
for native_suffix in c cpp; do
  native_source="$here/../../../../cloud-build/origin-layout/unit-name.$native_suffix"
  set +e
  timeout --signal=TERM --kill-after=5s 25s "$new_home/bin/verifast" -verbose 1 -c "$native_source" \
    > "$evidence/native-unit-$native_suffix.log" 2>&1
  native_unit_status=$?
  set -e
  printf '%s\n' "$native_unit_status" > "$evidence/native-unit-$native_suffix-exit-code.txt"
  cat "$evidence/native-unit-$native_suffix.log"
  if [[ "$native_suffix" == cpp && "$native_unit_status" != 0 ]]; then
    # Reveal exporter stderr hidden by vfconsole's dummy-location formatter.
    # Match the existing C++ frontend's empty process environment and argv.
    set +e
    timeout --signal=TERM --kill-after=5s 20s env -i "$new_home/bin/vf-cxx-ast-exporter" \
      "$native_source" -allow_macro_expansion=__VF_CXX_CLANG_FRONTEND__,__INT8_TYPE__,__INT16_TYPE__,__INT32_TYPE__,__INT64_TYPE__,__UINT8_TYPE__,__UINT16_TYPE__,__UINT32_TYPE__,__UINT64_TYPE__ -- \
      -xc++ -std=c++17 "-I$new_home/bin" -D__VF_CXX_CLANG_FRONTEND__ \
      > "$evidence/native-unit-cpp-exporter.bin" 2> "$evidence/native-unit-cpp-exporter.log"
    native_exporter_status=$?
    set -e
    printf '%s\n' "$native_exporter_status" > "$evidence/native-unit-cpp-exporter-exit-code.txt"
    cat "$evidence/native-unit-cpp-exporter.log"
  fi
done

# Independent concrete ABI observation by the pinned compiler, separate from VF.
compiler_layout_source="$here/../../../../cloud-build/origin-layout/compiler-layout.rs"
cp "$compiler_layout_source" "$evidence/compiler-layout.rs"
python3 - "$compiler_layout_source" "$evidence" <<'COMPILER_RECEIPT'
import hashlib,json,os,pathlib,runpy,shutil,subprocess,sys
source,evidence=map(pathlib.Path,sys.argv[1:])
version=subprocess.check_output(['rustc','-vV'],text=True)
resolved=subprocess.check_output(['rustup','which','rustc'],text=True).strip()
assert subprocess.check_output([resolved,'-vV'],text=True)==version
assert os.environ.get('RUSTUP_TOOLCHAIN')=='nightly-2026-09-25'
assert 'commit-hash: f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f' in version
assert 'host: x86_64-unknown-linux-gnu' in version
receipt={'schema':'compiler-layout-fact-v1','classification':'COMPILER_FACT_DIAGNOSTIC_NOT_PROOF',
 'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
 'rustc_version':version,'rustc_command':shutil.which('rustc'),'rustc_resolved':resolved,
 'rustc_sha256':hashlib.sha256(pathlib.Path(resolved).read_bytes()).hexdigest(),
 'toolchain':os.environ['RUSTUP_TOOLCHAIN'],'target':'x86_64-unknown-linux-gnu',
 'proof_sha':os.environ['PROOF_SHA'],
 'provider':runpy.run_path(os.environ['SMALLSORT_PROVIDER_FILE'])['require_supported_provider']()}
(evidence/'compiler-layout-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
(evidence/'compiler-layout-rustc.txt').write_text(resolved+'\n')
COMPILER_RECEIPT
compiler_layout_rustc=$(cat "$evidence/compiler-layout-rustc.txt")
set +e
timeout --signal=TERM --kill-after=5s 25s "$compiler_layout_rustc" --edition=2021 --crate-name=compiler_layout --crate-type=bin \
  --target=x86_64-unknown-linux-gnu "$compiler_layout_source" -o "$evidence/compiler-layout" \
  > "$evidence/compiler-layout-compile.log" 2>&1
compiler_layout_status=$?
set -e
printf '%s\n' "$compiler_layout_status" > "$evidence/compiler-layout-compile-exit-code.txt"
(( compiler_layout_status == 0 )) || exit "$compiler_layout_status"
set +e
timeout --signal=TERM --kill-after=5s 5s "$evidence/compiler-layout" \
  > "$evidence/compiler-layout.json" 2> "$evidence/compiler-layout-run.log"
compiler_layout_status=$?
set -e
printf '%s\n' "$compiler_layout_status" > "$evidence/compiler-layout-run-exit-code.txt"
(( compiler_layout_status == 0 )) || exit "$compiler_layout_status"
rm "$evidence/compiler-layout"
