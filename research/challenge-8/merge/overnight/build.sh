#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0 OR MIT
# Build or restore only the SHA-pinned VeriFast 26.10 console for this frozen profile.
set -euo pipefail

fail() { printf 'ERROR: %s\n' "$*" >&2; exit 2; }
[[ "${GITHUB_ACTIONS:-}" == true && "${RUNNER_ENVIRONMENT:-}" == github-hosted && "${RUNNER_OS:-}" == Linux ]] ||
  fail 'VeriFast source builds require GitHub-hosted Linux Actions'
. /etc/os-release
[[ "$ID" == ubuntu && "$VERSION_ID" == 22.04 ]] || fail 'requires GitHub-hosted Ubuntu 22.04'

release_home=${1:?usage: build.sh release_home evidence_dir fresh_source_dir}
evidence=${2:?usage: build.sh release_home evidence_dir fresh_source_dir}
source_home=${3:?usage: build.sh release_home evidence_dir fresh_source_dir}
repo=$(git rev-parse --show-toplevel)
patch_file="$repo/research/challenge-8/merge/overnight/wrapping.patch"
callback_patch="$repo/research/challenge-8/merge/overnight/callback.patch"
callback_sha=0a006df94f04d6425d70280967d6652bdd33ccb88ead4a44f02a2e36775aaa5e
copy_patch="$repo/research/challenge-8/merge/overnight/copy.patch"
copy_sha=da167ee095e9fb5f425e2d604dd46a973a8c1e3a5121b2c87cc3546b0ec8e9a5
cleanup_patch="$repo/research/challenge-8/merge/overnight/cleanup.patch"
cleanup_sha=94fe2cd69edc9da6907553961ca32f0557c338266d9e9472e577860a95887604
patched_kernel_sha=100eebae92c770a0b8cd57e2639588761f881316dd522fc3b9a9b1ec6fd91cd6
patched_translator_sha=0e450267e453493f894b91763ef9412bf41b7ee8d3988115f24126456ab4e025
vf_commit=f76012fb518703b1d98e243ac4f487f16877cfcb
vfdeps_sha=8d022c93d51a1d13ec1e782d767c60462405f6865d5ee416f82d6234e93ee580
vfdeps_z3_sha=1837668dc531d14b3a4fffc0b690b77929d29c41868f98a89686f5ff64da95ea
decoder_rev=2d6606d9b59cd0c88a66729f3f076c10c0c8e0b2
decoder_url=https://github.com/btj/capnpc-ocaml-decoder
patch_sha=c7c776ff5aef2b8668aa2ed3d59b47109fce1d67a9dc2f2043fc2744dc0ed31e
release_console_sha=9b7650ad3ab0dad3b8974ae9ba1c662ab2cd897ce1dd07215dedcbe460249ee1
release_exporter_sha=b00c75f43ab4d89bf85f5e62a5114a238b89b720d4598d90423347b9d97ac796
release_refiner_sha=b049c8d1b0bb350f77664e1c75c5a95966c5839984abc25c7cb629c0cba04d28
translator_rel=src/rust_frontend/vf_mir_translator/vf_mir_translator.ml
prelude_rel=bin/rust/prelude_core.rsspec
std_lib_rel=bin/rust/std/lib.rsspec
parser_rel=src/rust_frontend/vf_mir_translator/rust_parser.ml
allowed_files=$(printf '%s\n' "$translator_rel" "$prelude_rel" "$std_lib_rel" "$parser_rel" src/verifast.ml | LC_ALL=C sort)

[[ ! -e "$evidence" ]] || fail "refusing to reuse evidence directory: $evidence"
[[ ! -e "$source_home" ]] || fail "refusing to reuse source directory: $source_home"
[[ -x "$release_home/bin/vf-rust-mir-exporter" && -x "$release_home/bin/refinement-checker" ]] ||
  fail 'pinned release exporter/refiner are missing'
printf '%s  %s\n' "$release_console_sha" "$release_home/bin/verifast" | sha256sum -c -
printf '%s  %s\n' "$release_exporter_sha" "$release_home/bin/vf-rust-mir-exporter" | sha256sum -c -
printf '%s  %s\n' "$release_refiner_sha" "$release_home/bin/refinement-checker" | sha256sum -c -
[[ -f "$patch_file" ]] || fail "missing reviewed patch: $patch_file"
mkdir -p "$evidence"
trap 's=$?; printf "%s\n" "$s" > "$evidence/source-build-exit-code.txt"' EXIT

run_stage() {
  local stage=$1 status
  shift
  set +e
  /usr/bin/time -v -o "$evidence/$stage-resources.txt" "$@" > "$evidence/$stage.log" 2>&1
  status=$?
  set -e
  printf '%s\n' "$status" > "$evidence/$stage-exit-code.txt"
  cat "$evidence/$stage.log"
  (( status == 0 )) || exit "$status"
}

{
  printf 'Profile: VeriFast26.10 source console + separate experimental wrapping/callback/copy/strict-cleanup patches\n'
  printf 'Source commit: %s\nVFdeps archive SHA256: %s\nDecoder revision: %s\n' "$vf_commit" "$vfdeps_sha" "$decoder_rev"
  printf 'Runner: %s / %s\n' "$RUNNER_ENVIRONMENT" "$RUNNER_OS"
  cat /etc/os-release
  printf 'Patch: %s\n' "$patch_file"
  sha256sum "$patch_file" "$release_home/bin/verifast" \
    "$release_home/bin/vf-rust-mir-exporter" "$release_home/bin/refinement-checker"
} > "$evidence/source-build-inputs.txt"
printf '%s  %s\n' "$patch_sha" "$patch_file" | sha256sum -c -
printf '%s  %s\n' "$callback_sha" "$callback_patch" | sha256sum -c -
printf '%s  %s\n' "$copy_sha" "$copy_patch" | sha256sum -c -
printf '%s  %s\n' "$cleanup_sha" "$cleanup_patch" | sha256sum -c -
sha256sum "$callback_patch" >> "$evidence/source-build-inputs.txt"
sha256sum "$copy_patch" >> "$evidence/source-build-inputs.txt"
sha256sum "$cleanup_patch" >> "$evidence/source-build-inputs.txt"

# Pin the source tree by immutable commit, then check out only that commit.
run_stage source-init git init "$source_home"
run_stage source-origin git -C "$source_home" remote add origin https://github.com/verifast/verifast.git
run_stage source-fetch git -C "$source_home" fetch --depth=1 origin "$vf_commit"
run_stage source-checkout git -C "$source_home" checkout --detach FETCH_HEAD
actual_commit=$(git -C "$source_home" rev-parse HEAD)
printf '%s\n' "$actual_commit" > "$evidence/verifast-source-commit.txt"
[[ "$actual_commit" == "$vf_commit" ]] || fail "source pin mismatch: $actual_commit"

# Verify original kernel and immutable exporter/refiner inputs before the explicit cleanup patch.
kernel_sha=adbf2c3de02cba7fbdb0b8e203a864e34c1b2ab16de4f6b153477106dbba04d0
exporter_lib_sha=11f1e10bb8e52a4950611f874b1123c11e2c87cbb1378c3f5060992f74425f00
printf '%s  %s\n' "$kernel_sha" "$source_home/src/verifast.ml" | sha256sum -c -
printf '%s  %s\n' "$exporter_lib_sha" "$source_home/src/rust_frontend/vf_mir_exporter/src/lib.rs" | sha256sum -c -
(cd "$source_home" && find src/refinement_checker -type f -print0 | sort -z | xargs -0 sha256sum) > "$evidence/refiner-source.sha256"
(cd "$source_home" && find src/rust_frontend/vf_mir_exporter -type f -print0 | sort -z | xargs -0 sha256sum) > "$evidence/exporter-source.sha256"
cp "$source_home/src/verifast.ml" "$evidence/verifast.kernel.original.ml"
cp "$source_home/$translator_rel" "$evidence/translator.original.ml"
cp "$source_home/$parser_rel" "$evidence/parser.original.ml"
cp "$source_home/$prelude_rel" "$evidence/prelude_core.original.rsspec"
cp "$source_home/$std_lib_rel" "$evidence/std_lib.original.rsspec"

# Audit the explicit frontend/spec/strict-kernel paths; exporter/refiner remain immutable.
git -C "$source_home" apply --numstat "$patch_file" > "$evidence/patch-numstat.txt"
git -C "$source_home" apply --numstat "$callback_patch" >> "$evidence/patch-numstat.txt"
git -C "$source_home" apply --numstat "$copy_patch" >> "$evidence/patch-numstat.txt"
git -C "$source_home" apply --numstat "$cleanup_patch" >> "$evidence/patch-numstat.txt"
awk -F '\t' 'NF != 3 { exit 1 } { print $3 }' "$evidence/patch-numstat.txt" | LC_ALL=C sort -u > "$evidence/patch-files.txt"
[[ -s "$evidence/patch-files.txt" ]] || fail 'wrapping.patch contains no file changes'
if comm -23 "$evidence/patch-files.txt" <(printf '%s\n' "$allowed_files") | grep -q .; then
  fail 'patch contains paths outside the explicit frontend/spec/strict-kernel allowlist'
fi
run_stage patch-check git -C "$source_home" apply --check "$patch_file"
run_stage patch-apply git -C "$source_home" apply --whitespace=error "$patch_file"
run_stage callback-patch-check git -C "$source_home" apply --check "$callback_patch"
run_stage callback-patch-apply git -C "$source_home" apply --whitespace=error "$callback_patch"
run_stage copy-patch-check git -C "$source_home" apply --check "$copy_patch"
run_stage copy-patch-apply git -C "$source_home" apply --whitespace=error "$copy_patch"
run_stage cleanup-patch-check git -C "$source_home" apply --check "$cleanup_patch"
run_stage cleanup-patch-apply git -C "$source_home" -c core.whitespace=cr-at-eol apply --whitespace=error "$cleanup_patch"
printf '%s  %s\n' "$patched_kernel_sha" "$source_home/src/verifast.ml" | sha256sum -c -
printf '%s  %s\n' "$patched_translator_sha" "$source_home/$translator_rel" | sha256sum -c -
printf '%s  %s\n' "$exporter_lib_sha" "$source_home/src/rust_frontend/vf_mir_exporter/src/lib.rs" | sha256sum -c -
cp "$source_home/src/verifast.ml" "$evidence/verifast.kernel.patched.ml"
git -C "$source_home" diff --name-only > "$evidence/source-modified-files.txt"
diff -u "$evidence/patch-files.txt" "$evidence/source-modified-files.txt" || fail 'applied tree differs from the audited patch paths'
git -C "$source_home" diff --binary > "$evidence/applied-profile.patch"
sha256sum "$evidence/applied-profile.patch" > "$evidence/applied-profile.patch.sha256"
cp "$source_home/$translator_rel" "$evidence/translator.patched.ml"
cp "$source_home/$parser_rel" "$evidence/parser.patched.ml"
cp "$source_home/$prelude_rel" "$evidence/prelude_core.patched.rsspec"
cp "$source_home/$std_lib_rel" "$evidence/std_lib.patched.rsspec"
sha256sum "$evidence"/translator.* "$evidence"/prelude_core.* "$evidence"/std_lib.* >> "$evidence/source-build-inputs.txt"
sha256sum "$evidence"/parser.* >> "$evidence/source-build-inputs.txt"

# Keep toolchain providers pinned; use runner-provided build utilities without apt upgrades.
for tool in git curl tar sha256sum make gcc cargo rustc grep python3 realpath; do command -v "$tool" >/dev/null || fail "required runner tool missing: $tool"; done
deps_archive=${VFDEPS_ARCHIVE:-"$RUNNER_TEMP/vfdeps-adf88dc-linux.txz"}
if [[ ! -f "$deps_archive" ]]; then
  run_stage vfdeps-download curl --fail --location --retry 3 --output "$deps_archive" \
    https://github.com/verifast/vfdeps/releases/download/25.01/vfdeps-adf88dc-linux.txz
fi
printf '%s  %s\n' "$vfdeps_sha" "$deps_archive" | sha256sum -c -
printf '%s\n' "$deps_archive" > "$evidence/vfdeps-archive-path.txt"
[[ ! -e /vfdeps-adf88dc && ! -e /tmp/vfdeps-adf88dc ]] || fail 'refusing to overwrite an existing VFdeps installation'
run_stage vfdeps-extract sudo tar -xjf "$deps_archive" -C /
[[ -d /vfdeps-adf88dc ]] || fail 'pinned VFdeps extraction did not produce expected directory'
run_stage vfdeps-link ln -s /vfdeps-adf88dc /tmp/vfdeps-adf88dc
export PATH="/tmp/vfdeps-adf88dc/bin:$PATH"
export CAPNP_INC_DIR=/tmp/vfdeps-adf88dc/include
export LD_LIBRARY_PATH="$source_home/bin:/tmp/vfdeps-adf88dc/lib:${LD_LIBRARY_PATH:-}"
{
  command -v ocamlc ocamlfind dune capnp
  gcc --version
  make --version
  cargo --version
  rustc --version
  ocamlc -version
  dune --version
  capnp --version
  ocamlfind printconf
  ocamlfind query -qe Z3 || ocamlfind query z3
  sha256sum "$(command -v gcc)" "$(command -v make)" "$(command -v cargo)" "$(command -v rustc)" \
    "$(command -v realpath)" \
    /tmp/vfdeps-adf88dc/bin/ocamlc /tmp/vfdeps-adf88dc/bin/dune /tmp/vfdeps-adf88dc/bin/capnp
} > "$evidence/build-toolchain.txt" 2>&1
run_stage decoder-install cargo install --locked --git "$decoder_url" --rev "$decoder_rev"
{ command -v capnpc-ocaml-decoder; sha256sum "$(command -v capnpc-ocaml-decoder)"; cargo install --list; } >> "$evidence/build-toolchain.txt"

# Mirror the pinned GNUmakefile Z3_DLL_DIR resolution and stage only that exact
# VFdeps library. The source checkout does not contain bin/libz3.so yet.
z3_ocaml_dir=$(ocamlfind query -qe Z3 2>/dev/null || true)
if [[ -n "$z3_ocaml_dir" ]]; then
  z3_dll_dir="$z3_ocaml_dir/../.."
else
  z3_ocaml_dir=$(ocamlfind query z3) || fail 'pinned VFdeps Z3 OCaml package is missing'
  z3_dll_dir="$z3_ocaml_dir"
fi
z3_dll_dir=$(realpath -e "$z3_dll_dir") || fail 'cannot resolve the pinned Z3 DLL directory'
vfdeps_lib_dir=$(realpath -e /tmp/vfdeps-adf88dc/lib) || fail 'pinned VFdeps library directory is missing'
[[ "$z3_dll_dir" == "$vfdeps_lib_dir" ]] || fail "unexpected Z3_DLL_DIR: $z3_dll_dir"
z3_lib=$(realpath -e "$z3_dll_dir/libz3.so") || fail 'pinned VFdeps libz3.so is missing'
[[ "$z3_lib" == "$vfdeps_lib_dir/libz3.so" ]] || fail "Z3 library escaped pinned VFdeps: $z3_lib"
printf '%s  %s\n' "$vfdeps_z3_sha" "$z3_lib" | sha256sum -c -
[[ ! -e "$source_home/bin/libz3.so" && ! -L "$source_home/bin/libz3.so" ]] ||
  fail 'fresh source tree unexpectedly already has bin/libz3.so'
run_stage z3-runtime-stage cp "$z3_lib" "$source_home/bin/libz3.so"
cmp "$z3_lib" "$source_home/bin/libz3.so"
printf 'Z3_OCAML_DIR=%s\nZ3_DLL_DIR=%s\nZ3_LIBRARY=%s\n' \
  "$z3_ocaml_dir" "$z3_dll_dir" "$z3_lib" > "$evidence/z3-runtime-source.txt"
sha256sum "$z3_lib" "$source_home/bin/libz3.so" >> "$evidence/z3-runtime-source.txt"

# Build only the console. Exporter/refiner remain the byte-identical release files.
cache_helper="$repo/research/challenge-8/merge/overnight/console-cache.py"
cache_profile="$evidence/console-cache-profile.txt"
profile_hash() {
  local key=$1 path=$2 line digest
  line=$(sha256sum "$path")
  digest=${line%% *}
  printf '%s=%s\n' "$key" "$digest"
}
{
  printf 'profile_id=vf26.10-w1-m2-c1-cleanup-ubuntu22.04-v1\n'
  printf 'runner_os=%s\nrunner_version=%s\nsource_commit=%s\n' "$RUNNER_OS" "$VERSION_ID" "$actual_commit"
  profile_hash wrapping_patch "$patch_file"
  profile_hash callback_patch "$callback_patch"
  profile_hash copy_patch "$copy_patch"
  profile_hash cleanup_patch "$cleanup_patch"
  profile_hash release_console "$release_home/bin/verifast"
  profile_hash release_exporter "$release_home/bin/vf-rust-mir-exporter"
  profile_hash release_refiner "$release_home/bin/refinement-checker"
  profile_hash vfdeps_archive "$deps_archive"
  printf 'decoder_revision=%s\n' "$decoder_rev"
  profile_hash build_toolchain "$evidence/build-toolchain.txt"
  profile_hash build_script "$repo/research/challenge-8/merge/overnight/build.sh"
  profile_hash cache_helper "$cache_helper"
  profile_hash applied_patch "$evidence/applied-profile.patch"
  profile_hash kernel_original "$evidence/verifast.kernel.original.ml"
  profile_hash kernel_patched "$evidence/verifast.kernel.patched.ml"
  profile_hash translator_original "$evidence/translator.original.ml"
  profile_hash translator_patched "$evidence/translator.patched.ml"
  profile_hash parser_original "$evidence/parser.original.ml"
  profile_hash parser_patched "$evidence/parser.patched.ml"
  profile_hash prelude_original "$evidence/prelude_core.original.rsspec"
  profile_hash prelude_patched "$evidence/prelude_core.patched.rsspec"
  profile_hash stdlib_original "$evidence/std_lib.original.rsspec"
  profile_hash stdlib_patched "$evidence/std_lib.patched.rsspec"
  profile_hash z3_runtime "$source_home/bin/libz3.so"
} > "$cache_profile"

cache_dir=${VF_CONSOLE_CACHE_DIR:-}
cache_hit=false
if [[ -n "$cache_dir" ]]; then
  if python3 "$cache_helper" restore --cache-dir "$cache_dir" --profile "$cache_profile" \
      --destination "$source_home/bin/verifast" --evidence "$evidence"; then
    cache_hit=true
    printf 'cache-hit\n' > "$evidence/console-build-mode.txt"
    printf 'Console make was skipped because the exact cached console and profile were verified.\n' \
      > "$evidence/console-build-skipped.txt"
  fi
fi
if [[ "$cache_hit" != true ]]; then
  if [[ -z "$cache_dir" ]]; then
    printf 'cold-cache-disabled\n' > "$evidence/console-build-mode.txt"
  else
    printf 'cold-cache-miss\n' > "$evidence/console-build-mode.txt"
  fi
  run_stage console-build make -C "$source_home/src" ../bin/verifast WITHOUT_LABLGTK=yes VERBOSE=yes
fi
if [[ -n "$cache_dir" && "$cache_hit" != true ]]; then
  python3 "$cache_helper" publish --cache-dir "$cache_dir" --profile "$cache_profile" \
    --binary "$source_home/bin/verifast" --producer-sha "$GITHUB_SHA" --evidence "$evidence" || true
fi
if [[ -x "$source_home/bin/verifast" ]]; then
  console_line=$(sha256sum "$source_home/bin/verifast")
  console_digest=${console_line%% *}
  if [[ "$console_digest" == 3a08722cedc2f07daf26dfde2f46b8710662028ca5924212c4d1d92d68b70f1a ]]; then
    python3 "$cache_helper" self-test --profile "$cache_profile" \
      --binary "$source_home/bin/verifast" --evidence "$evidence" || fail 'console cache fail-closed self-test failed'
  else
    printf 'not-run: console differs from the admitted cache digest (%s)\n' "$console_digest" \
      > "$evidence/console-cache-self-test-status.txt"
  fi
fi
cp "$release_home/bin/vf-rust-mir-exporter" "$source_home/bin/vf-rust-mir-exporter"
cp "$release_home/bin/refinement-checker" "$source_home/bin/refinement-checker"
cmp "$release_home/bin/vf-rust-mir-exporter" "$source_home/bin/vf-rust-mir-exporter"
cmp "$release_home/bin/refinement-checker" "$source_home/bin/refinement-checker"
# C++ translation is unchanged. Pair the console with the exact release helper;
# the release archive hash gates this additional executable and prelude.
cp "$release_home/bin/vf-cxx-ast-exporter" "$source_home/bin/vf-cxx-ast-exporter"
cmp "$release_home/bin/vf-cxx-ast-exporter" "$source_home/bin/vf-cxx-ast-exporter"
cmp "$release_home/bin/prelude_cxx.h" "$source_home/bin/prelude_cxx.h"
{
  sha256sum "$source_home/bin/verifast" "$source_home/bin/vf-rust-mir-exporter" \
    "$source_home/bin/refinement-checker" "$release_home/bin/vf-rust-mir-exporter" "$release_home/bin/refinement-checker"
  printf 'LD_LIBRARY_PATH=%s\n' "$LD_LIBRARY_PATH"
  ldd "$source_home/bin/verifast"
  printf 'Bundled binary/spec resource hashes:\n'
  find "$source_home/bin" -type f ! -name verifast ! -name vf-rust-mir-exporter ! -name refinement-checker -print0 | sort -z | xargs -0 sha256sum
} > "$evidence/source-build-runtime.txt" 2>&1
ldd "$source_home/bin/verifast" > "$evidence/source-console-ldd.txt"
if ! grep -F "libz3.so => $source_home/bin/libz3.so " "$evidence/source-console-ldd.txt"; then
  fail 'source console did not resolve its paired pinned Z3'
fi
if grep -q 'not found' "$evidence/source-console-ldd.txt"; then fail 'source console has unresolved dynamic libraries'; fi
printf 'Source console build complete. No verifier or C suite was run by this helper.\n' | tee "$evidence/source-build-status.txt"
