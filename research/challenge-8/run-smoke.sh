#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0 OR MIT
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"
selection=${1:-all}
budget=${2:-90}
prefix=slice::sort::shared::smallsort::challenge8_bootstrap
case "$selection" in
    all) harness="$prefix" ;;
    orders_i32_pair|preserves_i32_values_for_any_decision)
        harness="$prefix::$selection" ;;
    *) echo "Unknown proof selection: $selection" >&2; exit 2 ;;
esac
case "$budget" in
    30|60|90|120) ;;
    *) echo "Budget must be 30, 60, 90 or 120 minutes" >&2; exit 2 ;;
esac

target=library/core/src/slice/sort/shared/smallsort.rs
if rg -q 'pub mod challenge8_bootstrap' "$target"; then
    echo "Bootstrap module already present; use a clean checkout" >&2
    exit 2
fi
mkdir -p research-results
{
    printf 'Source commit: '
    git rev-parse HEAD
    printf 'Proof selection: %s\nBudget including cold tool build: %s minutes\n' "$selection" "$budget"
    cat tool_config/kani-version.toml
    uname -a
    lscpu
    free -h
    df -h .
    sha256sum "$target" research/challenge-8/smoke.rs
} > research-results/environment.txt

# Add only cfg(kani) proof code in the disposable verification checkout.
# The actual swap_if_less implementation comes from this checked-out std.
cat research/challenge-8/smoke.rs >> "$target"
cp "$target" research-results/smallsort-with-smoke.rs

set +e
/usr/bin/time -v -o research-results/resources.txt \
    timeout --signal=TERM --kill-after=30s "${budget}m" \
    bash scripts/run-kani.sh --path . --kani-args \
    --harness "$harness" --jobs 1 \
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
        printf '### SmallSort bootstrap\n\n'
        printf 'Selection: `%s`\n\nExit code: `%s` (124 means timeout).\n\n' "$selection" "$verification_status"
        printf 'The budget includes a cold Kani build. This is not a complete Challenge 8 solution.\n\n'
        printf '```text\n'
        cat research-results/resources.txt
        printf '\n```\n'
    } >> "$GITHUB_STEP_SUMMARY"
fi
exit "$verification_status"
