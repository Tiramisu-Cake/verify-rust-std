#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0 OR MIT
# GitHub-hosted-only full VeriFast source build for the exact tuple-2 parser patch.
set -euo pipefail

if [[ "${GITHUB_ACTIONS:-}" != true || "${RUNNER_ENVIRONMENT:-}" != github-hosted || "${RUNNER_OS:-}" != Linux ]]; then
    echo 'VeriFast source builds require a GitHub-hosted Linux runner' >&2
    exit 2
fi
. /etc/os-release
[[ "$ID" == ubuntu && "$VERSION_ID" == 22.04 ]] || {
    echo 'This source-build recipe requires Ubuntu 22.04' >&2
    exit 2
}

repo=$(git rev-parse --show-toplevel)
release_home=${1:?pinned 26.10 base tool home required}
evidence=${2:?evidence directory required}
source_home=${3:?fresh source checkout path required}
vf_commit=f76012fb518703b1d98e243ac4f487f16877cfcb
parser_rel=src/rust_frontend/vf_mir_translator/rust_parser.ml
parser_base_sha=b26422aff8a6091181485a1355fc60e3a2afde5c8bff2bbe5176fdee07b08622
prelude_sha=d7058d43557a2b5147eb1377e85bb67d04b94c83594b6c1c27650c9c571841b5
deps_sha=8d022c93d51a1d13ec1e782d767c60462405f6865d5ee416f82d6234e93ee580
decoder_rev=2d6606d9b59cd0c88a66729f3f076c10c0c8e0b2
patch_file="$repo/research/challenge-8/overnight-callback/verifast-tuple2-own-26.10.patch"
expected_patch_sha=84b58b71bfb65ac2bfac1a63d181239001cf0a7ffba3f8bfb5d5b0f1d3a640da

mkdir -p "$evidence"
trap 'printf "%s\n" "$?" > "$evidence/source-build-exit-code.txt"' EXIT
[[ ! -e "$source_home" ]] || {
    echo 'Refuse to reuse a source checkout or build directory' >&2
    exit 2
}
[[ -f "$release_home/bin/vf-rust-mir-exporter" &&
   -f "$release_home/bin/refinement-checker" ]] || {
    echo 'Pinned 26.10 exporter/refinement-checker bundle is incomplete' >&2
    exit 2
}
printf '%s  %s\n' "$expected_patch_sha" "$patch_file" | sha256sum -c -
printf '%s\n' \
    "source_pin=$vf_commit" \
    "parser_base_sha256=$parser_base_sha" \
    "prelude_sha256=$prelude_sha" \
    "tuple2_patch_sha256=$expected_patch_sha" \
    "decoder_revision=$decoder_rev" \
    "vfdeps_archive_sha256=$deps_sha" \
    "release_verifier_sha256=$(sha256sum "$release_home/bin/verifast" | cut -d ' ' -f 1)" \
    "release_exporter_sha256=$(sha256sum "$release_home/bin/vf-rust-mir-exporter" | cut -d ' ' -f 1)" \
    "release_refiner_sha256=$(sha256sum "$release_home/bin/refinement-checker" | cut -d ' ' -f 1)" \
    > "$evidence/source-build-inputs.txt"

run_stage() {
    local stage=$1
    shift
    set +e
    /usr/bin/time -v -o "$evidence/$stage-resources.txt" "$@" > "$evidence/$stage.log" 2>&1
    local status=$?
    set -e
    printf '%s\n' "$status" > "$evidence/$stage-exit-code.txt"
    if (( status != 0 )); then cat "$evidence/$stage.log" >&2; exit "$status"; fi
}

run_stage source-checkout git clone --no-checkout https://github.com/verifast/verifast.git "$source_home"
run_stage source-fetch git -C "$source_home" fetch --depth 1 origin "$vf_commit"
run_stage source-checkout-pinned git -C "$source_home" checkout --detach FETCH_HEAD
actual_commit=$(git -C "$source_home" rev-parse HEAD)
[[ "$actual_commit" == "$vf_commit" ]] || {
    echo "Source pin mismatch: $actual_commit" >&2
    exit 2
}
printf '%s\n' "$actual_commit" > "$evidence/verifast-source-commit.txt"
printf '%s  %s\n' "$parser_base_sha" "$source_home/$parser_rel" | sha256sum -c -
printf '%s  %s\n' "$prelude_sha" "$source_home/bin/rust/prelude.rsspec" | sha256sum -c -
printf '%s  %s\n' "$prelude_sha" "$release_home/bin/rust/prelude.rsspec" | sha256sum -c -
cp "$source_home/$parser_rel" "$evidence/rust_parser.original.ml"
cp "$source_home/bin/rust/prelude.rsspec" "$evidence/prelude.unmodified.rsspec"
git -C "$source_home" apply --check "$patch_file"
git -C "$source_home" apply "$patch_file"
[[ "$(git -C "$source_home" diff --name-only)" == "$parser_rel" ]]
git -C "$source_home" diff --check
git -C "$source_home" diff > "$evidence/applied-tuple2-parser.patch"
cp "$source_home/$parser_rel" "$evidence/rust_parser.patched.ml"
sha256sum "$evidence/rust_parser.original.ml" "$evidence/rust_parser.patched.ml" \
    "$evidence/prelude.unmodified.rsspec" >> "$evidence/source-build-inputs.txt"

run_stage build-apt bash -c 'sudo apt-get update && sudo apt-get install --yes --no-install-recommends build-essential git curl ca-certificates m4 patch unzip'
deps_archive="${RUNNER_TEMP:?}/challenge8-vfdeps-adf88dc-linux.txz"
run_stage vfdeps-download curl -fL --retry 3 -o "$deps_archive" https://github.com/verifast/vfdeps/releases/download/25.01/vfdeps-adf88dc-linux.txz
printf '%s  %s\n' "$deps_sha" "$deps_archive" | sha256sum -c -
[[ ! -e /vfdeps-adf88dc && ! -e /tmp/vfdeps-adf88dc ]] || {
    echo 'Refuse to reuse the VFDeps prefix from another build' >&2
    exit 2
}
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

cp "$release_home/bin/vf-rust-mir-exporter" "$source_home/bin/vf-rust-mir-exporter"
cp "$release_home/bin/refinement-checker" "$source_home/bin/refinement-checker"
cmp "$release_home/bin/vf-rust-mir-exporter" "$source_home/bin/vf-rust-mir-exporter"
cmp "$release_home/bin/refinement-checker" "$source_home/bin/refinement-checker"
run_stage console-build make -C "$source_home/src" ../bin/verifast WITHOUT_LABLGTK=yes VERBOSE=yes
sha256sum "$source_home/bin/verifast" "$source_home/bin/vf-rust-mir-exporter" \
    "$source_home/bin/refinement-checker" "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" \
    > "$evidence/source-built-tools-sha256.txt"
git -C "$source_home" diff --name-only > "$evidence/source-modified-files.txt"
[[ "$(cat "$evidence/source-modified-files.txt")" == "$parser_rel" ]]
git -C "$source_home" status --porcelain --untracked-files=all > "$evidence/source-status.txt"
[[ "$(cat "$evidence/source-status.txt")" == " M $parser_rel" ]]
printf 'Full source build complete. Run tuple/callback fixtures with tool home: %s\n' "$source_home"
