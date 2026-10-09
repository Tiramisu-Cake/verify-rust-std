#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0 OR MIT
# Cloud-only, separate seventh-component console; six-patch source is read-only.
set -euo pipefail

fail() { printf 'MIR-OR-JOIN-LIVENESS build refusal: %s\n' "$*" >&2; exit 2; }
[[ "${SMALLSORT_EXECUTION_PROVIDER:-}" == cloud-build ]] ||
  fail 'Cloud Build provider is required'
python3 "${SMALLSORT_PROVIDER_FILE:?provider helper is required}" >/dev/null ||
  fail 'Cloud Build provider certificate failed'
. /etc/os-release
[[ "$ID" == ubuntu && "$VERSION_ID" == 22.04 ]] ||
  fail 'pinned Ubuntu 22.04 builder is required'

base=${1:?usage: build-seven.sh base6-source-home base6-build-evidence seven-evidence}
base_evidence=${2:?usage: build-seven.sh base6-source-home base6-build-evidence seven-evidence}
evidence=${3:?usage: build-seven.sh base6-source-home base6-build-evidence seven-evidence}
seven="${RUNNER_TEMP:?RUNNER_TEMP is required}/challenge8-merge-or-join-seven/source"
repo=$(git rev-parse --show-toplevel)
component="$repo/research/challenge-8/merge/overnight/or-join-liveness"
manifest="$component/PINNED-INPUTS.json"
patch_file="$component/or-join-liveness.patch"
translator=src/rust_frontend/vf_mir_translator/vf_mir_translator.ml
kernel=src/verifast.ml
parser=src/rust_frontend/vf_mir_translator/rust_parser.ml
prelude=bin/rust/prelude_core.rsspec
stdlib=bin/rust/std/lib.rsspec

[[ "$seven" == /workspace/* && "$evidence" == /workspace/* ]] ||
  fail 'source/evidence destinations must be inside the disposable Cloud workspace'
[[ "$base" == "$RUNNER_TEMP"/* && "$base_evidence" == /workspace/* &&
   ! -L "$base" && ! -L "$base_evidence" ]] ||
  fail 'six-component inputs must be genuine Cloud workspace paths'
[[ -d "$base/.git" && -f "$base/$translator" &&
   -f "$base_evidence/translator.patched.ml" &&
   -f "$base_evidence/applied-profile.patch" &&
   -f "$base_evidence/source-build-exit-code.txt" ]] ||
  fail 'complete six-component source and evidence are required'
[[ "$(cat "$base_evidence/source-build-exit-code.txt")" == 0 ]] ||
  fail 'six-component baseline build did not finish successfully'
[[ ! -e "$seven" && ! -e "$evidence" ]] ||
  fail 'refusing to reuse seventh-component source or evidence'
mkdir -p "$(dirname "$seven")"
mkdir -p "$evidence"
trap 'status=$?; printf "%s\n" "$status" > "$evidence/seven-build-exit-code.txt"' EXIT

pin() {
  python3 - "$manifest" "$1" <<'PIN'
import json, pathlib, re, sys
value = json.loads(pathlib.Path(sys.argv[1]).read_text())[sys.argv[2]]
if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
    raise SystemExit("invalid seventh-component SHA pin: " + sys.argv[2])
print(value)
PIN
}
check_pin() {
  local key=$1 path=$2
  printf '%s  %s\n' "$(pin "$key")" "$path" | sha256sum -c - >/dev/null ||
    fail "$key mismatch"
}
stage() {
  local name=$1 status=0
  shift
  /usr/bin/time -v -o "$evidence/$name-resources.txt" "$@" \
    > "$evidence/$name.log" 2>&1 || status=$?
  printf '%s\n' "$status" > "$evidence/$name-exit-code.txt"
  (( status == 0 )) || fail "$name failed; see preserved log"
}

[[ "$(git -C "$base" rev-parse HEAD)" == f76012fb518703b1d98e243ac4f487f16877cfcb ]] ||
  fail 'six-component source commit differs from f760 pin'
check_pin baseline_translator_sha256 "$base/$translator"
check_pin baseline_translator_sha256 "$base_evidence/translator.patched.ml"
check_pin component_patch_sha256 "$patch_file"
check_pin admission_checker_sha256 "$component/admit-source.py"
check_pin baseline_console_sha256 "$base/bin/verifast"
check_pin baseline_kernel_sha256 "$base/$kernel"
check_pin baseline_parser_sha256 "$base/$parser"
check_pin baseline_prelude_sha256 "$base/$prelude"
check_pin baseline_stdlib_sha256 "$base/$stdlib"
check_pin release_exporter_sha256 "$base/bin/vf-rust-mir-exporter"
check_pin release_refiner_sha256 "$base/bin/refinement-checker"
base_profile_sha=$(sha256sum "$base_evidence/applied-profile.patch")
base_profile_sha=${base_profile_sha%% *}
[[ "$base_profile_sha" == "$(pin baseline_applied_profile_sha256)" ]] ||
  fail 'baseline six-patch full diff hash mismatch'
printf '%s\n' "$base_profile_sha" > "$evidence/base-six-applied-profile-sha256.txt"

# Copy first; never apply a patch or run make in the six-component source home.
stage copy-base timeout --signal=TERM --kill-after=10s 90s cp -a "$base" "$seven"
cmp "$base/$translator" "$seven/$translator" ||
  fail 'the seventh source copy differs before patch application'
[[ "$(git -C "$seven" rev-parse HEAD)" == f76012fb518703b1d98e243ac4f487f16877cfcb ]] ||
  fail 'copied source commit differs'

numstat=$(git -C "$seven" apply --numstat "$patch_file")
[[ "$(printf '%s\n' "$numstat" | wc -l)" -eq 1 &&
   "${numstat##*$'\t'}" == "$translator" ]] ||
  fail 'component patch changes a path outside the translator'
printf '%s\n' "$numstat" > "$evidence/component-patch-numstat.txt"
stage patch-check git -C "$seven" apply --check "$patch_file"
stage patch-apply git -C "$seven" apply --whitespace=error "$patch_file"
check_pin component_translator_sha256 "$seven/$translator"
cp "$base/$translator" "$evidence/translator.six.ml"
cp "$seven/$translator" "$evidence/translator.seven.ml"
git -C "$seven" diff --binary > "$evidence/full-seven-applied-profile.patch"
git -C "$base" diff --binary > "$evidence/base-six-applied-profile.patch"
cmp "$base_evidence/applied-profile.patch" "$evidence/base-six-applied-profile.patch" ||
  fail 'six-component full patch differs from its build evidence'
git -C "$seven" diff --name-only > "$evidence/seven-modified-files.txt"
cmp "$base/$kernel" "$seven/$kernel"
cmp "$base/$parser" "$seven/$parser"
cmp "$base/$prelude" "$seven/$prelude"
cmp "$base/$stdlib" "$seven/$stdlib"
cmp "$base/bin/vf-rust-mir-exporter" "$seven/bin/vf-rust-mir-exporter"
cmp "$base/bin/refinement-checker" "$seven/bin/refinement-checker"

[[ -d /tmp/vfdeps-adf88dc &&
   -f "$seven/bin/libz3.so" ]] ||
  fail 'pinned baseline VFdeps/Z3 environment is unavailable'
export PATH="/tmp/vfdeps-adf88dc/bin:$PATH"
export CAPNP_INC_DIR=/tmp/vfdeps-adf88dc/include
export LD_LIBRARY_PATH="$seven/bin:/tmp/vfdeps-adf88dc/lib:${LD_LIBRARY_PATH:-}"
for tool in ocamlc dune ocamlfind capnp make; do
  command -v "$tool" >/dev/null || fail "build tool missing: $tool"
done
stage console-build timeout --signal=TERM --kill-after=10s 360s \
  make -C "$seven/src" ../bin/verifast WITHOUT_LABLGTK=yes VERBOSE=yes
[[ -x "$seven/bin/verifast" ]] || fail 'new console binary was not produced'
new_console_sha=$(sha256sum "$seven/bin/verifast")
new_console_sha=${new_console_sha%% *}
[[ "$new_console_sha" != "$(pin baseline_console_sha256)" ]] ||
  fail 'seventh console is byte-identical to the six-component console'
check_pin baseline_console_sha256 "$base/bin/verifast"
check_pin baseline_translator_sha256 "$base/$translator"
check_pin baseline_kernel_sha256 "$base/$kernel"
check_pin baseline_parser_sha256 "$base/$parser"
check_pin baseline_prelude_sha256 "$base/$prelude"
check_pin baseline_stdlib_sha256 "$base/$stdlib"
check_pin release_exporter_sha256 "$seven/bin/vf-rust-mir-exporter"
check_pin release_refiner_sha256 "$seven/bin/refinement-checker"
cmp "$base/$kernel" "$seven/$kernel"
cmp "$base/$parser" "$seven/$parser"
cmp "$base/$prelude" "$seven/$prelude"
cmp "$base/$stdlib" "$seven/$stdlib"
sha256sum "$base/bin/verifast" "$seven/bin/verifast" \
  "$base/$kernel" "$seven/$kernel" "$base/$prelude" "$seven/$prelude" \
  "$base/$stdlib" "$seven/$stdlib" "$base/$parser" "$seven/$parser" \
  "$base/bin/vf-rust-mir-exporter" "$seven/bin/vf-rust-mir-exporter" \
  "$base/bin/refinement-checker" "$seven/bin/refinement-checker" \
  "$evidence/full-seven-applied-profile.patch" \
  > "$evidence/seven-profile-hashes.txt"
ldd "$seven/bin/verifast" > "$evidence/seven-console-ldd.txt"
grep -F "libz3.so => $seven/bin/libz3.so " "$evidence/seven-console-ldd.txt" >/dev/null ||
  fail 'seventh console did not resolve its copied pinned Z3'
if grep -q 'not found' "$evidence/seven-console-ldd.txt"; then
  fail 'seventh console has unresolved dynamic libraries'
fi
python3 - "$manifest" "$evidence" "$base" "$seven" "$new_console_sha" <<'RECORD'
import hashlib, json, pathlib, sys
manifest, evidence, base, seven = map(pathlib.Path, sys.argv[1:5])
console_sha = sys.argv[5]
pin = json.loads(manifest.read_text())
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
result = {
    "component": "MIR-OR-JOIN-LIVENESS",
    "status": "EXPERIMENTAL_BUILD_ONLY",
    "accepted": False,
    "source_commit": pin["verifast_commit"],
    "component_manifest_sha256": digest(manifest),
    "base_six_console_sha256": digest(base / "bin/verifast"),
    "seven_console_sha256": console_sha,
    "component_patch_sha256": pin["component_patch_sha256"],
    "baseline_translator_sha256": pin["baseline_translator_sha256"],
    "component_translator_sha256": pin["component_translator_sha256"],
    "base_six_full_diff_sha256": digest(evidence / "base-six-applied-profile.patch"),
    "seven_full_diff_sha256": digest(evidence / "full-seven-applied-profile.patch"),
    "kernel_unchanged": digest(base / "src/verifast.ml") ==
                        digest(seven / "src/verifast.ml"),
    "parser_unchanged": digest(base / "src/rust_frontend/vf_mir_translator/rust_parser.ml") ==
                        digest(seven / "src/rust_frontend/vf_mir_translator/rust_parser.ml"),
    "prelude_unchanged": digest(base / "bin/rust/prelude_core.rsspec") ==
                         digest(seven / "bin/rust/prelude_core.rsspec"),
    "stdlib_unchanged": digest(base / "bin/rust/std/lib.rsspec") ==
                        digest(seven / "bin/rust/std/lib.rsspec"),
    "exporter_unchanged": digest(base / "bin/vf-rust-mir-exporter") ==
                          digest(seven / "bin/vf-rust-mir-exporter"),
    "refiner_unchanged": digest(base / "bin/refinement-checker") ==
                         digest(seven / "bin/refinement-checker"),
}
(evidence / "seven-profile-manifest.json").write_text(
    json.dumps(result, sort_keys=True, indent=2) + "\n")
RECORD
printf '%s\n' "$seven" > "$evidence/seven-source-home.txt"
printf 'seventh experimental console built; no proof was run\n' \
  > "$evidence/seven-build-status.txt"
