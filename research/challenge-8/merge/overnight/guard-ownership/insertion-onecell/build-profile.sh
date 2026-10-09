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
deps={'bin/vf-rust-mir-exporter':'exporter_sha256',
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
(evidence/'frozen-dependency-bootstrap.json').write_text(json.dumps(report,indent=2)+'\n')
BOOTSTRAP
python3 - "$here" "$new_home" "$evidence" <<'PINS'
import hashlib,json,pathlib,sys
here,home,evidence=map(pathlib.Path,sys.argv[1:])
pins=json.loads((here/'PROFILE.json').read_text())
assert pins['schema']=='smallsort-tracked-md-profile-v1' and not pins['accepted']
paths={'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml':'baseline_translator_sha256','src/verifast.ml':'baseline_kernel_sha256','src/rust_frontend/vf_mir_translator/rust_parser.ml':'parser_sha256','bin/rust/prelude_core.rsspec':'prelude_sha256','bin/rust/std/lib.rsspec':'stdlib_sha256','bin/vf-rust-mir-exporter':'exporter_sha256','bin/refinement-checker':'refiner_sha256','bin/libz3.so':'z3_sha256','src/frontend/ocaml_expr_of_ast.ml':'baseline_emitter_sha256'}
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
export PATH="/tmp/vfdeps-adf88dc/bin:$PATH"
export CAPNP_INC_DIR=/tmp/vfdeps-adf88dc/include
export LD_LIBRARY_PATH="$new_home/bin:/tmp/vfdeps-adf88dc/lib:${LD_LIBRARY_PATH:-}"
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
paths={'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml':'translator_sha256','src/verifast.ml':'kernel_sha256','src/rust_frontend/vf_mir_translator/rust_parser.ml':'parser_sha256','bin/rust/prelude_core.rsspec':'prelude_sha256','bin/rust/std/lib.rsspec':'stdlib_sha256','bin/vf-rust-mir-exporter':'exporter_sha256','bin/refinement-checker':'refiner_sha256','bin/libz3.so':'z3_sha256','src/frontend/ocaml_expr_of_ast.ml':'emitter_sha256','src/frontend/ast.ml':'ast_sha256','src/SExpressionEmitter.ml':'sexpression_sha256','src/verify_expr.ml':'verify_expr_sha256'}
for path,key in paths.items(): assert h(home/path)==pins[key],(path,key)
pins.update(console_sha256=h(home/'bin/verifast'),proof_sha=os.environ['PROOF_SHA'],baseline_build_manifest_sha256=h(base_evidence/'console-cache-profile.txt'),provider=runpy.run_path(os.environ['SMALLSORT_PROVIDER_FILE'])['require_supported_provider'](),build_exit=0)
(evidence/'profile-build.json').write_text(json.dumps(pins,indent=2)+'\n')
(evidence/'translator.patched.ml').write_bytes((home/'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml').read_bytes())
(evidence/'emitter.patched.ml').write_bytes((home/'src/frontend/ocaml_expr_of_ast.ml').read_bytes())
(evidence/'kernel.patched.ml').write_bytes((home/'src/verifast.ml').read_bytes())
FINAL

# Native regression for ordinary prototypes with the historical marker spelling.
set +e
timeout --signal=TERM --kill-after=5s 35s "$new_home/bin/verifast" \
  "$new_home/tests/rust_storage_marker_name_calls.c" \
  > "$evidence/native-origin.log" 2>&1
native_status=$?
set -e
printf '%s\n' "$native_status" > "$evidence/native-origin-exit-code.txt"
cat "$evidence/native-origin.log"
# Record diagnostics separately; never promote failed native test to PASS.
