#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0 OR MIT
# Experimental source build. Invoke only inside the probe's overall timeout.
set -euo pipefail
if [[ "${GITHUB_ACTIONS:-}" != true || "${RUNNER_ENVIRONMENT:-}" != github-hosted || "${RUNNER_OS:-}" != Linux ]]; then
    echo 'Source builds require a GitHub-hosted Linux Actions runner' >&2
    exit 2
fi
. /etc/os-release
[[ "$ID" == ubuntu && "$VERSION_ID" == 22.04 ]] || { echo 'This recipe requires Ubuntu22.04' >&2; exit 2; }
repo=$(git rev-parse --show-toplevel)
release_home=${1:?release tool directory required}
evidence=${2:?evidence directory required}
source_home=${3:?fresh source directory required}
mkdir -p "$evidence"
trap 'printf "%s\n" "$?" > "$evidence/source-build-exit-code.txt"' EXIT
vf_commit=809de4596839b739dd999f9e462242c835e3af46
parser_rel=src/rust_frontend/vf_mir_translator/rust_parser.ml
parser_sha=f7f2c2bf573be09d8ce5dcd640ddca0e1437a8f18464facc9621ac287a5082e8
prelude_sha=d7058d43557a2b5147eb1377e85bb67d04b94c83594b6c1c27650c9c571841b5
deps_sha=8d022c93d51a1d13ec1e782d767c60462405f6865d5ee416f82d6234e93ee580
decoder_rev=2d6606d9b59cd0c88a66729f3f076c10c0c8e0b2
patch_file="$repo/research/challenge-8/verifast-tuple-own.patch"
{
    printf 'Experimental tuple2 parser; base26.09 source: %s\nDecoder revision: %s\n' "$vf_commit" "$decoder_rev"
    printf 'VFDeps25.01 archive SHA256: %s\n' "$deps_sha"
    printf 'Source build directory: %s\n' "$source_home"
    cat /etc/os-release
    sha256sum "$patch_file" "$release_home/bin/verifast" "$release_home/bin/vf-rust-mir-exporter" "$release_home/bin/refinement-checker"
} > "$evidence/source-build-inputs.txt"
run_stage() {
    local stage=$1
    shift
    set +e
    /usr/bin/time -v -o "$evidence/$stage-resources.txt" "$@" > "$evidence/$stage.log" 2>&1
    local result=$?
    set -e
    printf '%s\n' "$result" > "$evidence/$stage-exit-code.txt"
    cat "$evidence/$stage.log"
    if (( result != 0 )); then exit "$result"; fi
}
[[ ! -e "$source_home" ]] || { echo 'Refuse to reuse a source build directory' >&2; exit 2; }
run_stage source-checkout git clone --depth 1 --branch 26.09 https://github.com/verifast/verifast.git "$source_home"
actual_commit=$(git -C "$source_home" rev-parse HEAD)
printf '%s\n' "$actual_commit" > "$evidence/verifast-source-commit.txt"
[[ "$actual_commit" == "$vf_commit" ]] || { echo "Source pin mismatch: $actual_commit" >&2; exit 2; }
printf '%s  %s\n' "$parser_sha" "$source_home/$parser_rel" | sha256sum -c -
printf '%s  %s\n' "$prelude_sha" "$source_home/bin/rust/prelude.rsspec" | sha256sum -c -
printf '%s  %s\n' "$prelude_sha" "$release_home/bin/rust/prelude.rsspec" | sha256sum -c -
cp "$source_home/$parser_rel" "$evidence/rust_parser.original.ml"
cp "$source_home/bin/rust/prelude.rsspec" "$evidence/prelude.unmodified.rsspec"
git -C "$source_home" apply --check "$patch_file"
git -C "$source_home" apply "$patch_file"
[[ "$(git -C "$source_home" diff --name-only)" == "$parser_rel" ]]
git -C "$source_home" diff > "$evidence/applied-tuple-parser.patch"
cp "$source_home/$parser_rel" "$evidence/rust_parser.patched.ml"
sha256sum "$evidence/rust_parser.original.ml" "$evidence/rust_parser.patched.ml" "$evidence/prelude.unmodified.rsspec" >> "$evidence/source-build-inputs.txt"
run_stage build-apt bash -c 'sudo apt-get update && sudo apt-get install --yes --no-install-recommends build-essential git curl ca-certificates m4 patch unzip'
deps_archive="$RUNNER_TEMP/challenge8-vfdeps-adf88dc-linux.txz"
run_stage vfdeps-download curl -fL --retry 3 -o "$deps_archive" https://github.com/verifast/vfdeps/releases/download/25.01/vfdeps-adf88dc-linux.txz
printf '%s  %s\n' "$deps_sha" "$deps_archive" | sha256sum -c -
# Preserve the archive's compiled-in /vfdeps prefix, as upstream setup does.
[[ ! -e /vfdeps-adf88dc && ! -e /tmp/vfdeps-adf88dc ]]
# Despite the .txz name, upstream setup-build.sh uses bzip2 (-j).
run_stage vfdeps-extract sudo tar -xjf "$deps_archive" -C /
[[ -d /vfdeps-adf88dc ]]
ln -s /vfdeps-adf88dc /tmp/vfdeps-adf88dc
export PATH="/tmp/vfdeps-adf88dc/bin:$PATH"
export CAPNP_INC_DIR=/tmp/vfdeps-adf88dc/include
export LD_LIBRARY_PATH="$source_home/bin:/tmp/vfdeps-adf88dc/lib:${LD_LIBRARY_PATH:-}"
{
    command -v ocamlc ocamlfind dune capnp
    gcc --version
    make --version
    dpkg-query -W build-essential git curl ca-certificates m4 patch unzip
    ocamlc -version
    dune --version
    capnp --version
    ocamlfind printconf
    ocamlfind query -qe Z3 || ocamlfind query z3
    sha256sum /tmp/vfdeps-adf88dc/bin/ocamlc /tmp/vfdeps-adf88dc/bin/dune /tmp/vfdeps-adf88dc/bin/capnp
} > "$evidence/build-toolchain.txt" 2>&1
run_stage decoder-install cargo install --locked --git https://github.com/btj/capnpc-ocaml-decoder --rev "$decoder_rev"
{
    command -v capnpc-ocaml-decoder
    sha256sum "$(command -v capnpc-ocaml-decoder)"
    cargo install --list
} >> "$evidence/build-toolchain.txt"
# All probe inputs are .rs: final C manifest linking is not used. Build the
# console artifact alone; do not generate, reuse or fabricate C manifests.
run_stage console-build make -C "$source_home/src" ../bin/verifast WITHOUT_LABLGTK=yes VERBOSE=yes
# Rust frontend wire protocol is unchanged. Keep source console/Z3/specs together.
cp "$release_home/bin/vf-rust-mir-exporter" "$source_home/bin/vf-rust-mir-exporter"
cp "$release_home/bin/refinement-checker" "$source_home/bin/refinement-checker"
cmp "$release_home/bin/vf-rust-mir-exporter" "$source_home/bin/vf-rust-mir-exporter"
cmp "$release_home/bin/refinement-checker" "$source_home/bin/refinement-checker"
printf '%s  %s\n' "$prelude_sha" "$source_home/bin/rust/prelude.rsspec" | sha256sum -c -
{
    printf 'Experimental derived26.09 binary; not unchanged release.\n'
    sha256sum "$source_home/bin/verifast" "$source_home/bin/libz3.so" "$source_home/bin/vf-rust-mir-exporter" "$source_home/bin/refinement-checker"
    printf 'LD_LIBRARY_PATH: %s\nDynamic libraries of source console:\n' "$LD_LIBRARY_PATH"
    ldd "$source_home/bin/verifast"
    printf 'All bundled source resource hashes:\n'
    find "$source_home/bin" -type f ! -name verifast ! -name vf-rust-mir-exporter ! -name refinement-checker -print0 | sort -z | xargs -0 sha256sum
} > "$evidence/source-build-runtime.txt" 2>&1
ldd "$source_home/bin/verifast" > "$evidence/source-console-ldd.txt"
if ! rg -F "libz3.so => $source_home/bin/libz3.so " "$evidence/source-console-ldd.txt"; then
    echo 'Source console did not resolve its paired pinned Z3' >&2
    exit 2
fi
if rg -q 'not found' "$evidence/source-build-runtime.txt"; then
    echo 'Source console has unresolved dynamic libraries' >&2
    exit 2
fi
printf 'Console source build completed; proceeding to actual insertion probe.\n'
