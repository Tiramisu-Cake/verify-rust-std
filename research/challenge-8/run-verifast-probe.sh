#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0 OR MIT
# GitHub-hosted Actions only: installing or executing VeriFast locally is forbidden.
set -euo pipefail

if [[ "${GITHUB_ACTIONS:-}" != true || "${RUNNER_ENVIRONMENT:-}" != github-hosted || "${RUNNER_OS:-}" != Linux ]]; then
    echo 'This probe runs only on a GitHub-hosted Linux Actions runner' >&2
    exit 2
fi

repo=$(git rev-parse --show-toplevel)
cd "$repo"
evidence="$repo/research-results/verifast-probe"
export VFVERSION=26.09
export VFPLATFORM=linux
export RUSTUP_TOOLCHAIN=nightly-2026-02-05
export VF_PROBE_PROFILE=${VF_PROBE_PROFILE:-frontend}

if [[ "${1:-}" == --stages ]]; then
    cd "$evidence"
    # The repository's pinned setup installs only on this hosted runner.
    . "$repo/verifast-proofs/setup-verifast-home"
    printf 'VeriFast pin: %s\nRust toolchain: %s\n' "$VFVERSION" "$RUSTUP_TOOLCHAIN"
    {
        printf '\nInstalled tool versions and binary hashes:\n'
        rustc --version --verbose
        if [[ -f "$VERIFAST_HOME/bin/VERSION" ]]; then
            printf 'VeriFast release VERSION file:\n'
            cat "$VERIFAST_HOME/bin/VERSION"
        else
            printf 'VeriFast VERSION file absent; release pin and binary hash below identify this binary.\n'
        fi
        sha256sum "$VERIFAST_HOME/bin/verifast" "$VERIFAST_HOME/bin/refinement-checker"
        printf 'Bundled prelude before any overlay:\n'
        sha256sum "$VERIFAST_HOME/bin/rust/prelude.rsspec"
    } >> "$evidence/environment.txt" 2>&1

    vf_options=()
    if [[ "$VF_PROBE_PROFILE" == tuple_overlay ]]; then
        python3 "$repo/research/challenge-8/patch-verifast-tuple-model.py" \
            "$VERIFAST_HOME/bin/rust/prelude.rsspec" "$evidence" \
            2>&1 | tee "$evidence/model-overlay.log"
        vf_options=(-verbose 1)
        {
            printf 'Bundled prelude after tuple-2 overlay:\n'
            sha256sum "$VERIFAST_HOME/bin/rust/prelude.rsspec"
            printf 'Verifier binary hashes after spec overlay:\n'
            sha256sum "$VERIFAST_HOME/bin/verifast" "$VERIFAST_HOME/bin/refinement-checker"
        } >> "$evidence/environment.txt"
    fi

    printf 'Probe profile: %s\n' "$VF_PROBE_PROFILE"
    # Only insert_tail is specified. An exit 0 must be inspected for function
    # counts; it is not evidence for CopyOnDrop or the outer function.
    set +e
    /usr/bin/time -v -o verifast-resources.txt "$VERIFAST_HOME/bin/verifast" -rustc_args '--edition 2021' \
        "${vf_options[@]}" -skip_specless_fns verified/lib.rs > verifast.log 2>&1
    vf_status=$?
    /usr/bin/time -v -o refinement-resources.txt "$VERIFAST_HOME/bin/refinement-checker" --rustc-args '--edition 2021' \
        original/lib.rs verified/lib.rs > refinement.log 2>&1
    refinement_status=$?
    set -e
    printf '%s\n' "$vf_status" > verifast-exit-code.txt
    printf '%s\n' "$refinement_status" > refinement-exit-code.txt
    cat verifast.log refinement.log
    if (( vf_status != 0 || refinement_status != 0 )); then
        exit 1
    fi
    exit 0
fi

budget=${1:-90}
case "$budget" in
    30|60|90|120) ;;
    *) echo 'Budget must be 30, 60, 90 or 120 minutes' >&2; exit 2 ;;
esac
profile=${2:-frontend}
case "$profile" in
    frontend|range|tuple_overlay) ;;
    *) echo 'Profile must be frontend, range or tuple_overlay' >&2; exit 2 ;;
esac
export VF_PROBE_PROFILE="$profile"
mkdir -p "$evidence"
{
    printf 'Source commit: '
    git rev-parse HEAD
    printf 'Selection: %s\nProfile: %s\nBudget including setup: %s minutes\n' "${PROOF_SELECTION:-verifast_insert_tail_probe}" "$profile" "$budget"
    printf 'VeriFast pin: %s (%s)\nRust toolchain: %s\n' "$VFVERSION" "$VFPLATFORM" "$RUSTUP_TOOLCHAIN"
    printf 'Expected specified target bodies: 1 (insert_tail); an exit 0 needs statement/function count inspection.\n'
    printf 'Runner: %s / %s\n' "$RUNNER_ENVIRONMENT" "$RUNNER_OS"
    uname -a
    sha256sum library/core/src/slice/sort/shared/smallsort.rs \
        research/challenge-8/extract-verifast-insertion.py \
        research/challenge-8/patch-verifast-tuple-model.py \
        research/challenge-8/run-verifast-probe.sh \
        verifast-proofs/setup-verifast-home
} > "$evidence/environment.txt"

# This writes exact selected source chunks, both versions, and per-chunk hashes.
set +e
python3 research/challenge-8/extract-verifast-insertion.py "$evidence" --profile "$profile" \
    > "$evidence/extraction.log" 2>&1
extraction_status=$?
set -e
if (( extraction_status != 0 )); then
    cat "$evidence/extraction.log" >&2
    printf '%s\n' "$extraction_status" > "$evidence/exit-code.txt"
    exit "$extraction_status"
fi

set +e
/usr/bin/time -v -o "$evidence/resources.txt" \
    timeout --signal=TERM --kill-after=30s "${budget}m" \
    bash research/challenge-8/run-verifast-probe.sh --stages \
    2>&1 | tee "$evidence/execution.log"
status=${PIPESTATUS[0]}
set -e
printf '%s\n' "$status" > "$evidence/exit-code.txt"
if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
    {
        printf '### SmallSort VeriFast insertion probe\n\n'
        printf 'Profile: `%s`.\n\n' "$profile"
        printf 'Actual source: `insert_tail` only specified; CopyOnDrop and outer function are extracted but unspecified.\n\n'
        printf 'Exit code: `%s` (124 means timeout). Inspect logs and verified function count before any proof claim.\n' "$status"
    } >> "$GITHUB_STEP_SUMMARY"
fi
exit "$status"
