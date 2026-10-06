#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0 OR MIT
# GitHub-hosted Actions only. Never install or run VeriFast on the editing server.
set -euo pipefail

if [[ "${GITHUB_ACTIONS:-}" != true || "${RUNNER_ENVIRONMENT:-}" != github-hosted || "${RUNNER_OS:-}" != Linux ]]; then
    echo 'This VeriFast experiment runs only on a GitHub-hosted Linux Actions runner' >&2
    exit 2
fi

repo=$(git rev-parse --show-toplevel)
cd "$repo"
evidence="$repo/research-results/verifast-swap-size"
budget=${1:-90}
case "$budget" in
    30|60|90|120) ;;
    *) echo 'Budget must be 30, 60, 90 or 120 minutes' >&2; exit 2 ;;
esac
export VFVERSION=26.09
export VFPLATFORM=linux
export RUSTUP_TOOLCHAIN=nightly-2026-02-05
selection=${PROOF_SELECTION:-verifast_swap_size}

if [[ "${2:-}" != --inside ]]; then
    mkdir -p "$evidence"
    if [[ -e "$evidence/exit-code.txt" ]]; then
        echo "refusing to overwrite prior evidence: $evidence" >&2
        exit 2
    fi
    set +e
    /usr/bin/time -v -o "$evidence/resources.txt" \
        timeout --signal=TERM --kill-after=30s "${budget}m" \
        bash "$repo/research/challenge-8/run-verifast-swap-size.sh" "$budget" --inside \
        2>&1 | tee "$evidence/execution.log"
    status=${PIPESTATUS[0]}
    set -e
    printf '%s\n' "$status" > "$evidence/exit-code.txt"
    if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
        {
            printf '### Generic SmallSort size helper VeriFast experiment\n\n'
            printf 'Selection: `%s`; specified target bodies: one.\n\n' "$selection"
            printf 'Exit code: `%s` (124 indicates timeout). This experiment covers only the pure size helper.\n' "$status"
        } >> "$GITHUB_STEP_SUMMARY"
    fi
    exit "$status"
fi

mkdir -p "$evidence"
{
    printf 'Source commit: '
    git rev-parse HEAD
    printf 'Selection: %s\nBudget including extraction and tool setup: %s minutes\n' "$selection" "$budget"
    printf 'VeriFast pin: %s (%s)\nRust toolchain: %s\n' "$VFVERSION" "$VFPLATFORM" "$RUSTUP_TOOLCHAIN"
    printf 'Expected specified target bodies: 1 (has_efficient_in_place_swap<T>)\n'
    printf 'Contract: req true; ens result == (std::mem::size_of::<T>() <= 8); unrestricted generic T\n'
    printf 'Runner: %s / %s\n' "$RUNNER_ENVIRONMENT" "$RUNNER_OS"
    uname -a
    sha256sum library/core/src/slice/sort/shared/smallsort.rs \
        research/challenge-8/extract-verifast-swap-size.py \
        research/challenge-8/run-verifast-swap-size.sh \
        verifast-proofs/setup-verifast-home
} > "$evidence/environment.txt"

set +e
python3 research/challenge-8/extract-verifast-swap-size.py "$evidence" \
    > "$evidence/extraction.log" 2>&1
extract_status=$?
set -e
printf '%s\n' "$extract_status" > "$evidence/extraction-exit-code.txt"
if (( extract_status != 0 )); then
    cat "$evidence/extraction.log" >&2
    exit "$extract_status"
fi

set +e
(
    cd "$evidence"
    . "$repo/verifast-proofs/setup-verifast-home"
    {
        printf 'Pinned runtime details:\n'
        rustc --version --verbose
        if [[ -f "$VERIFAST_HOME/bin/VERSION" ]]; then
            cat "$VERIFAST_HOME/bin/VERSION"
        fi
        sha256sum "$VERIFAST_HOME/bin/verifast" "$VERIFAST_HOME/bin/refinement-checker"
    } >> environment.txt 2>&1

    set +e
    /usr/bin/time -v -o verifast-resources.txt "$VERIFAST_HOME/bin/verifast" \
        -rustc_args '--edition 2021' -skip_specless_fns -verbose 1 verified/lib.rs > verifast.log 2>&1
    vf_status=$?
    /usr/bin/time -v -o refinement-resources.txt "$VERIFAST_HOME/bin/refinement-checker" \
        --rustc-args '--edition 2021' original/lib.rs verified/lib.rs > refinement.log 2>&1
    refinement_status=$?
    set -e
    printf '%s\n' "$vf_status" > verifast-exit-code.txt
    printf '%s\n' "$refinement_status" > refinement-exit-code.txt
    target_count=$(grep -F -c "Verifying function 'smallsort::has_efficient_in_place_swap'" verifast.log || true)
    target_lines=$(python3 -c 'import json; print("|".join(map(str, json.load(open("extraction.json"))["target_statement_lines"])))')
    statement_count=$(grep -E -c "^.*verified/smallsort[.]rs\\(($target_lines),[0-9]+(-[0-9]+(,[0-9]+)?)?\\): (note: )?Executing (statement|return statement)$" verifast.log || true)
    printf '%s\n' "$target_count" > verified-target-count.txt
    printf '%s\n' "$statement_count" > verified-target-statement-count.txt
    cat verifast.log refinement.log
    if (( vf_status != 0 || refinement_status != 0 || target_count != 1 || statement_count < 1 )); then
        printf 'verification rejected: verifier=%s refinement=%s exact_target_count=%s target_statement_count=%s\n' \
            "$vf_status" "$refinement_status" "$target_count" "$statement_count" >&2
        exit 1
    fi
) > "$evidence/stages.log" 2>&1
stages_status=$?
set -e
printf '%s\n' "$stages_status" > "$evidence/stages-exit-code.txt"
cat "$evidence/stages.log"
exit "$stages_status"
