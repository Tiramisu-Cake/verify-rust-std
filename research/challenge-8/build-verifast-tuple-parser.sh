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
build_profile=${4:-tuple_parser}
case "$build_profile" in tuple_parser|tuple_hrtb|tuple_lft_cut|tuple_address_taken|tuple_manually_drop_ref|tuple_local_drop) ;; *) echo 'Unknown source-build profile' >&2; exit 2 ;; esac
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
    printf 'Experimental source profile: %s\nBase26.09 source: %s\nDecoder revision: %s\n' "$build_profile" "$vf_commit" "$decoder_rev"
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
expected_modified="$parser_rel"
if [[ "$build_profile" == tuple_hrtb || "$build_profile" == tuple_lft_cut || "$build_profile" == tuple_address_taken || "$build_profile" == tuple_manually_drop_ref || "$build_profile" == tuple_local_drop ]]; then
    translator_rel=src/rust_frontend/vf_mir_translator/vf_mir_translator.ml
    translator_sha=7319d2638c3fc49a1663b50925d565ca2e10d95754933ed58e37f27239936803
    hrtb_patch="$repo/research/challenge-8/verifast-fnmut-hrtb.patch"
    printf '%s  %s\n' "$translator_sha" "$source_home/$translator_rel" | sha256sum -c -
    cp "$source_home/$translator_rel" "$evidence/vf_mir_translator.original.ml"
    sha256sum "$hrtb_patch" >> "$evidence/source-build-inputs.txt"
    git -C "$source_home" apply --check "$hrtb_patch"
    git -C "$source_home" apply "$hrtb_patch"
    if [[ "$build_profile" == tuple_lft_cut || "$build_profile" == tuple_address_taken || "$build_profile" == tuple_manually_drop_ref || "$build_profile" == tuple_local_drop ]]; then
        kernel_rel=src/verifast.ml
        kernel_sha=5968a05e264042782e8373c452b241ccdd1f4ba3323d596888a9bdf6b18c3310
        cut_patch="$repo/research/challenge-8/verifast-end-lft-binding.patch"
        printf '%s  %s\n' "$kernel_sha" "$source_home/$kernel_rel" | sha256sum -c -
        cut_translator_input_sha=ef88c9c08388ef85bc661675f19212041e37b341d5ab61132ff80e5b9080b8d4
        printf '%s  %s\n' "$cut_translator_input_sha" "$source_home/$translator_rel" | sha256sum -c -
        cp "$source_home/$kernel_rel" "$evidence/verifast.original.ml"
        cp "$source_home/$translator_rel" "$evidence/vf_mir_translator.before-lft-cut.ml"
        sha256sum "$cut_patch" "$evidence/vf_mir_translator.before-lft-cut.ml" >> "$evidence/source-build-inputs.txt"
        git -C "$source_home" apply --check "$cut_patch"
        git -C "$source_home" apply "$cut_patch"
        cp "$source_home/$kernel_rel" "$evidence/verifast.patched.ml"
        sha256sum "$evidence/verifast.original.ml" "$evidence/verifast.patched.ml" >> "$evidence/source-build-inputs.txt"
    fi
    cp "$source_home/$translator_rel" "$evidence/vf_mir_translator.patched.ml"
    if [[ "$build_profile" != tuple_manually_drop_ref && "$build_profile" != tuple_local_drop ]]; then
        sha256sum "$evidence/vf_mir_translator.original.ml" "$evidence/vf_mir_translator.patched.ml" >> "$evidence/source-build-inputs.txt"
    fi
    expected_modified="$parser_rel"$'\n'"$translator_rel"
    if [[ "$build_profile" == tuple_lft_cut || "$build_profile" == tuple_address_taken || "$build_profile" == tuple_manually_drop_ref || "$build_profile" == tuple_local_drop ]]; then
        expected_modified+=$'\n'"$kernel_rel"
    fi
    if [[ "$build_profile" == tuple_address_taken || "$build_profile" == tuple_manually_drop_ref || "$build_profile" == tuple_local_drop ]]; then
        expr_rel=src/verify_expr.ml
        expr_sha=af5f7399d63e2ce2d5fc18291466b406c278f49d6bcb966ed49d644782958e2e
        address_patch="$repo/research/challenge-8/verifast-address-taken.patch"
        printf '%s  %s\n' "$expr_sha" "$source_home/$expr_rel" | sha256sum -c -
        cp "$source_home/$expr_rel" "$evidence/verify_expr.original.ml"
        printf '%s\n' "$expr_sha" > "$evidence/verify_expr-original-sha256.txt"
        sha256sum "$address_patch" >> "$evidence/source-build-inputs.txt"
        git -C "$source_home" apply --check "$address_patch"
        git -C "$source_home" apply "$address_patch"
        cp "$source_home/$expr_rel" "$evidence/verify_expr.patched.ml"
        sha256sum "$evidence/verify_expr.original.ml" "$evidence/verify_expr.patched.ml" >> "$evidence/source-build-inputs.txt"
        sha256sum "$source_home/$expr_rel" | cut -d ' ' -f 1 > "$evidence/verify_expr-patched-sha256.txt"
        expected_modified+=$'\n'"$expr_rel"
    fi
    if [[ "$build_profile" == tuple_manually_drop_ref || "$build_profile" == tuple_local_drop ]]; then
        translator_before_ref_sha=15a9db2fbafa0f04e74e75e5bee0dd7d941a7428906e42432e9d9687843bbcce
        manually_drop_patch="$repo/research/challenge-8/verifast-manually-drop-ref.patch"
        printf '%s  %s\n' "$translator_before_ref_sha" "$source_home/$translator_rel" | sha256sum -c -
        cp "$source_home/$translator_rel" "$evidence/vf_mir_translator.before-manually-drop-ref.ml"
        sha256sum "$manually_drop_patch" >> "$evidence/source-build-inputs.txt"
        git -C "$source_home" apply --check "$manually_drop_patch"
        git -C "$source_home" apply "$manually_drop_patch"
        if [[ "$build_profile" == tuple_manually_drop_ref ]]; then
            cp "$source_home/$translator_rel" "$evidence/vf_mir_translator.patched.ml"
            sha256sum "$evidence/vf_mir_translator.original.ml" \
                "$evidence/vf_mir_translator.before-manually-drop-ref.ml" \
                "$evidence/vf_mir_translator.patched.ml" >> "$evidence/source-build-inputs.txt"
            sha256sum "$source_home/$translator_rel" | cut -d ' ' -f 1 > "$evidence/vf_mir_translator-after-manually-drop-ref-sha256.txt"
        fi
    fi
    if [[ "$build_profile" == tuple_local_drop ]]; then
        translator_before_local_drop_sha=f8751fab591ed98daebf446eb34800e892e72a838c7c083f643bd4efabbb0432
        local_drop_patch_sha=bc13ff90cbdc4a937200fb6b20efa2dbb9ceaea0a92d0e428c1fd5b47cc3a65a
        translator_after_local_drop_sha=03bf4a5c460c1babbd79c80dff7d1c4fc02d21add286498df9bd81fe47796213
        local_drop_patch="$repo/research/challenge-8/verifast-local-drop-call.patch"
        printf '%s  %s\n' "$translator_before_local_drop_sha" "$source_home/$translator_rel" | sha256sum -c -
        cp "$source_home/$translator_rel" "$evidence/vf_mir_translator.before-local-drop-call.ml"
        printf '%s  %s\n' "$local_drop_patch_sha" "$local_drop_patch" | sha256sum -c -
        sha256sum "$local_drop_patch" >> "$evidence/source-build-inputs.txt"
        git -C "$source_home" apply --check "$local_drop_patch"
        git -C "$source_home" apply "$local_drop_patch"
        printf '%s  %s\n' "$translator_after_local_drop_sha" "$source_home/$translator_rel" | sha256sum -c -
        cp "$source_home/$translator_rel" "$evidence/vf_mir_translator.patched.ml"
        sha256sum "$evidence/vf_mir_translator.original.ml" \
            "$evidence/vf_mir_translator.before-manually-drop-ref.ml" \
            "$evidence/vf_mir_translator.before-local-drop-call.ml" \
            "$evidence/vf_mir_translator.patched.ml" >> "$evidence/source-build-inputs.txt"
        sha256sum "$source_home/$translator_rel" | cut -d ' ' -f 1 > "$evidence/vf_mir_translator-after-local-drop-call-sha256.txt"
    fi
fi
git -C "$source_home" diff --name-only > "$evidence/source-modified-files.txt"
[[ "$(cat "$evidence/source-modified-files.txt")" == "$expected_modified" ]]
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
