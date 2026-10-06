#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0 OR MIT
# Hosted-only actual local-Drop caller and cleanup-edge gate.
set -euo pipefail

if [[ "${GITHUB_ACTIONS:-}" != true || "${RUNNER_ENVIRONMENT:-}" != github-hosted || "${RUNNER_OS:-}" != Linux ]]; then
    echo 'Local Drop caller gate requires a GitHub-hosted Linux Actions runner' >&2
    exit 2
fi

repo=$(git rev-parse --show-toplevel)
cd "$repo"
evidence="$repo/research-results/verifast-drop-caller-gate"
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

    source_home="${RUNNER_TEMP:?}/challenge8-verifast-drop-caller-gate"
    bash "$repo/research/challenge-8/build-verifast-tuple-parser.sh" \
        "$VERIFAST_HOME" "$evidence" "$source_home" tuple_local_drop
    export VERIFAST_HOME="$source_home"
    export LD_LIBRARY_PATH="$VERIFAST_HOME/bin:${LD_LIBRARY_PATH:-}"
    vf_options=(-verbose 1)
    printf 'Source-built verifier: %s\nLD_LIBRARY_PATH: %s\n' "$VERIFAST_HOME" "$LD_LIBRARY_PATH" >> "$evidence/environment.txt"

    count_verified_header() {
        local name=$1 log=$2
        awk -v target="Verifying function '$name'" '
            index($0, target) && $0 ~ /^[[:space:]]*[0-9]+[.][0-9]+s: / &&
                $0 !~ /: note: Verifying function / { count++ }
            END { print count + 0 }
        ' "$log"
    }

    run_regression() {
        local name=$1
        shift
        set +e
        /usr/bin/time -v -o "$evidence/$name-resources.txt" "$@" > "$evidence/$name.log" 2>&1
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

    decoder=/tmp/vfdeps-adf88dc/bin/capnp
    schema="$source_home/src/rust_frontend/vf_mir/vf_mir.capnp"
    [[ -x "$decoder" && -f "$schema" ]]
    compiler_sysroot=$(rustc --print sysroot)
    compiler_libdir="$compiler_sysroot/lib"
    sha256sum "$compiler_libdir"/librustc_driver-*.so >> "$evidence/environment.txt"

    # First prove the exact actual CopyOnDrop method by itself. This is also
    # the reviewed template reused by the caller extractor below.
    direct="$evidence/direct-drop"
    mkdir -p "$direct"
    run_timed() {
        local name=$1
        shift
        set +e
        /usr/bin/time -v -o "$direct/$name-resources.txt" "$@" > "$direct/$name.log" 2>&1
        local result=$?
        set -e
        printf '%s\n' "$result" > "$direct/$name-exit-code.txt"
        if (( result != 0 )); then cat "$direct/$name.log" >&2; exit "$result"; fi
    }
    run_timed extract python3 "$repo/research/challenge-8/extract-verifast-drop.py" \
        --source "$repo/library/core/src/slice/sort/shared/smallsort.rs" \
        --output "$direct/crate" --evidence "$direct/crate/extraction.json"
    direct_crate="$direct/crate"
    jq -e '.exact_destination_values == true and .generic_T == true and .arbitrary_len == true and
        .body_source_unchanged == true and .ghost_strip_exact_bytes == true and .block_bytes == 364 and
        .block_sha256 == "caff1edbfa3a8d9fd29459e49c43abd0f8f987f9061c75e7bf6ecedbbba26a6a" and
        .source_sha256 == "32574fd06623190132f213cbfeaeca5bd466e3c802ca97a2174e24fd3c240959" and
        (.contract_sha256 | type == "string" and length == 64)' \
        "$direct_crate/extraction.json" > "$direct/extraction-audit.json"
    sha256sum "$direct_crate/original/lib.rs" "$direct_crate/verified/lib.rs" \
        "$direct_crate/extraction.json" > "$direct/extraction-files-sha256.txt"
    printf '%s  %s\n' "$(jq -r '.original_sha256' "$direct_crate/extraction.json")" "$direct_crate/original/lib.rs" | sha256sum -c -
    printf '%s  %s\n' "$(jq -r '.verified_sha256' "$direct_crate/extraction.json")" "$direct_crate/verified/lib.rs" | sha256sum -c -
    sha256sum "$direct_crate/original/lib.rs" "$direct_crate/verified/lib.rs" \
        "$repo/library/core/src/slice/sort/shared/smallsort.rs" > "$direct/source-before.txt"
    cd "$direct_crate"
    set +e
    env LD_LIBRARY_PATH="$compiler_libdir:$VERIFAST_HOME/bin:${LD_LIBRARY_PATH:-}" \
        /usr/bin/time -v -o "$direct/compiler-mir-resources.txt" \
        "$VERIFAST_HOME/bin/vf-rust-mir-exporter" verified/lib.rs "--sysroot=$compiler_sysroot" \
        --edition 2021 --vf-rust-mir-exporter:preprocess-readonly \
        > "$direct/compiler-mir.bin" 2> "$direct/compiler-mir.log"
    direct_export_status=$?
    printf '%s\n' "$direct_export_status" > "$direct/compiler-mir-exit-code.txt"
    if (( direct_export_status == 0 )); then
        /usr/bin/time -v -o "$direct/compiler-mir-decode-resources.txt" "$decoder" decode \
            -I /tmp/vfdeps-adf88dc/include "$schema" VfMir < "$direct/compiler-mir.bin" \
            > "$direct/compiler-mir.txt" 2> "$direct/compiler-mir-decode.log"
        direct_decode_status=$?
    else
        direct_decode_status=98
    fi
    printf '%s\n' "$direct_decode_status" > "$direct/compiler-mir-decode-exit-code.txt"
    set -e
    if (( direct_export_status != 0 || direct_decode_status != 0 )); then
        cat "$direct/compiler-mir.log" "$direct/compiler-mir-decode.log" >&2
        exit 1
    fi
    expected_drop='<CopyOnDrop<T> as core::ops::Drop>::drop'
    [[ $(grep -F -c "defPath = \"$expected_drop\"" "$direct/compiler-mir.txt" || true) == 1 ]]
    [[ $(grep -F -c 'copy_nonoverlapping' "$direct/compiler-mir.txt" || true) -ge 1 ]]
    jq -e --arg target "$expected_drop" '.expected_target_name == $target and .target_copy_call_line > 0' \
        extraction.json > "$direct/target-audit.json"
    set +e
    /usr/bin/time -v -o "$direct/verifast-resources.txt" \
        "$VERIFAST_HOME/bin/verifast" -rustc_args '--edition 2021' "${vf_options[@]}" \
        -skip_specless_fns verified/lib.rs > "$direct/verifast.log" 2>&1
    direct_vf=$?
    /usr/bin/time -v -o "$direct/refinement-resources.txt" \
        "$VERIFAST_HOME/bin/refinement-checker" --rustc-args '--edition 2021' \
        original/lib.rs verified/lib.rs > "$direct/refinement.log" 2>&1
    direct_refinement=$?
    set -e
    printf '%s\n' "$direct_vf" > "$direct/verifast-exit-code.txt"
    printf '%s\n' "$direct_refinement" > "$direct/refinement-exit-code.txt"
    sha256sum "$direct_crate/original/lib.rs" "$direct_crate/verified/lib.rs" \
        "$repo/library/core/src/slice/sort/shared/smallsort.rs" > "$direct/source-after.txt"
    cmp "$direct/source-before.txt" "$direct/source-after.txt"
    copy_line=$(jq -r '.target_copy_call_line' extraction.json)
    core_target_count=$(count_verified_header "$expected_drop" "$direct/verifast.log")
    std_target="${expected_drop/core::ops::Drop/std::ops::Drop}"
    std_target_count=$(count_verified_header "$std_target" "$direct/verifast.log")
    copy_call_count=$(grep -E -c "verified/lib[.]rs\\(${copy_line},[0-9]+(-[0-9]+(,[0-9]+)?)?\\): Verifying call$" "$direct/verifast.log" || true)
    copy_statement_count=$(grep -E -c "verified/lib[.]rs\\(${copy_line},[0-9]+(-[0-9]+(,[0-9]+)?)?\\): (note: )?Executing statement$" "$direct/verifast.log" || true)
    printf '%s\n' "$core_target_count" > "$direct/target-core-count.txt"
    printf '%s\n' "$std_target_count" > "$direct/target-std-count.txt"
    printf '%s\n' "$copy_call_count" > "$direct/copy-call-count.txt"
    printf '%s\n' "$copy_statement_count" > "$direct/copy-statement-count.txt"
    [[ $direct_vf == 0 && $direct_refinement == 0 && $((core_target_count + std_target_count)) == 1 &&
        $copy_call_count == 1 && $copy_statement_count -ge 1 ]] || {
        cat "$direct/verifast.log" "$direct/refinement.log" >&2
        echo 'Exact actual Drop body gate failed before caller experiments' >&2
        exit 1
    }
    cd "$repo"

    caller_evidence="$evidence/callers/extraction.json"
    /usr/bin/time -v -o "$evidence/caller-extraction-resources.txt" \
        python3 "$repo/research/challenge-8/extract-verifast-drop-caller.py" \
        --source "$repo/library/core/src/slice/sort/shared/smallsort.rs" \
        --fixture "$repo/research/challenge-8/verifast-drop-caller-cases.rs" \
        --direct-extractor "$repo/research/challenge-8/extract-verifast-drop.py" \
        --output "$evidence/callers" --evidence "$caller_evidence" \
        > "$evidence/caller-extraction.log" 2>&1
    jq -e '.selection == "verifast_local_drop_caller_gate" and .all_ghost_strip_audits_exact == true and
        .source_sha256 == "32574fd06623190132f213cbfeaeca5bd466e3c802ca97a2174e24fd3c240959" and
        .direct_drop_block_bytes == 364 and .direct_drop_block_sha256 == "caff1edbfa3a8d9fd29459e49c43abd0f8f987f9061c75e7bf6ecedbbba26a6a" and
        (.cases | length == 9)' "$caller_evidence" > "$evidence/caller-extraction-audit.json"
    [[ $(jq -r '.direct_drop_contract_sha256' "$caller_evidence") == \
        $(jq -r '.contract_sha256' "$direct_crate/extraction.json") ]]

    case_names=(cleanup_one cleanup_callback negative_missing_source negative_missing_destination \
        negative_missing_own negative_unannotated_drop negative_broken_drop_post \
        unsupported_extra_field unsupported_copy_bound)
    for case_name in "${case_names[@]}"; do
        case_dir="$evidence/callers/$case_name"
        case_evidence="$case_dir/case.json"
        expected=$(jq -r --arg name "$case_name" '.cases[$name].expected' "$caller_evidence")
        copy_line=$(jq -r --arg name "$case_name" '.cases[$name].target_copy_call_line' "$caller_evidence")
        caller_line=$(jq -r --arg name "$case_name" '(.cases[$name].caller_record_line // 0)' "$caller_evidence")
        caller_drop_line=$(jq -r --arg name "$case_name" '(.cases[$name].caller_drop_line // 0)' "$caller_evidence")
        [[ -s "$case_dir/original/lib.rs" && -s "$case_dir/verified/lib.rs" &&
            $(jq -r --arg name "$case_name" '.cases[$name].ghost_strip_exact_bytes' "$caller_evidence") == true ]]
        printf '%s  %s\n' "$(jq -r --arg name "$case_name" '.cases[$name].original_sha256' "$caller_evidence")" \
            "$case_dir/original/lib.rs" | sha256sum -c -
        printf '%s  %s\n' "$(jq -r --arg name "$case_name" '.cases[$name].verified_sha256' "$caller_evidence")" \
            "$case_dir/verified/lib.rs" | sha256sum -c -
        sha256sum "$case_dir/original/lib.rs" "$case_dir/verified/lib.rs" > "$case_dir/source-before.txt"
        cd "$case_dir"
        set +e
        /usr/bin/time -v -o compiler-mir-resources.txt \
            env LD_LIBRARY_PATH="$compiler_libdir:$VERIFAST_HOME/bin:${LD_LIBRARY_PATH:-}" \
            "$VERIFAST_HOME/bin/vf-rust-mir-exporter" verified/lib.rs "--sysroot=$compiler_sysroot" \
            --edition 2021 --vf-rust-mir-exporter:preprocess-readonly > compiler-mir.bin 2> compiler-mir.log
        export_status=$?
        printf '%s\n' "$export_status" > compiler-mir-exit-code.txt
        if (( export_status == 0 )); then
            set +e
            /usr/bin/time -v -o compiler-mir-decode-resources.txt "$decoder" decode \
                -I /tmp/vfdeps-adf88dc/include "$schema" VfMir < compiler-mir.bin > compiler-mir.txt 2> compiler-mir-decode.log
            decode_status=$?
            set -e
        else
            decode_status=98
        fi
        printf '%s\n' "$decode_status" > compiler-mir-decode-exit-code.txt
        set -e
        if (( export_status != 0 || decode_status != 0 )); then
            echo "Rust export/decode must succeed before intended $expected classification: $case_name" >&2
            cat compiler-mir.log compiler-mir-decode.log >&2
            exit 1
        fi
        [[ $(grep -F -c "defPath = \"$expected_drop\"" compiler-mir.txt || true) == 1 ]]
        [[ $(grep -F -c 'copy_nonoverlapping' compiler-mir.txt || true) -ge 1 ]]
        set +e
        /usr/bin/time -v -o verifast-resources.txt \
            "$VERIFAST_HOME/bin/verifast" -rustc_args '--edition 2021' "${vf_options[@]}" \
            -skip_specless_fns verified/lib.rs > verifast.log 2>&1
        vf_status=$?
        printf '%s\n' "$vf_status" > verifast-exit-code.txt
        if [[ "$expected" == pass ]]; then
            /usr/bin/time -v -o refinement-resources.txt \
                "$VERIFAST_HOME/bin/refinement-checker" --rustc-args '--edition 2021' \
                original/lib.rs verified/lib.rs > refinement.log 2>&1
            refinement_status=$?
        else
            refinement_status=99
        fi
        set -e
        printf '%s\n' "$refinement_status" > refinement-exit-code.txt
        sha256sum "$case_dir/original/lib.rs" "$case_dir/verified/lib.rs" > source-after.txt
        cmp source-before.txt source-after.txt

        core_target_count=$(count_verified_header "$expected_drop" verifast.log)
        std_target="${expected_drop/core::ops::Drop/std::ops::Drop}"
        std_target_count=$(count_verified_header "$std_target" verifast.log)
        target_count=$((core_target_count + std_target_count))
        copy_call_count=$(grep -E -c "verified/lib[.]rs\\(${copy_line},[0-9]+(-[0-9]+(,[0-9]+)?)?\\): Verifying call$" verifast.log || true)
        copy_statement_count=$(grep -E -c "verified/lib[.]rs\\(${copy_line},[0-9]+(-[0-9]+(,[0-9]+)?)?\\): (note: )?Executing statement$" verifast.log || true)
        caller_record_count=$(grep -E -c "verified/lib[.]rs\\(${caller_line},[0-9]+(-[0-9]+(,[0-9]+)?)?\\): (Verifying call|(note: )?Executing statement)$" verifast.log || true)
        caller_drop_call_count=$(grep -E -c "verified/lib[.]rs\\(${caller_drop_line},[0-9]+(-[0-9]+(,[0-9]+)?)?\\): Verifying call$" verifast.log || true)
        rg -n -i 'error:' verifast.log > verifier-error-lines.txt || true
        if [[ "$case_name" == negative_broken_drop_post ]]; then
            caller_target_count=0
        else
            caller_target_count=$(count_verified_header "$case_name" verifast.log)
        fi
        printf '%s\n' "$core_target_count" > target-core-count.txt
        printf '%s\n' "$std_target_count" > target-std-count.txt
        printf '%s\n' "$target_count" > target-count.txt
        printf '%s\n' "$copy_call_count" > copy-call-count.txt
        printf '%s\n' "$copy_statement_count" > copy-statement-count.txt
        printf '%s\n' "$caller_record_count" > caller-record-count.txt
        printf '%s\n' "$caller_drop_line" > caller-drop-source-line.txt
        printf '%s\n' "$caller_drop_call_count" > caller-drop-call-record-count.txt
        jq -n --arg case "$case_name" --arg expected "$expected" --argjson export "$export_status" \
            --argjson decode "$decode_status" --argjson vf "$vf_status" --argjson refinement "$refinement_status" \
            --argjson target "$target_count" --argjson copy_calls "$copy_call_count" \
            --argjson copy_statements "$copy_statement_count" --argjson caller_records "$caller_record_count" \
            --argjson caller_target "$caller_target_count" \
            --argjson caller_drop_calls "$caller_drop_call_count" \
            '{case:$case,expected:$expected,export_status:$export,decode_status:$decode,
              verifast_status:$vf,refinement_status:$refinement,target_count:$target,
              copy_call_records:$copy_calls,copy_statement_records:$copy_statements,
              caller_records:$caller_records,caller_target_count:$caller_target,
              caller_drop_call_records:$caller_drop_calls}' > case.json

        case "$expected" in
            pass)
                if (( vf_status != 0 || refinement_status != 0 || target_count != 1 ||
                    copy_call_count != 1 || copy_statement_count < 1 || caller_target_count != 1 ||
                    caller_drop_call_count < 1 )); then
                    cat verifast.log refinement.log >&2
                    echo "Positive local Drop caller proof failed: $case_name" >&2
                    exit 1
                fi
                if [[ "$case_name" == cleanup_callback ]] && (( caller_drop_call_count < 2 )); then
                    echo 'FnMut normal and cleanup local-Drop call records were not both observed' >&2
                    exit 1
                fi
                ;;
            fail)
                case "$case_name" in
                    negative_missing_source) diagnostic_pattern='(?i)error: No matching heap chunks: .*(array|points_to|pointsto).*(src)|error: No matching heap chunks: .*src.*(array|points_to|pointsto)' ;;
                    negative_missing_destination) diagnostic_pattern='(?i)error: No matching heap chunks: .*(array|points_to|pointsto).*(dst)|error: No matching heap chunks: .*dst.*(array|points_to|pointsto)' ;;
                    negative_missing_own) diagnostic_pattern='(?i)error: No matching heap chunks: .*foreach' ;;
                    *) diagnostic_pattern='(?i)error:' ;;
                esac
                if (( vf_status == 0 || target_count != 1 || caller_target_count != 1 )) ||
                    ! rg -q "$diagnostic_pattern" verifier-error-lines.txt ||
                    { [[ "$case_name" == negative_missing_own ]] &&
                        rg -qi 'error: No matching heap chunks: .*CopyOnDrop.*own' verifier-error-lines.txt; }; then
                    cat verifast.log >&2
                    echo "Expected caller resource rejection was not classified at its caller: $case_name" >&2
                    exit 1
                fi
                ;;
            generic_reject)
                if (( vf_status == 0 || caller_target_count != 1 || target_count != 0 ||
                    copy_call_count != 0 )) ||
                    ! rg -qi 'error:.*CopyOnDrop.*own|error:.*own.*CopyOnDrop' verifier-error-lines.txt; then
                    cat verifast.log >&2
                    echo 'Unannotated Drop baseline did not retain its generic Own failure' >&2
                    exit 1
                fi
                ;;
            actual_drop_body_failure)
                if (( vf_status == 0 || target_count != 1 || caller_target_count != 0 ||
                    copy_call_count < 1 || copy_statement_count < 1 )) ||
                    ! rg -qi 'error:.*(postcondition|ensures|ens clause|actual_values|src_values)' verifier-error-lines.txt; then
                    cat verifast.log >&2
                    echo 'Broken postcondition did not fail while proving the named actual Drop body' >&2
                    exit 1
                fi
                ;;
            frontend_reject)
                if (( vf_status == 0 )) || ! rg -qi 'Local Drop call:.*(unsupported|exact local type|matching)' verifast.log; then
                    cat verifast.log >&2
                    echo "Unsupported annotated Drop shape did not fail closed at frontend: $case_name" >&2
                    exit 1
                fi
                ;;
            *) echo "Unknown case classification: $expected" >&2; exit 2 ;;
        esac

        if [[ "$case_name" == cleanup_callback ]]; then
            callback_call_line=$(jq -r '.cases.cleanup_callback.callback_call_line' "$caller_evidence")
            [[ "$callback_call_line" =~ ^[1-9][0-9]*$ ]]
            callback_call_count=$(grep -E -c "verified/lib[.]rs\\(${callback_call_line},[0-9]+(-[0-9]+(,[0-9]+)?)?\\): Verifying call$" verifast.log || true)
            awk -v function_name='cleanup_callback' '
                index($0, "defPath = ") && index($0, function_name) { active=1; start=NR }
                active && NR > start && index($0, "defPath = ") { exit }
                active { print }
            ' compiler-mir.txt > callback-mir-function.txt
            callback_mir_function_count=$(grep -F -c 'cleanup_callback' callback-mir-function.txt || true)
            callback_mir_fnmut_call_count=$(grep -E -ci '(FnMut|call_mut)' callback-mir-function.txt || true)
            callback_mir_unwind_count=$(grep -F -c 'unwindResume = void' callback-mir-function.txt || true)
            callback_mir_drop_count=$(grep -F -c 'drop = (' callback-mir-function.txt || true)
            callback_mir_cleanup_count=$(grep -F -c 'isCleanup = true' callback-mir-function.txt || true)
            callback_mir_guard_type_count=$(grep -F -c 'CopyOnDrop' callback-mir-function.txt || true)
            printf '%s\n' "$callback_call_line" > callback-source-line.txt
            printf '%s\n' "$callback_call_count" > callback-call-record-count.txt
            printf '%s\n' "$callback_mir_function_count" > callback-mir-function-count.txt
            printf '%s\n' "$callback_mir_fnmut_call_count" > callback-mir-fnmut-call-count.txt
            printf '%s\n' "$callback_mir_unwind_count" > callback-mir-unwind-count.txt
            printf '%s\n' "$callback_mir_drop_count" > callback-mir-drop-count.txt
            printf '%s\n' "$callback_mir_cleanup_count" > callback-mir-cleanup-count.txt
            printf '%s\n' "$callback_mir_guard_type_count" > callback-mir-guard-type-count.txt
            rg -n -C 4 'cleanup_callback|unwindResume = void|drop = \(|isCleanup = true|CopyOnDrop' \
                callback-mir-function.txt > callback-mir-cleanup-evidence.txt
            [[ $callback_call_count == 1 && $callback_mir_function_count -ge 1 &&
                $callback_mir_fnmut_call_count -ge 1 &&
                $callback_mir_unwind_count -ge 1 && $callback_mir_drop_count -ge 2 &&
                $callback_mir_cleanup_count -ge 1 && $caller_drop_call_count -ge 2 &&
                $callback_mir_guard_type_count -ge 1 ]]
        fi
        cd "$repo"
    done
    exit 0
fi

budget=${1:-90}
case "$budget" in 30|60|90|120) ;; *) echo 'Budget must be 30, 60, 90 or 120 minutes' >&2; exit 2 ;; esac
[[ ! -e "$evidence" ]] || { echo 'Refusing to reuse local Drop caller evidence directory' >&2; exit 2; }
mkdir -p "$evidence"
{
    printf 'Source commit: '
    git rev-parse HEAD
    printf 'Selection: %s\nTotal budget including setup: %s minutes\n' \
        "${PROOF_SELECTION:-verifast_local_drop_caller_gate}" "$budget"
    printf 'Verifier pin: %s (%s)\nRust toolchain: %s\n' "$VFVERSION" "$VFPLATFORM" "$RUSTUP_TOOLCHAIN"
    printf 'Hosted runner: %s / %s\n' "$RUNNER_ENVIRONMENT" "$RUNNER_OS"
    uname -a
    sha256sum research/challenge-8/build-verifast-tuple-parser.sh \
        research/challenge-8/run-verifast-drop-caller-gate.sh \
        research/challenge-8/extract-verifast-drop-caller.py \
        research/challenge-8/extract-verifast-drop.py \
        research/challenge-8/verifast-drop-caller-cases.rs \
        research/challenge-8/verifast-local-drop-call.patch \
        research/challenge-8/verifast-manually-drop-ref.patch \
        research/challenge-8/verifast-address-taken.patch
    printf 'Pinned SmallSort source SHA-256: 32574fd06623190132f213cbfeaeca5bd466e3c802ca97a2174e24fd3c240959\n'
    printf 'Local Drop translator input: f8751fab591ed98daebf446eb34800e892e72a838c7c083f643bd4efabbb0432\n'
    printf 'Local Drop patch SHA-256: f8f259e944478c5d23829a2d294def4c79087fb6886df559d9e91ed4146a8739\n'
    printf 'Local Drop translator output: 910a2b79a0761e359a76ac0502251cacc5183b075c556078018be3590ea679b5\n'
} > "$evidence/selection.txt"

set +e
/usr/bin/time -v -o "$evidence/resources.txt" \
    timeout --signal=TERM --kill-after=30s "${budget}m" \
    bash "$repo/research/challenge-8/run-verifast-drop-caller-gate.sh" --stages \
    2>&1 | tee "$evidence/execution.log"
status=${PIPESTATUS[0]}
set -e
printf '%s\n' "$status" > "$evidence/exit-code.txt"
if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
    {
        printf '### SmallSort local Drop caller gate\n\n'
        printf 'Selection: `verifast_local_drop_caller_gate`\n\n'
        printf 'Exit code: `%s` (124 means total setup/proof timeout).\n' "$status"
    } >> "$GITHUB_STEP_SUMMARY"
fi
exit "$status"
