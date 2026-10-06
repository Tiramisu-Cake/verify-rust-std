#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0 OR MIT
# Hosted-only exact-source CopyOnDrop destructor proof gate.
set -euo pipefail

if [[ "${GITHUB_ACTIONS:-}" != true || "${RUNNER_ENVIRONMENT:-}" != github-hosted || "${RUNNER_OS:-}" != Linux ]]; then
    echo 'CopyOnDrop gate requires a GitHub-hosted Linux Actions runner' >&2
    exit 2
fi

repo=$(git rev-parse --show-toplevel)
cd "$repo"
evidence="$repo/research-results/verifast-drop-gate"
export VFVERSION=26.09
export VFPLATFORM=linux
export RUSTUP_TOOLCHAIN=nightly-2026-02-05

if [[ "${1:-}" == --stages ]]; then
    cd "$evidence"
    . "$repo/verifast-proofs/setup-verifast-home"
    {
        printf 'VeriFast pin: %s\nRust toolchain: %s\n' "$VFVERSION" "$RUSTUP_TOOLCHAIN"
        rustc --version --verbose
        sha256sum "$VERIFAST_HOME/bin/verifast" "$VERIFAST_HOME/bin/refinement-checker" \
            "$VERIFAST_HOME/bin/vf-rust-mir-exporter" "$VERIFAST_HOME/bin/rust/prelude.rsspec"
    } > "$evidence/environment.txt" 2>&1

    source_home="${RUNNER_TEMP:?}/challenge8-verifast-drop-gate"
    bash "$repo/research/challenge-8/build-verifast-tuple-parser.sh" \
        "$VERIFAST_HOME" "$evidence" "$source_home" tuple_manually_drop_ref
    export VERIFAST_HOME="$source_home"
    export LD_LIBRARY_PATH="$VERIFAST_HOME/bin:${LD_LIBRARY_PATH:-}"
    vf_options=(-verbose 1)
    printf 'Source-built verifier: %s\nLD_LIBRARY_PATH: %s\n' "$VERIFAST_HOME" "$LD_LIBRARY_PATH" >> "$evidence/environment.txt"

    run_regression() {
        local name=$1
        shift
        set +e
        /usr/bin/time -v -o "$evidence/$name-resources.txt" "$@" \
            > "$evidence/$name.log" 2>&1
        local result=$?
        set -e
        printf '%s\n' "$result" > "$evidence/$name-exit-code.txt"
        cat "$evidence/$name.log"
        if (( result != 0 )); then exit "$result"; fi
    }

    run_regression hrtb-regressions bash "$repo/research/challenge-8/run-verifast-hrtb-regressions.sh" \
        "$source_home" "$evidence/hrtb-regressions"
    run_regression lft-cut-regressions bash "$repo/research/challenge-8/run-verifast-lft-cut-regressions.sh" \
        "$source_home" "$evidence/lft-cut-regressions"
    run_regression address-regressions bash "$repo/research/challenge-8/run-verifast-address-regressions.sh" \
        "$source_home" "$evidence/address-regressions" tracked_manually_drop

    workdir="$evidence/drop"
    mkdir -p "$workdir"
    set +e
    /usr/bin/time -v -o "$evidence/extraction-resources.txt" \
        python3 "$repo/research/challenge-8/extract-verifast-drop.py" \
        --source "$repo/library/core/src/slice/sort/shared/smallsort.rs" \
        --output "$workdir" --evidence "$workdir/extraction.json" \
        > "$evidence/extraction.log" 2>&1
    extraction_status=$?
    set -e
    printf '%s\n' "$extraction_status" > "$evidence/extraction-exit-code.txt"
    cat "$evidence/extraction.log"
    if (( extraction_status != 0 )); then exit "$extraction_status"; fi
    [[ -s "$workdir/original/lib.rs" && -s "$workdir/verified/lib.rs" && -s "$workdir/extraction.json" ]]
    jq -e '.exact_destination_values == true and .generic_T == true and .arbitrary_len == true and .body_source_unchanged == true and .ghost_strip_exact_bytes == true and
        .block_bytes == 364 and .block_sha256 == "caff1edbfa3a8d9fd29459e49c43abd0f8f987f9061c75e7bf6ecedbbba26a6a" and
        .source_sha256 == "32574fd06623190132f213cbfeaeca5bd466e3c802ca97a2174e24fd3c240959" and
        (.contract_sha256 | type == "string" and length == 64)' \
        "$workdir/extraction.json" > "$evidence/extraction-audit.json"
    sha256sum "$workdir/original/lib.rs" "$workdir/verified/lib.rs" "$workdir/extraction.json" \
        > "$evidence/extraction-files-sha256.txt"
    printf '%s  %s\n' "$(jq -r '.original_sha256' "$workdir/extraction.json")" "$workdir/original/lib.rs" | sha256sum -c -
    printf '%s  %s\n' "$(jq -r '.verified_sha256' "$workdir/extraction.json")" "$workdir/verified/lib.rs" | sha256sum -c -
    sha256sum "$workdir/original/lib.rs" "$workdir/verified/lib.rs" \
        "$repo/library/core/src/slice/sort/shared/smallsort.rs" > "$evidence/drop-source-before.txt"
    cd "$workdir"

    compiler_sysroot=$(rustc --print sysroot)
    compiler_libdir="$compiler_sysroot/lib"
    decoder=/tmp/vfdeps-adf88dc/bin/capnp
    schema="$source_home/src/rust_frontend/vf_mir/vf_mir.capnp"
    [[ -x "$decoder" && -f "$schema" ]]
    sha256sum "$compiler_libdir"/librustc_driver-*.so >> "$evidence/environment.txt"
    set +e
    LD_LIBRARY_PATH="$compiler_libdir:$VERIFAST_HOME/bin:${LD_LIBRARY_PATH:-}" \
        /usr/bin/time -v -o "$evidence/compiler-mir-resources.txt" \
        "$VERIFAST_HOME/bin/vf-rust-mir-exporter" verified/lib.rs \
        "--sysroot=$compiler_sysroot" --edition 2021 \
        --vf-rust-mir-exporter:preprocess-readonly \
        > "$evidence/compiler-mir.bin" 2> "$evidence/compiler-mir.log"
    compiler_mir_status=$?
    set -e
    printf '%s\n' "$compiler_mir_status" > "$evidence/compiler-mir-exit-code.txt"
    sha256sum "$workdir/original/lib.rs" "$workdir/verified/lib.rs" \
        "$repo/library/core/src/slice/sort/shared/smallsort.rs" > "$evidence/drop-source-after-mir.txt"
    cmp "$evidence/drop-source-before.txt" "$evidence/drop-source-after-mir.txt"
    if (( compiler_mir_status != 0 )); then cat "$evidence/compiler-mir.log" >&2; exit "$compiler_mir_status"; fi
    set +e
    /usr/bin/time -v -o "$evidence/compiler-mir-decode-resources.txt" "$decoder" decode \
        -I /tmp/vfdeps-adf88dc/include "$schema" VfMir \
        < "$evidence/compiler-mir.bin" > "$evidence/compiler-mir.txt" 2> "$evidence/compiler-mir-decode.log"
    compiler_decode_status=$?
    set -e
    printf '%s\n' "$compiler_decode_status" > "$evidence/compiler-mir-decode-exit-code.txt"
    if (( compiler_decode_status != 0 )); then cat "$evidence/compiler-mir-decode.log" >&2; exit "$compiler_decode_status"; fi
    expected_mir_target='<CopyOnDrop<T> as core::ops::Drop>::drop'
    mir_target_count=$(grep -F -c "$expected_mir_target" "$evidence/compiler-mir.txt" || true)
    mir_copy_call_count=$(grep -F -c 'copy_nonoverlapping' "$evidence/compiler-mir.txt" || true)
    printf '%s\n' "$expected_mir_target" > "$evidence/compiler-mir-expected-target.txt"
    printf '%s\n' "$mir_target_count" > "$evidence/compiler-mir-drop-target-count.txt"
    printf '%s\n' "$mir_copy_call_count" > "$evidence/compiler-mir-copy-call-count.txt"
    rg -n -F "$expected_mir_target" "$evidence/compiler-mir.txt" > "$evidence/compiler-mir-drop-target-evidence.txt" || true
    rg -n -F 'copy_nonoverlapping' "$evidence/compiler-mir.txt" > "$evidence/compiler-mir-copy-call-evidence.txt" || true
    if (( mir_target_count != 1 || mir_copy_call_count < 1 )); then
        echo 'Compiler MIR must contain one actual generic Drop definition and its copy_nonoverlapping call' >&2
        exit 1
    fi
    sha256sum "$evidence/compiler-mir.bin" "$evidence/compiler-mir.txt" >> "$evidence/environment.txt"

    set +e
    /usr/bin/time -v -o "$evidence/verifast-resources.txt" \
        "$VERIFAST_HOME/bin/verifast" -rustc_args '--edition 2021' "${vf_options[@]}" \
        -skip_specless_fns verified/lib.rs > "$evidence/verifast.log" 2>&1
    vf_status=$?
    /usr/bin/time -v -o "$evidence/refinement-resources.txt" \
        "$VERIFAST_HOME/bin/refinement-checker" --rustc-args '--edition 2021' \
        original/lib.rs verified/lib.rs > "$evidence/refinement.log" 2>&1
    refinement_status=$?
    set -e
    printf '%s\n' "$vf_status" > "$evidence/verifast-exit-code.txt"
    printf '%s\n' "$refinement_status" > "$evidence/refinement-exit-code.txt"
    sha256sum "$workdir/original/lib.rs" "$workdir/verified/lib.rs" \
        "$repo/library/core/src/slice/sort/shared/smallsort.rs" > "$evidence/drop-source-after.txt"
    cmp "$evidence/drop-source-before.txt" "$evidence/drop-source-after.txt"

    expected_target=$(jq -r '.expected_target_name' "$workdir/extraction.json")
    [[ "$expected_target" == '<CopyOnDrop<T> as core::ops::Drop>::drop' ]]
    target_core_count=$(grep -F -c "Verifying function '$expected_target'" "$evidence/verifast.log" || true)
    vf_target_std=${expected_target/core::ops::Drop/std::ops::Drop}
    target_std_count=$(grep -F -c "Verifying function '$vf_target_std'" "$evidence/verifast.log" || true)
    target_count=$((target_core_count + target_std_count))
    copy_call_line=$(jq -r '.target_copy_call_line' "$workdir/extraction.json")
    [[ "$copy_call_line" =~ ^[1-9][0-9]*$ ]]
    copy_call_record_count=$(grep -E -c "verified/lib[.]rs\\(${copy_call_line},[0-9]+(-[0-9]+(,[0-9]+)?)?\\): Verifying call$" "$evidence/verifast.log" || true)
    copy_statement_record_count=$(grep -E -c "verified/lib[.]rs\\(${copy_call_line},[0-9]+(-[0-9]+(,[0-9]+)?)?\\): (note: )?Executing statement$" "$evidence/verifast.log" || true)
    statement_count=$(grep -E -c 'verified/lib[.]rs\([0-9]+,[0-9]+(-[0-9]+(,[0-9]+)?)?\): (note: )?Executing (statement|return statement)$' "$evidence/verifast.log" || true)
    printf '%s\n' "$target_count" > "$evidence/verified-drop-target-count.txt"
    printf '%s\n' "$target_core_count" > "$evidence/verified-drop-target-core-name-count.txt"
    printf '%s\n' "$target_std_count" > "$evidence/verified-drop-target-std-name-count.txt"
    printf '%s\n' "$statement_count" > "$evidence/verified-drop-statement-count.txt"
    printf '%s\n' "$copy_call_line" > "$evidence/verified-copy-call-source-line.txt"
    printf '%s\n' "$copy_call_record_count" > "$evidence/verified-copy-call-record-count.txt"
    printf '%s\n' "$copy_statement_record_count" > "$evidence/verified-copy-statement-record-count.txt"
    rg -n "Verifying function '(<CopyOnDrop<T> as core::ops::Drop>::drop|<CopyOnDrop<T> as std::ops::Drop>::drop)'|verified/lib[.]rs\\(${copy_call_line},[0-9]+(-[0-9]+(,[0-9]+)?)?\\): (Verifying call|(note: )?Executing statement)$" \
        "$evidence/verifast.log" > "$evidence/verified-drop-body-evidence.txt" || true
    cat "$evidence/verifast.log" "$evidence/refinement.log"
    if (( vf_status != 0 || refinement_status != 0 || target_count != 1 || statement_count < 1 || copy_call_record_count != 1 || copy_statement_record_count < 1 )); then
        echo 'CopyOnDrop gate failed: require verifier/refinement success and actual Drop body/copy-call execution evidence' >&2
        exit 1
    fi
    exit 0
fi

budget=${1:-90}
case "$budget" in 30|60|90|120) ;; *) echo 'Budget must be 30, 60, 90 or 120 minutes' >&2; exit 2 ;; esac
[[ ! -e "$evidence" ]] || { echo 'Refusing to reuse CopyOnDrop evidence directory' >&2; exit 2; }
mkdir -p "$evidence"
{
    printf 'Source commit: '
    git rev-parse HEAD
    printf 'Selection: %s\nTotal budget including setup: %s minutes\n' \
        "${PROOF_SELECTION:-verifast_copy_on_drop_gate}" "$budget"
    printf 'Verifier pin: %s (%s)\nRust toolchain: %s\n' "$VFVERSION" "$VFPLATFORM" "$RUSTUP_TOOLCHAIN"
    printf 'Hosted runner: %s / %s\n' "$RUNNER_ENVIRONMENT" "$RUNNER_OS"
    uname -a
    sha256sum research/challenge-8/build-verifast-tuple-parser.sh \
        research/challenge-8/run-verifast-drop-gate.sh \
        research/challenge-8/extract-verifast-drop.py \
        research/challenge-8/verifast-manually-drop-ref.patch \
        research/challenge-8/verifast-end-lft-binding.patch \
        research/challenge-8/verifast-address-taken.patch
    printf 'Pinned SmallSort source SHA-256: 32574fd06623190132f213cbfeaeca5bd466e3c802ca97a2174e24fd3c240959\n'
} > "$evidence/selection.txt"

set +e
/usr/bin/time -v -o "$evidence/resources.txt" \
    timeout --signal=TERM --kill-after=30s "${budget}m" \
    bash "$repo/research/challenge-8/run-verifast-drop-gate.sh" --stages \
    2>&1 | tee "$evidence/execution.log"
status=${PIPESTATUS[0]}
set -e
printf '%s\n' "$status" > "$evidence/exit-code.txt"
if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
    {
        printf '### SmallSort CopyOnDrop destructor gate\n\n'
        printf 'Selection: `verifast_copy_on_drop_gate`\n\n'
        printf 'Exit code: `%s` (124 means total setup/proof timeout).\n' "$status"
    } >> "$GITHUB_STEP_SUMMARY"
fi
exit "$status"
