#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0 OR MIT
# Frozen official VeriFast; all execution only on hosted Actions.
set -euo pipefail
[[ "${GITHUB_ACTIONS:-}" == true && "${RUNNER_ENVIRONMENT:-}" == github-hosted && "${RUNNER_OS:-}" == Linux ]] || { echo 'requires GitHub-hosted Linux' >&2; exit 2; }
repo=$(git rev-parse --show-toplevel)
cd "$repo"
budget=${1:?budget required}
component=${2:?component required}
[[ "$budget" == 30 ]] || { echo 'night run allocation is 30 minutes' >&2; exit 2; }
[[ "$component" == index || "$component" == order || "$component" == select || "$component" == range || "$component" == swo || "$component" == swo_network ]] || exit 2
evidence="$repo/research-results/verifast-sort4-$component"
if [[ "${3:-}" != --inside ]]; then
    [[ ! -e "$evidence" ]] || exit 2
    mkdir -p "$evidence"
    # Reserve hosted upload/cleanup time inside the 30-minute job cap.
    remaining=$((budget * 60 - 120))
    if [[ -n "${SORT4_JOB_STARTED_EPOCH:-}" ]]; then
        [[ "$SORT4_JOB_STARTED_EPOCH" =~ ^[0-9]+$ ]] || exit 2
        remaining=$((remaining - $(date +%s) + SORT4_JOB_STARTED_EPOCH))
    fi
    (( remaining > 0 )) || exit 124
    set +e
    /usr/bin/time -v -o "$evidence/resources.txt" timeout --signal=TERM --kill-after=30s "${remaining}s" bash "$0" "$budget" "$component" --inside 2>&1 | tee "$evidence/execution.log"
    status=${PIPESTATUS[0]}
    set -e
    printf '%s\n' "$status" > "$evidence/exit-code.txt"
    exit "$status"
fi
[[ -d "$evidence" ]] || exit 2
export VFVERSION=26.09 VFPLATFORM=linux RUSTUP_TOOLCHAIN=nightly-2026-02-05
task_temp="$RUNNER_TEMP/verifast-sort4-$component"
[[ ! -e "$task_temp" ]] || exit 2
mkdir -p "$task_temp"
archive="$task_temp/verifast-26.09-linux.tar.gz"
tool_home="$task_temp/verifast-26.09"
source_pin=809de4596839b739dd999f9e462242c835e3af46
archive_sha=da1b619fa63ba73c12ce591638ced90fd2471add6f181d0e3310657fe4df98aa
{
    printf 'Source SHA: '; git rev-parse HEAD
    printf 'Profile: official-stock-26.09\nSource pin: %s\nComponent: %s\nBudget: %s minutes\n' "$source_pin" "$component" "$budget"
    printf 'Hosted: %s/%s\nCleanup reserve: 120 seconds\nGhost fixture timeout: 300 seconds\n' "$RUNNER_ENVIRONMENT" "$RUNNER_OS"
    sha256sum "$0" research/challenge-8/check-sort4-logical.py research/challenge-8/sort4-index.gh research/challenge-8/sort4-index-lemmas.c research/challenge-8/sort4-index-negative.c
} > "$evidence/environment.txt"
curl --fail --silent --show-error --location "https://github.com/verifast/verifast/releases/download/$VFVERSION/verifast-$VFVERSION-$VFPLATFORM.tar.gz" --output "$archive"
printf '%s  %s\n' "$archive_sha" "$archive" | sha256sum -c -
tar -xzf "$archive" -C "$task_temp"
export LD_LIBRARY_PATH="$tool_home/bin:${LD_LIBRARY_PATH:-}"
{
    sha256sum "$archive" "$tool_home/bin/verifast" "$tool_home/bin/refinement-checker" "$tool_home/bin/vf-rust-mir-exporter"
    find "$tool_home/bin/rust" -type f -name '*.rsspec' -print0 | sort -z | xargs -0 -r sha256sum
} >> "$evidence/environment.txt"
if [[ "$component" != select ]]; then
    if [[ "$component" == order ]]; then
        sha256sum research/challenge-8/sort4-order-lemmas.c research/challenge-8/sort4-order-negative.c >> "$evidence/environment.txt"
        gh run download 37548475221 --repo Tiramisu-Cake/verify-rust-std --name smallsort-research-37548475221-1 --dir "$evidence/saved-index"
        python3 research/challenge-8/check-sort4-logical.py --tool-home "$tool_home" --component "$component" --evidence "$evidence/checked" --replay-index-evidence "$evidence/saved-index"
    else
        if [[ "$component" == range || "$component" == swo ]]; then
            sha256sum "research/challenge-8/sort4-$component-lemmas.c" "research/challenge-8/sort4-$component-negative.c" >> "$evidence/environment.txt"
        fi
        if [[ "$component" == swo_network ]]; then
            sha256sum research/challenge-8/sort4-order.gh research/challenge-8/sort4-swo.gh research/challenge-8/sort4-swo-composition.c research/challenge-8/sort4-swo-composition-negative.c >> "$evidence/environment.txt"
        fi
        if [[ "$component" == swo ]]; then
            sha256sum research/challenge-8/sort4-swo.gh >> "$evidence/environment.txt"
        fi
        python3 research/challenge-8/check-sort4-logical.py --tool-home "$tool_home" --component "$component" --evidence "$evidence/checked"
    fi
else
    rustup toolchain install "$RUSTUP_TOOLCHAIN"
    sudo apt-get install --yes --no-install-recommends capnproto
    schema="$evidence/vf_mir.capnp"
    curl --fail --silent --show-error --location "https://raw.githubusercontent.com/verifast/verifast/$source_pin/src/rust_frontend/vf_mir/vf_mir.capnp" --output "$schema"
    printf '%s  %s\n' 7f3ebce320a33bcb956d51b8387754729e6516f4d15ba8dfdc61e6e36f90dfd9 "$schema" | sha256sum -c -
    compiler_sysroot=$(rustc --print sysroot)
    export LD_LIBRARY_PATH="$compiler_sysroot/lib:$tool_home/bin:${LD_LIBRARY_PATH:-}"
    rustc --version --verbose >> "$evidence/environment.txt"
    sha256sum research/challenge-8/prepare-and-check-sort4-select.py library/core/src/hint.rs >> "$evidence/environment.txt"
    python3 research/challenge-8/prepare-and-check-sort4-select.py --source library/core/src/hint.rs --workdir "$evidence/cases" --schema "$schema" --tool-home "$tool_home" --compiler-sysroot "$compiler_sysroot" --evidence "$evidence/checked"
fi
