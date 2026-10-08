#!/usr/bin/env bash
# Build and run the H2d generated-post mutants in an isolated hosted console.
# The source/console used by production S6 and actual Rust checks is read-only.
set -euo pipefail
[[ "${GITHUB_ACTIONS:-}" == true && "${RUNNER_ENVIRONMENT:-}" == github-hosted && "${RUNNER_OS:-}" == Linux ]] || exit 2

repo=$(git rev-parse --show-toplevel)
production_source=
production_diff=
stock_home=
compiler_sysroot=
evidence=
deadline_epoch=
while (($#)); do
  case "$1" in
    --production-source) production_source=$2; shift 2 ;;
    --production-applied-patch) production_diff=$2; shift 2 ;;
    --stock-home) stock_home=$2; shift 2 ;;
    --compiler-sysroot) compiler_sysroot=$2; shift 2 ;;
    --evidence) evidence=$2; shift 2 ;;
    --deadline-epoch) deadline_epoch=$2; shift 2 ;;
    *) printf 'Unknown H2d option: %s\n' "$1" >&2; exit 2 ;;
  esac
done
[[ -n "$production_source" && -n "$production_diff" && -n "$stock_home" && -n "$compiler_sysroot" && -n "$evidence" && -n "$deadline_epoch" ]] || exit 2
[[ "$deadline_epoch" =~ ^[0-9]+$ ]] || exit 2
[[ -d "$production_source/.git" && -f "$production_diff" && -f "$stock_home/bin/vf-rust-mir-exporter" && -d "$compiler_sysroot/lib" ]] || exit 2
[[ ! -e "$evidence" ]] || { printf 'Refusing existing H2d evidence: %s\n' "$evidence" >&2; exit 2; }
[[ "$(git -C "$production_source" rev-parse HEAD)" == f76012fb518703b1d98e243ac4f487f16877cfcb ]] || exit 2
[[ "$(git -C "$repo" rev-parse --show-toplevel)" == "$repo" ]] || exit 2

test_patch="$repo/research/challenge-8/overnight-guard/verifast-h2d-test-only-drop-post-26.10.patch"
[[ -f "$test_patch" ]] || exit 2
test_source="$RUNNER_TEMP/overnight-h2d-test-source"
[[ ! -e "$test_source" ]] || { printf 'Refusing existing H2d source copy: %s\n' "$test_source" >&2; exit 2; }
mkdir -p "$evidence"
stage() {
  local name=$1; shift
  local code=0
  /usr/bin/time -v -o "$evidence/$name-resources.txt" "$@" > "$evidence/$name.log" 2>&1 || code=$?
  printf '%s\n' "$code" > "$evidence/$name-exit-code.txt"
  return "$code"
}
hash() { sha256sum "$1" | cut -d' ' -f1; }
production_console_sha=$(hash "$production_source/bin/verifast")
production_translator_sha=$(hash "$production_source/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml")
git -C "$production_source" diff > "$evidence/production-applied.patch"
cmp "$production_diff" "$evidence/production-applied.patch"
printf '%s\n' bin/rust/std/lib.rsspec src/rust_frontend/vf_mir_translator/rust_parser.ml src/rust_frontend/vf_mir_translator/vf_mir_translator.ml > "$evidence/production-allowed-files.txt"
git -C "$production_source" diff --name-only > "$evidence/production-modified-files.txt"
cmp "$evidence/production-allowed-files.txt" "$evidence/production-modified-files.txt"

# Copy the exact already patched production checkout, including the pinned
# source tree and support files. This is a distinct directory, not a symlink.
stage source-copy cp -a "$production_source" "$test_source"
[[ "$(git -C "$test_source" rev-parse HEAD)" == f76012fb518703b1d98e243ac4f487f16877cfcb ]] || exit 2
git -C "$test_source" diff > "$evidence/test-before-applied.patch"
cmp "$evidence/production-applied.patch" "$evidence/test-before-applied.patch"
[[ "$(hash "$test_source/bin/verifast")" == "$production_console_sha" ]] || exit 2
stage test-patch-check git -C "$test_source" apply --check "$test_patch"
stage test-patch-apply git -C "$test_source" apply "$test_patch"
git -C "$test_source" diff > "$evidence/test-applied.patch"
git -C "$test_source" diff --name-only > "$evidence/test-modified-files.txt"
cmp "$evidence/production-allowed-files.txt" "$evidence/test-modified-files.txt"
git -C "$test_source" apply --reverse --check "$test_patch"
[[ "$(hash "$production_source/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml")" == "$production_translator_sha" ]] || exit 2

# A cache hit in the production build may have skipped these build-only
# dependencies. Re-establish the pinned vfdeps and decoder in the hosted job.
deps_dir=/vfdeps-adf88dc
if [[ ! -d "$deps_dir" ]]; then
  deps_archive="$RUNNER_TEMP/vfdeps-adf88dc-h2d-linux.txz"
  stage deps-download curl -fL --retry 2 -o "$deps_archive" https://github.com/verifast/vfdeps/releases/download/25.01/vfdeps-adf88dc-linux.txz
  printf '%s  %s\n' 8d022c93d51a1d13ec1e782d767c60462405f6865d5ee416f82d6234e93ee580 "$deps_archive" | sha256sum -c -
  stage deps-extract sudo tar -xjf "$deps_archive" -C /
fi
[[ -d "$deps_dir" ]] || exit 2
if [[ ! -e /tmp/vfdeps-adf88dc ]]; then ln -s "$deps_dir" /tmp/vfdeps-adf88dc; fi
[[ "$(readlink -f /tmp/vfdeps-adf88dc)" == "$deps_dir" ]] || exit 2
export PATH="/tmp/vfdeps-adf88dc/bin:$PATH"
export CAPNP_INC_DIR=/tmp/vfdeps-adf88dc/include
export RUSTUP_TOOLCHAIN=nightly-2026-09-25
export LD_LIBRARY_PATH="$compiler_sysroot/lib:$test_source/bin:/tmp/vfdeps-adf88dc/lib:${LD_LIBRARY_PATH:-}"
if ! command -v capnpc-ocaml-decoder >/dev/null; then
  stage decoder-install cargo install --locked --git https://github.com/btj/capnpc-ocaml-decoder --rev 2d6606d9b59cd0c88a66729f3f076c10c0c8e0b2
fi
[[ "$(hash "$production_source/src/rust_frontend/vf_mir/vf_mir.capnp")" == f48fcf29b99717c2e0cb37d4708b47eccaa3270b999e4a84093e37fbd51b7469 ]] || exit 2
remaining=$((deadline_epoch - $(date +%s) - 90))
(( remaining >= 60 )) || { printf 'Insufficient hosted H2d build time\n' >&2; exit 124; }

# Never reuse or write the production console cache. Remove the copied
# binary so make must link a fresh TEST console from the H2d source overlay.
rm "$test_source/bin/verifast"
stage test-console-build timeout --signal=TERM --kill-after=10s "${remaining}s" make -C "$test_source/src" ../bin/verifast WITHOUT_LABLGTK=yes VERBOSE=yes
[[ -f "$test_source/bin/verifast" ]] || exit 2
# Preserve generated decoder for read-only complete-body representation audit.
[[ -f "$test_source/src/_build/default/rust_frontend/vf_mir_decoder/vf_mir_decoder.ml" ]] || exit 2
cp "$test_source/src/_build/default/rust_frontend/vf_mir_decoder/vf_mir_decoder.ml" "$evidence/vf_mir_decoder.ml"
test_console_sha=$(hash "$test_source/bin/verifast")
[[ "$test_console_sha" != "$production_console_sha" ]] || { printf 'H2d did not rebuild a distinct console\n' >&2; exit 2; }
for name in vf-rust-mir-exporter refinement-checker vf-cxx-ast-exporter libz3.so; do
  cmp "$production_source/bin/$name" "$test_source/bin/$name"
  cmp "$stock_home/bin/$name" "$test_source/bin/$name"
done
cmp "$production_source/bin/rust/std/lib.rsspec" "$test_source/bin/rust/std/lib.rsspec"
ldd "$test_source/bin/verifast" > "$evidence/test-console-ldd.txt"
if grep -q 'not found' "$evidence/test-console-ldd.txt"; then exit 2; fi

python3 - "$repo" "$production_source" "$test_source" "$stock_home" "$test_patch" "$evidence" <<'AUDIT'
import hashlib, json, pathlib, sys
repo,prod,test,stock,patch,ev=map(pathlib.Path,sys.argv[1:])
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
paths=["bin/verifast","bin/vf-rust-mir-exporter","bin/refinement-checker",
       "bin/rust/std/lib.rsspec","src/rust_frontend/vf_mir/vf_mir.capnp",
       "src/rust_frontend/vf_mir_translator/vf_mir_translator.ml",
       "src/rust_frontend/vf_mir_translator/rust_parser.ml"]
manifest={"profile":"H2D_TEST_ONLY_NOT_PRODUCTION",
          "proof_sha":__import__("subprocess").check_output(
              ["git","-C",str(repo),"rev-parse","HEAD"],text=True).strip(),
          "verifast_source_sha":__import__("subprocess").check_output(
              ["git","-C",str(prod),"rev-parse","HEAD"],text=True).strip(),
          "production_applied_diff_sha256":h(ev/"production-applied.patch"),
          "test_applied_diff_sha256":h(ev/"test-applied.patch"),
          "test_overlay_patch_sha256":h(patch),
          "production":{p:h(prod/p) for p in paths},
          "test":{p:h(test/p) for p in paths},
          "stock_exporter_sha256":h(stock/"bin/vf-rust-mir-exporter"),
          "production_console_cache_used":None,
          "test_console_cache_used":False,
          "actual_or_s6_run_on_test_console":False}
(ev/"test-console-manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
AUDIT

remaining=$((deadline_epoch - $(date +%s) - 20))
(( remaining >= 30 )) || { printf 'Insufficient hosted H2d diagnostic time\n' >&2; exit 124; }
stage test-post-matrix timeout --signal=TERM --kill-after=10s "${remaining}s" python3 "$repo/research/challenge-8/overnight-guard/capture-h2b-post-mutation.py" \
  --tool-home "$test_source" \
  --schema "$test_source/src/rust_frontend/vf_mir/vf_mir.capnp" \
  --compiler-sysroot "$compiler_sysroot" \
  --evidence "$evidence/post-mutation" \
  --deadline-epoch "$deadline_epoch" \
  --guard-root "$repo" --template-root "$repo"
python3 - "$evidence/post-mutation/summary.json" <<'CHECK'
import json, pathlib, sys
data=json.loads(pathlib.Path(sys.argv[1]).read_text())
assert data["results"] and data["results"][0]["classification"]=="UNMODIFIED_LOCAL_POSITIVE_PROVED"
assert data["component_accepted"] is False and data["actual_nested_drop_proved"] is False
CHECK
printf '%s\n' H2D_TEST_ONLY_DIAGNOSTIC_NOT_PRODUCTION > "$evidence/PROFILE-STATUS.txt"
