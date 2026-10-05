#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0 OR MIT
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

# Execute stages serially. A caller using a summary is never checked unless
# verification of that summary's real implementation succeeds in this run.
if [[ "${1:-}" == --stages ]]; then
    case "${2:-}" in
        insertion_contracts_4) proofs=(prove_tail_contract_4 prove_composition_4) ;;
        insertion_direct_4) proofs=(prove_direct_insertion_4) ;;
        insertion_all_4) proofs=(prove_tail_contract_4 prove_composition_4 prove_direct_insertion_4) ;;
        insertion_outer_invariant_4) proofs=(prove_outer_safety_4) ;;
        *) echo 'Invalid stage selection' >&2; exit 2 ;;
    esac
    proof_module=challenge8_insertion
    if [[ "${2:-}" == insertion_outer_invariant_4 ]]; then
        proof_module=challenge8_insertion_safety
    fi
    for proof in "${proofs[@]}"; do
        printf '\nRunning stage: %s\n' "$proof"
        bash scripts/run-kani.sh --path . --kani-args \
            --harness "slice::sort::shared::smallsort::$proof_module::$proof" \
            --exact --jobs 1 2>&1 | tee "research-results/$proof.log"
    done
    exit 0
fi

selection=${1:-insertion_all_4}
budget=${2:-90}
case "$selection" in
    insertion_contracts_4|insertion_direct_4|insertion_all_4|insertion_outer_invariant_4) ;;
    *) echo 'Invalid proof selection' >&2; exit 2 ;;
esac
case "$budget" in
    30|60|90|120) ;;
    *) echo 'Budget must be 30, 60, 90 or 120 minutes' >&2; exit 2 ;;
esac

target=library/core/src/slice/sort/shared/smallsort.rs
if rg -q 'pub mod challenge8_insertion' "$target"; then
    echo 'Insertion module already present; use a clean checkout' >&2
    exit 2
fi
proof_source=research/challenge-8/insertion-4.rs
if [[ "$selection" == insertion_outer_invariant_4 ]]; then
    proof_source=research/challenge-8/insertion-safety-4.rs
fi
mkdir -p research-results
{
    printf 'Source commit: '
    git rev-parse HEAD
    printf 'Selection: %s\nTotal budget including cold build: %s minutes\n' "$selection" "$budget"
    cat tool_config/kani-version.toml
    uname -a
    lscpu
    free -h
    df -h .
    sha256sum "$target" "$proof_source"
    if [[ "$selection" == insertion_outer_invariant_4 ]]; then
        sha256sum research/challenge-8/inject-outer-invariant.py
    fi
} > research-results/environment.txt
if [[ "$selection" == insertion_outer_invariant_4 ]]; then
    python3 research/challenge-8/inject-outer-invariant.py "$target"
fi
cat "$proof_source" >> "$target"
cp "$target" research-results/smallsort-with-insertion.rs

set +e
/usr/bin/time -v -o research-results/resources.txt \
    timeout --signal=TERM --kill-after=30s "${budget}m" \
    bash research/challenge-8/run-insertion.sh --stages "$selection" \
    2>&1 | tee research-results/verification.log
verification_status=${PIPESTATUS[0]}
set -e
printf '%s\n' "$verification_status" > research-results/exit-code.txt
if [[ -x kani_build/scripts/kani ]]; then
    kani_build/scripts/kani --version >> research-results/environment.txt 2>&1 || true
fi
if command -v cbmc >/dev/null; then
    cbmc --version >> research-results/environment.txt 2>&1 || true
fi
if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
    {
        printf '### SmallSort insertion experiment\n\n'
        printf 'Selection: `%s`\n\nExit code: `%s` (124 means timeout).\n\n' "$selection" "$verification_status"
        if [[ "$selection" == insertion_outer_invariant_4 ]]; then
            printf 'Four initialized i32 cells, arbitrary comparator decisions, actual outer loop with a pointer invariant; inner loop bounded.\n\n'
        else
            printf 'The domain is four i32 elements. Contracts are on a proof-only adapter calling the real std helper.\n\n'
        fi
        printf '```text\n'
        cat research-results/resources.txt
        printf '\n```\n'
    } >> "$GITHUB_STEP_SUMMARY"
fi
exit "$verification_status"
