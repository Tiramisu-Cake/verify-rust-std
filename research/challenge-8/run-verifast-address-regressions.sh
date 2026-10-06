#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0 OR MIT
# Address-taking traversal regressions; these are not SmallSort proofs.
set -euo pipefail

if [[ "${GITHUB_ACTIONS:-}" != true || "${RUNNER_ENVIRONMENT:-}" != github-hosted || "${RUNNER_OS:-}" != Linux ]]; then
    echo 'Address-taking regressions require a GitHub-hosted Linux Actions runner' >&2
    exit 2
fi

repo=$(git rev-parse --show-toplevel)
source_home=${1:?source-built VeriFast directory required}
results=${2:?fresh regression evidence directory required}
evidence=$(dirname "$results")
case "$source_home" in "${RUNNER_TEMP:?}"/*) ;; *) echo 'Verifier must be in RUNNER_TEMP' >&2; exit 2 ;; esac
[[ ! -e "$results" ]] || { echo 'Refusing non-fresh regression evidence directory' >&2; exit 2; }
[[ -x "$source_home/bin/verifast" && -x "$source_home/bin/vf-rust-mir-exporter" ]]
[[ -f "$evidence/source-build-inputs.txt" && "$(cat "$evidence/source-build-exit-code.txt")" == 0 ]]
patch="$repo/research/challenge-8/verifast-address-taken.patch"
patch_sha=$(sha256sum "$patch" | cut -d ' ' -f 1)
rg -F "$patch_sha" "$evidence/source-build-inputs.txt" >/dev/null
rg -F 'MergeFractionsStmt(_, a) -> ass_mark_addr_taken a locals; cont locals' "$source_home/src/verify_expr.ml" >/dev/null
mkdir -p "$results"
export RUSTUP_TOOLCHAIN=nightly-2026-02-05
export LD_LIBRARY_PATH="$source_home/bin:${LD_LIBRARY_PATH:-}"
template="$repo/research/challenge-8/verifast-address-regressions.rs"
compiler_sysroot=$(rustc --print sysroot)
compiler_libdir="$compiler_sysroot/lib"
decoder=/tmp/vfdeps-adf88dc/bin/capnp
schema="$source_home/src/rust_frontend/vf_mir/vf_mir.capnp"
[[ -x "$decoder" && -f "$schema" ]]
{
    printf 'Selection: address-taking continuation regression fixtures; no SmallSort proof claim\n'
    printf 'Source-built verifier: %s\nPatch SHA-256: %s\n' "$source_home" "$patch_sha"
    rustc --version --verbose
    sha256sum "$patch" "$template" "$source_home/bin/verifast" "$source_home/bin/vf-rust-mir-exporter"
    ldd "$source_home/bin/verifast"
} > "$results/environment.txt" 2>&1
rg -F "libz3.so => $source_home/bin/libz3.so " "$results/environment.txt" >/dev/null
printf 'case\texporter\tdecoder\tverifier\tclassification\tevidence\n' > "$results/results.tsv"

run_case() {
    local name=$1 kind=$2 expected=$3 case_dir="$results/$1"
    mkdir -p "$case_dir"
    local fixture="$case_dir/lib.rs" log="$case_dir/verifast.log"
    awk -v selected="$name" '
        /^\/\/ CASE_BEGIN / { seen = 1; active = ($3 == selected); if (active) count++; next }
        /^\/\/ CASE_END / { if (active) active = 0; next }
        !seen || active { print }
        END { if (count != 1) exit 3 }
    ' "$template" > "$fixture"
    [[ "$(grep -E -c '^pub unsafe fn ' "$fixture")" == 1 && "$(grep -F -c "fn $name" "$fixture")" == 1 ]] || { echo "$name: isolated fixture does not contain exactly one function" >&2; return 1; }
    sha256sum "$template" "$fixture" > "$case_dir/source-before.txt"
    set +e
    LD_LIBRARY_PATH="$compiler_libdir:$source_home/bin:${LD_LIBRARY_PATH:-}" \
        /usr/bin/time -v -o "$case_dir/exporter-resources.txt" \
        "$source_home/bin/vf-rust-mir-exporter" "$fixture" "--sysroot=$compiler_sysroot" \
        --edition 2021 --crate-type lib --vf-rust-mir-exporter:preprocess-readonly \
        > "$case_dir/mir.bin" 2> "$case_dir/exporter.log"
    local exporter=$?
    set -e
    printf '%s\n' "$exporter" > "$case_dir/exporter-exit-code.txt"
    sha256sum "$template" "$fixture" > "$case_dir/source-after.txt"
    cmp "$case_dir/source-before.txt" "$case_dir/source-after.txt"
    local decoder_status=NA
    if (( exporter == 0 )); then
        set +e
        /usr/bin/time -v -o "$case_dir/decoder-resources.txt" "$decoder" decode \
            -I /tmp/vfdeps-adf88dc/include "$schema" VfMir < "$case_dir/mir.bin" \
            > "$case_dir/mir.txt" 2> "$case_dir/decoder.log"
        decoder_status=$?
        set -e
    fi
    printf '%s\n' "$decoder_status" > "$case_dir/decoder-exit-code.txt"
    local status=NA classification=frontend_failure evidence_text=''
    if (( exporter == 0 && decoder_status == 0 )); then
        set +e
        /usr/bin/time -v -o "$case_dir/verifier-resources.txt" timeout --signal=TERM --kill-after=10s 180s \
            "$source_home/bin/verifast" -rustc_args '--edition 2021 --crate-type lib' \
            -skip_specless_fns -verbose 1 "$fixture" > "$log" 2>&1
        status=$?
        set -e
        if rg -q 'Parse error|Rust frontend failed|Failed to run rustc|error\[E[0-9]+\]|error: aborting due' "$log"; then
            classification=frontend_failure
        elif [[ "$kind" == positive ]]; then
            local named statements
            named=$(grep -F -c "Verifying function '$name'" "$log" || true)
            statements=$(grep -E -c 'lib[.]rs\([0-9]+,[0-9]+(-[0-9]+(,[0-9]+)?)?\): (note: )?Executing (statement|return statement)$' "$log" || true)
            if (( status == 0 && named == 1 && statements > 0 )); then classification=positive_verified; fi
            evidence_text="named=$named statements=$statements"
        else
            local named=0
            grep -F "Verifying function '$name'" "$log" >/dev/null && named=1 || true
            if (( status == 1 && named == 1 )) && [[ "$expected" == ownership ]] && \
                rg -qi 'lib[.]rs\([^)]*\): error: No matching heap chunks: .*points_to' "$log"; then
                classification=expected_ownership
            fi
            evidence_text="named=$named"
        fi
    fi
    printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$name" "$exporter" "$decoder_status" "$status" "$classification" "$evidence_text" >> "$results/results.tsv"
    if [[ "$kind" == positive ]]; then [[ "$classification" == positive_verified ]] || return 1
    else [[ "$classification" == expected_* ]] || return 1; fi
}

run_case positive_scalar_after_merge positive ''
run_case positive_manually_drop_after_merge positive ''
run_case negative_read_without_permission negative ownership
printf 'Address-taking regressions passed; permission-negative case requires intended failure.\n'
