#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0 OR MIT
# Translator regressions, not SmallSort verification. GitHub-hosted Actions only.
set -euo pipefail

if [[ "${GITHUB_ACTIONS:-}" != true || "${RUNNER_ENVIRONMENT:-}" != github-hosted || "${RUNNER_OS:-}" != Linux ]]; then
    echo 'HRTB regressions require a GitHub-hosted Linux Actions runner' >&2
    exit 2
fi

repo=$(git rev-parse --show-toplevel)
source_home=${1:?source-built VeriFast directory required}
regressions=${2:?fresh HRTB regression evidence directory required}
evidence=$(dirname "$regressions")
case "$source_home" in
    "${RUNNER_TEMP:?}"/*) ;;
    *) echo 'Refuse a verifier outside this hosted runner temporary directory' >&2; exit 2 ;;
esac
[[ -x "$source_home/bin/verifast" && -f "$evidence/source-build-inputs.txt" ]]
[[ "$(cat "$evidence/source-build-exit-code.txt")" == 0 ]]
patch="$repo/research/challenge-8/verifast-fnmut-hrtb.patch"
patch_sha=$(sha256sum "$patch" | cut -d ' ' -f 1)
rg -F "$patch_sha" "$evidence/source-build-inputs.txt" >/dev/null
rg -F 'CHALLENGE8_HRTB_EQ' "$source_home/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml" >/dev/null
export RUSTUP_TOOLCHAIN=nightly-2026-02-05
export LD_LIBRARY_PATH="$source_home/bin:${LD_LIBRARY_PATH:-}"
mkdir -p "$regressions"
template="$repo/research/challenge-8/verifast-fnmut-hrtb-regressions.rs"
[[ -f "$template" ]]
compiler_sysroot=$(rustc --print sysroot)
compiler_libdir="$compiler_sysroot/lib"
decoder=/tmp/vfdeps-adf88dc/bin/capnp
schema="$source_home/src/rust_frontend/vf_mir/vf_mir.capnp"
[[ -x "$source_home/bin/vf-rust-mir-exporter" && -x "$decoder" && -f "$schema" ]]
{
    printf 'Selection: translator HRTB matcher regressions; no SmallSort proof claim\n'
    printf 'Source verifier: %s\n' "$source_home"
    rustc --version --verbose
    sha256sum "$patch" "$source_home/bin/verifast" "$template"
    ldd "$source_home/bin/verifast"
} > "$regressions/environment.txt" 2>&1
rg -F "libz3.so => $source_home/bin/libz3.so " "$regressions/environment.txt" >/dev/null
printf 'case\texporter_exit\tdecoder_exit\tMIR_calls\ttranslator_calls\tverifier_exit\tclassification\tequalities\texpected_equalities\tverified_function\n' > "$regressions/results.tsv"

marked_line() {
    local fn_name=$1
    local fixture=$2
    awk -v fn_name="$fn_name" '
        index($0, "pub unsafe fn " fn_name "<") { in_function = 1 }
        in_function && index($0, "/*@::<") { print NR; exit }
    ' "$fixture"
}

run_case() {
    local cfg=$1
    local verified_function=$2
    local expected_markers=$3
    local marked_function=$4
    local expected_calls=$5
    local expected_sections=1
    if [[ "$cfg" == hrtb_second_body ]]; then expected_sections=2; fi
    local case_dir="$regressions/$cfg"
    mkdir -p "$case_dir"
    local fixture="$case_dir/lib.rs"
    # VeriFast collects ghost annotations before rustc cfg elimination. Emit a
    # physical one-case source: retain header and exact selected function text,
    # dropping only cfg selector lines. The dual-body case keeps both sections.
    awk -v selected="$cfg" -v expected="$expected_sections" '
        /^#\[cfg\(hrtb_/ {
            if ($0 !~ /^#\[cfg\(hrtb_[a-z0-9_]+\)\]$/) exit 2
            in_cases = 1
            active = ($0 == "#[cfg(" selected ")]")
            if (active) selected_count++
            next
        }
        !in_cases || active { print }
        END { if (selected_count != expected) exit 3 }
    ' "$template" > "$fixture"
    if rg -q '^#\[cfg\(hrtb_' "$fixture"; then
        echo "$cfg: inactive cfg selector leaked into isolated source" >&2
        return 1
    fi
    local log="$regressions/$cfg.log"
    sha256sum "$template" "$fixture" > "$regressions/$cfg.source-before.txt"
    set +e
    LD_LIBRARY_PATH="$compiler_libdir:$source_home/bin:${LD_LIBRARY_PATH:-}" \
        /usr/bin/time -v -o "$regressions/$cfg.exporter-resources.txt" \
        "$source_home/bin/vf-rust-mir-exporter" "$fixture" \
        "--sysroot=$compiler_sysroot" --edition 2021 --crate-type lib \
        --cfg "$cfg" --vf-rust-mir-exporter:preprocess-readonly \
        > "$regressions/$cfg.mir.bin" 2> "$regressions/$cfg.exporter.log"
    local exporter_status=$?
    set -e
    printf '%s\n' "$exporter_status" > "$regressions/$cfg.exporter-exit-code.txt"
    sha256sum "$template" "$fixture" > "$regressions/$cfg.source-after.txt"
    cmp "$regressions/$cfg.source-before.txt" "$regressions/$cfg.source-after.txt"
    if (( exporter_status != 0 )); then
        echo "$cfg: compiler MIR exporter failed" >&2
        return 1
    fi
    set +e
    /usr/bin/time -v -o "$regressions/$cfg.decoder-resources.txt" \
        "$decoder" decode -I /tmp/vfdeps-adf88dc/include "$schema" VfMir \
        < "$regressions/$cfg.mir.bin" > "$regressions/$cfg.mir.txt" \
        2> "$regressions/$cfg.decoder.log"
    local decoder_status=$?
    set -e
    printf '%s\n' "$decoder_status" > "$regressions/$cfg.decoder-exit-code.txt"
    if (( decoder_status != 0 )); then
        echo "$cfg: compiler MIR decode failed" >&2
        return 1
    fi
    local mir_calls
    mir_calls=$(grep -F -c 'name = "core::ops::FnMut::call_mut"' "$regressions/$cfg.mir.txt" || true)
    if (( mir_calls != expected_calls )); then
        echo "$cfg: MIR exported $mir_calls FnMut calls, expected $expected_calls" >&2
        return 1
    fi
    if [[ "$cfg" == hrtb_no_output ]] &&
       rg -F 'defId = "core::ops::FnOnce::Output"' "$regressions/$cfg.mir.txt" >/dev/null; then
        echo "$cfg: compiler exported an Output equality for the unconstrained case" >&2
        return 1
    fi
    set +e
    /usr/bin/time -v -o "$regressions/$cfg.resources.txt" \
        timeout --signal=TERM --kill-after=10s 180s \
        "$source_home/bin/verifast" \
        -rustc_args "--edition 2021 --crate-type lib --cfg $cfg" \
        -skip_specless_fns -verbose 1 "$fixture" > "$log" 2>&1
    local status=$?
    set -e
    printf '%s\n' "$status" > "$regressions/$cfg.exit-code.txt"
    local markers
    markers=$(grep -F -c 'CHALLENGE8_HRTB_EQ ' "$log" || true)
    local translator_calls
    translator_calls=$(grep -F -c 'CHALLENGE8_HRTB_CALL ' "$log" || true)
    local classification
    if (( status != 1 )); then
        classification=unexpected_exit
    elif rg -q 'No matching heap chunks' "$log"; then
        classification=ownership_failure
    elif rg -q 'error: Type mismatch[.]' "$log"; then
        classification=type_failure
    elif rg -q 'error\[E[0-9]+\]|error: aborting due|Failed to run rustc' "$log"; then
        classification=compiler_or_frontend_failure
    else
        classification=other_verifier_failure
    fi
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
        "$cfg" "$exporter_status" "$decoder_status" "$mir_calls" "$translator_calls" \
        "$status" "$classification" "$markers" "$expected_markers" "$verified_function" \
        >> "$regressions/results.tsv"
    if (( status != 1 )); then
        echo "$cfg: expected verifier exit 1 from a finite ownership/type obligation, got status $status" >&2
        return 1
    fi
    if [[ "$classification" == compiler_or_frontend_failure || "$classification" == other_verifier_failure ]]; then
        echo "$cfg: failure was not classified as an ownership/type obligation" >&2
        return 1
    fi
    if (( translator_calls != expected_calls )); then
        echo "$cfg: translator considered $translator_calls calls, expected $expected_calls" >&2
        return 1
    fi
    local registered_calls
    registered_calls=$(grep -F -c 'CHALLENGE8_HRTB_CALL registered=1 ' "$log" || true)
    if (( registered_calls != expected_markers )); then
        echo "$cfg: considered-call trace registered $registered_calls equalities, expected $expected_markers" >&2
        return 1
    fi
    if ! rg -F "Verifying function '$verified_function'" "$log" >/dev/null; then
        echo "$cfg: no named body verification evidence" >&2
        return 1
    fi
    if (( markers != expected_markers )); then
        echo "$cfg: $markers registration markers; expected $expected_markers" >&2
        return 1
    fi
    if (( expected_markers == 1 )); then
        local line
        line=$(marked_line "$marked_function" "$fixture")
        [[ -n "$line" ]] || { echo "$cfg: no marked source call" >&2; return 1; }
        if ! rg -F "CHALLENGE8_HRTB_EQ F=F T=T lifetime='cmp call=" "$log" |
            rg -q "lib[.]rs\\($line,"; then
            echo "$cfg: equality was not attached to the expected call location" >&2
            return 1
        fi
    fi
}

run_case hrtb_positive positive 1 positive 1
run_case hrtb_u8 non_boolean 0 '' 1
run_case hrtb_no_output unconstrained_output 0 '' 1
run_case hrtb_wrong_f wrong_function_type 0 '' 1
run_case hrtb_wrong_t wrong_referent_type 0 '' 1
run_case hrtb_unequal_lifetimes unequal_lifetimes 0 '' 1
run_case hrtb_second_call second_call_unannotated 1 second_call_unannotated 2
# The bool body appears first; the later u8 body must not inherit its bound.
# Both calls must appear in the translator trace even if verification stops
# at the first body's deliberately missing ownership.
run_case hrtb_second_body first_body 1 first_body 2
printf 'HRTB translator regressions passed; individual verifier exits are expected failures.\n'
