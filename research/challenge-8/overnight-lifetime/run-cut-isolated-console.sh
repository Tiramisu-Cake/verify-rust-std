#!/usr/bin/env bash
# Hosted-only diagnostic for the strict lifetime-cut candidate. The production
# console/source/cache remain read-only; the cut console has its own tree.
set -euo pipefail
[[ "${GITHUB_ACTIONS:-}" == true && "${RUNNER_ENVIRONMENT:-}" == github-hosted && "${RUNNER_OS:-}" == Linux ]] || exit 2

repo=$(git rev-parse --show-toplevel)
production_source=
production_diff=
stock_home=
compiler_sysroot=
evidence=
deadline_epoch=
relocate_only=0
while (($#)); do
  case "$1" in
    --production-source) production_source=$2; shift 2 ;;
    --production-applied-patch) production_diff=$2; shift 2 ;;
    --stock-home) stock_home=$2; shift 2 ;;
    --compiler-sysroot) compiler_sysroot=$2; shift 2 ;;
    --evidence) evidence=$2; shift 2 ;;
    --deadline-epoch) deadline_epoch=$2; shift 2 ;;
    --relocate-only) relocate_only=1; shift ;;
    *) printf 'Unknown CUT option: %s\n' "$1" >&2; exit 2 ;;
  esac
done
[[ -n "$production_source" && -n "$production_diff" && -n "$stock_home" && -n "$compiler_sysroot" && -n "$evidence" && -n "$deadline_epoch" ]] || exit 2
[[ "$deadline_epoch" =~ ^[0-9]+$ ]] || exit 2
[[ -d "$production_source/.git" && -f "$production_diff" && -f "$production_source/bin/verifast" && -f "$stock_home/bin/vf-rust-mir-exporter" && -d "$compiler_sysroot/lib" ]] || exit 2
[[ ! -e "$evidence" ]] || { printf 'Refusing existing CUT evidence: %s\n' "$evidence" >&2; exit 2; }
[[ "$(git -C "$production_source" rev-parse HEAD)" == f76012fb518703b1d98e243ac4f487f16877cfcb ]] || exit 2

cut_patch="$repo/research/challenge-8/overnight-lifetime/verifast-strict-lft-cut-26.10.patch"
[[ -f "$cut_patch" ]] || exit 2
printf '%s  %s\n' d557082b0c17771acd7386ad6caca7bc139877cf1ca513d9570da210b1b542d8 "$cut_patch" | sha256sum -c -
cut_source="$RUNNER_TEMP/overnight-cut-isolated-source"
[[ ! -e "$cut_source" ]] || { printf 'Refusing existing CUT source copy: %s\n' "$cut_source" >&2; exit 2; }
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
git -C "$production_source" diff > "$evidence/production-applied.patch"
cmp "$production_diff" "$evidence/production-applied.patch"
printf '%s\n' bin/rust/std/lib.rsspec src/rust_frontend/vf_mir_translator/rust_parser.ml src/rust_frontend/vf_mir_translator/vf_mir_translator.ml > "$evidence/production-allowed-files.txt"
git -C "$production_source" diff --name-only > "$evidence/production-modified-files.txt"
cmp "$evidence/production-allowed-files.txt" "$evidence/production-modified-files.txt"
printf '%s\n' bin/rust/std/lib.rsspec src/rust_frontend/vf_mir_translator/rust_parser.ml src/rust_frontend/vf_mir_translator/vf_mir_translator.ml src/verifast.ml > "$evidence/cut-allowed-files.txt"
printf '%s  %s\n' f48fcf29b99717c2e0cb37d4708b47eccaa3270b999e4a84093e37fbd51b7469 "$production_source/src/rust_frontend/vf_mir/vf_mir.capnp" | sha256sum -c -

# Copy exact production bytes, then apply only the reviewed cut overlay.
stage source-copy cp -a "$production_source" "$cut_source"
[[ "$(git -C "$cut_source" rev-parse HEAD)" == f76012fb518703b1d98e243ac4f487f16877cfcb ]] || exit 2
git -C "$cut_source" diff > "$evidence/cut-before-applied.patch"
cmp "$evidence/production-applied.patch" "$evidence/cut-before-applied.patch"
[[ "$(hash "$cut_source/bin/verifast")" == "$production_console_sha" ]] || exit 2
stage cut-patch-check git -C "$cut_source" apply --check "$cut_patch"
stage cut-patch-apply git -C "$cut_source" apply "$cut_patch"
if (( relocate_only )); then
  for entry in 'verifast-cut-relocate-callback-TESTONLY.patch e7189430eca9a48ed49d280131bd22987af8d05ed43a88f9c4a5c9767e57bb9e' 'verifast-strict-cut-entry-trace-TESTONLY.patch bc129b381af7bfe8cd5ca56eef099d90312ad7695dbbf852864d0e28148a4c3b'; do
    read -r name expected_sha <<< "$entry"
    overlay="$repo/research/challenge-8/overnight-lifetime/$name"
    printf '%s  %s\n' "$expected_sha" "$overlay" | sha256sum -c -
    stage "$name-check" git -C "$cut_source" apply --check "$overlay"
    stage "$name-apply" git -C "$cut_source" apply "$overlay"
  done
fi
git -C "$cut_source" diff > "$evidence/cut-applied.patch"
git -C "$cut_source" diff --name-only > "$evidence/cut-modified-files.txt"
cmp "$evidence/cut-allowed-files.txt" "$evidence/cut-modified-files.txt"
if (( relocate_only == 0 )); then
  git -C "$cut_source" apply --reverse --check "$cut_patch"
fi
cmp "$production_source/src/rust_frontend/vf_mir/vf_mir.capnp" "$cut_source/src/rust_frontend/vf_mir/vf_mir.capnp"
cmp "$production_source/bin/rust/std/lib.rsspec" "$cut_source/bin/rust/std/lib.rsspec"
cmp "$production_source/src/rust_frontend/vf_mir_translator/rust_parser.ml" "$cut_source/src/rust_frontend/vf_mir_translator/rust_parser.ml"

# A production cache hit may omit build-only dependencies. Restore pinned
# vfdeps/decoder on the hosted runner without writing production cache files.
deps_dir=/vfdeps-adf88dc
if [[ ! -d "$deps_dir" ]]; then
  deps_archive="$RUNNER_TEMP/vfdeps-adf88dc-cut-linux.txz"
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
export LD_LIBRARY_PATH="$compiler_sysroot/lib:$cut_source/bin:/tmp/vfdeps-adf88dc/lib:${LD_LIBRARY_PATH:-}"
if ! command -v capnpc-ocaml-decoder >/dev/null; then
  stage decoder-install cargo install --locked --git https://github.com/btj/capnpc-ocaml-decoder --rev 2d6606d9b59cd0c88a66729f3f076c10c0c8e0b2
fi
remaining=$((deadline_epoch - $(date +%s) - 90))
(( remaining >= 60 )) || { printf 'Insufficient hosted CUT build time\n' >&2; exit 124; }

# Force a fresh console from CUT source. Never reuse/write production cache.
rm "$cut_source/bin/verifast"
stage cut-console-build timeout --signal=TERM --kill-after=10s "${remaining}s" make -C "$cut_source/src" ../bin/verifast WITHOUT_LABLGTK=yes VERBOSE=yes
[[ -f "$cut_source/bin/verifast" ]] || exit 2
[[ -f "$cut_source/src/_build/default/rust_frontend/vf_mir_decoder/vf_mir_decoder.ml" ]] || exit 2
cp "$cut_source/src/_build/default/rust_frontend/vf_mir_decoder/vf_mir_decoder.ml" "$evidence/vf_mir_decoder.ml"
cut_console_sha=$(hash "$cut_source/bin/verifast")
[[ "$cut_console_sha" != "$production_console_sha" ]] || { printf 'CUT did not rebuild a distinct console\n' >&2; exit 2; }
for name in vf-rust-mir-exporter refinement-checker vf-cxx-ast-exporter libz3.so; do
  cmp "$production_source/bin/$name" "$cut_source/bin/$name"
  cmp "$stock_home/bin/$name" "$cut_source/bin/$name"
done
ldd "$cut_source/bin/verifast" > "$evidence/cut-console-ldd.txt"
if grep -q 'not found' "$evidence/cut-console-ldd.txt"; then exit 2; fi
{
  rustc --version --verbose
  capnp --version
  if command -v ocamlc >/dev/null; then ocamlc -version; fi
  if command -v dune >/dev/null; then dune --version; fi
} > "$evidence/hosted-build-versions.txt"

python3 - "$repo" "$production_source" "$cut_source" "$stock_home" "$cut_patch" "$evidence" "$relocate_only" <<'AUDIT'
import hashlib, json, pathlib, subprocess, sys
repo,prod,cut,stock,patch,ev=map(pathlib.Path,sys.argv[1:7])
relocate_only=sys.argv[7]=="1"
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
paths=["bin/verifast","bin/vf-rust-mir-exporter","bin/refinement-checker",
       "bin/rust/std/lib.rsspec","src/rust_frontend/vf_mir/vf_mir.capnp",
       "src/rust_frontend/vf_mir_translator/vf_mir_translator.ml",
       "src/rust_frontend/vf_mir_translator/rust_parser.ml","src/verifast.ml"]
manifest={"profile":"STRICT_CUT_DIAGNOSTIC_NOT_ACCEPTED",
          "proof_sha":subprocess.check_output(["git","-C",str(repo),"rev-parse","HEAD"],text=True).strip(),
          "verifast_source_sha":subprocess.check_output(["git","-C",str(prod),"rev-parse","HEAD"],text=True).strip(),
          "production_applied_diff_sha256":h(ev/"production-applied.patch"),
          "cut_applied_diff_sha256":h(ev/"cut-applied.patch"),
          "cut_overlay_patch_sha256":h(patch),
          "production":{p:h(prod/p) for p in paths},
          "cut":{p:h(cut/p) for p in paths},
          "stock_exporter_sha256":h(stock/"bin/vf-rust-mir-exporter"),
          "generated_decoder_sha256":h(ev/"vf_mir_decoder.ml"),
          "cut_console_cache_used":False,
          "production_cache_writes":False,
          "actual_sort4_proved":False,
          "mandatory_negative_controls_complete":False}
manifest["relocate_test_only"] = relocate_only
manifest["test_overlays"] = {name:h(repo/"research/challenge-8/overnight-lifetime"/name)
    for name in ("verifast-cut-relocate-callback-TESTONLY.patch",
                 "verifast-strict-cut-entry-trace-TESTONLY.patch")} if relocate_only else {}
prod_specs={str(p.relative_to(prod)):h(p) for p in (prod/"bin/rust").rglob("*.rsspec")}
cut_specs={str(p.relative_to(cut)):h(p) for p in (cut/"bin/rust").rglob("*.rsspec")}
assert prod_specs==cut_specs
manifest["effective_spec_sha256"] = prod_specs
(ev/"cut-console-manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
AUDIT

schema="$cut_source/src/rust_frontend/vf_mir/vf_mir.capnp"
if (( relocate_only )); then
  relocation_status=0
  SORT4_STRICT_LFT_TRACE=1 stage relocation-diagnostic python3 "$repo/research/challenge-8/overnight-lifetime/capture-relocate.py" \
    --tool-home "$cut_source" --out "$evidence/relocate" \
    --deadline-epoch "$deadline_epoch" || relocation_status=$?
  git -C "$production_source" diff > "$evidence/production-after-applied.patch"
  cmp "$production_diff" "$evidence/production-after-applied.patch"
  [[ "$(hash "$production_source/bin/verifast")" == "$production_console_sha" ]] || exit 2
  printf 'relocation_status=%s\nprofile=TEST_RELOCATION_DIAGNOSTIC_ONLY\naccepted=false\nproduction_unchanged=true\n' "$relocation_status" > "$evidence/aggregate-stage-status.txt"
  exit "$relocation_status"
fi
lawful_test_positive_status=0
stage lawful-test-positive python3 "$repo/research/challenge-8/overnight-lifetime-test/capture-positive.py"   --tool-home "$cut_source" --out "$evidence/lawful-test-positive"   --deadline-epoch "$deadline_epoch" || lawful_test_positive_status=$?
cut_matrix_status=0
stage cut-matrix python3 "$repo/research/challenge-8/overnight-lifetime/capture.py" \
  --tool-home "$cut_source" --out "$evidence/cut-matrix" --deadline-epoch "$deadline_epoch" || cut_matrix_status=$?
no_optin_status=0
stage cut-no-opt-in python3 "$repo/research/challenge-8/overnight-lifetime/capture.py" \
  --tool-home "$cut_source" --out "$evidence/cut-no-opt-in" --deadline-epoch "$deadline_epoch" \
  --case positive_basic --without-opt-in || no_optin_status=$?
export SORT4_SELECT_PROFILE=experimental-s6-26.10-v1
unset SORT4_STRICT_LFT_CUT
s6_status=0
stage s6-full-matrix python3 "$repo/research/challenge-8/overnight-s6/accept-s6.py" \
  --stock-home "$stock_home" --tool-home "$cut_source" --schema "$schema" \
  --compiler-sysroot "$compiler_sysroot" --evidence "$evidence/s6-full" \
  --deadline-epoch "$deadline_epoch" || s6_status=$?
callback_status=0
stage callback-no-cut python3 "$repo/research/challenge-8/overnight-callback/probe.py" \
  --repo-root "$repo" --source-checkout "$cut_source" --tool-home "$cut_source" \
  --schema "$schema" --compiler-sysroot "$compiler_sysroot" \
  --evidence "$evidence/callback-no-cut" --deadline-epoch "$deadline_epoch" \
  --case all --unwind-matrix --enable-hrtb || callback_status=$?

callback_classifier_status=0
python3 - "$evidence/callback-no-cut/summary.json" "$evidence/callback-no-cut-classification.json" <<'CALLBACK' || callback_classifier_status=$?
import json, pathlib, sys
summary,output=map(pathlib.Path,sys.argv[1:])
expected={
  "callback_positive":"DIAGNOSTIC_POSITIVE_CANDIDATE_REVIEW_REQUIRED",
  "callback_false_post":"INTENDED_FALSE_NORMAL_POST",
  "unwind_missing_marker":"INTENDED_UNWIND_MARKER_ADMISSION_REJECTION",
  "unwind_duplicate_marker":"INTENDED_UNWIND_MARKER_ADMISSION_REJECTION",
  "unwind_moved_marker":"INTENDED_UNWIND_MARKER_ADMISSION_REJECTION",
  "unwind_foreign_marker":"INTENDED_UNWIND_MARKER_ADMISSION_REJECTION",
  "unwind_false_post":"INTENDED_FALSE_UNWIND_POST",
  "unwind_duplicate_f_owner":"INTENDED_DUPLICATE_UNWIND_OWNER_CANDIDATE_REVIEW_REQUIRED",
  "unwind_duplicate_left_owner":"INTENDED_DUPLICATE_UNWIND_OWNER_CANDIDATE_REVIEW_REQUIRED",
}
data=json.loads(summary.read_text()) if summary.exists() else {}
observed={name:case.get("classification") for name,case in data.get("cases",{}).items()}
record={"expected":expected,"observed":observed,"exact_match":observed==expected}
output.write_text(json.dumps(record,indent=2,sort_keys=True)+"\n")
if observed!=expected: raise SystemExit(1)
CALLBACK
printf 'lawful_test_positive_status=%s\ncut_matrix_status=%s\nno_opt_in_status=%s\ns6_full_status=%s\ncallback_status=%s\ncallback_classifier_status=%s\nprofile=STRICT_CUT_DIAGNOSTIC_NOT_ACCEPTED\n' \
  "$lawful_test_positive_status" "$cut_matrix_status" "$no_optin_status" "$s6_status" "$callback_status" "$callback_classifier_status" > "$evidence/aggregate-stage-status.txt"
git -C "$production_source" diff > "$evidence/production-after-applied.patch"
cmp "$production_diff" "$evidence/production-after-applied.patch"
[[ "$(hash "$production_source/bin/verifast")" == "$production_console_sha" ]] || exit 2
if (( lawful_test_positive_status || cut_matrix_status || no_optin_status || s6_status || callback_status || callback_classifier_status )); then exit 1; fi
printf '%s\n' STRICT_CUT_DIAGNOSTIC_ONLY > "$evidence/PROFILE-STATUS.txt"
