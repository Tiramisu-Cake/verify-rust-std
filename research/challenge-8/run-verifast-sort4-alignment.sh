#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0 OR MIT
# Hosted-only, unchanged VeriFast alignment geometry gate for sort4.
set -euo pipefail

if [[ "${GITHUB_ACTIONS:-}" != true || "${RUNNER_ENVIRONMENT:-}" != github-hosted || "${RUNNER_OS:-}" != Linux ]]; then
    echo 'sort4 alignment gate requires a GitHub-hosted Linux Actions runner' >&2
    exit 2
fi

repo=$(git rev-parse --show-toplevel)
cd "$repo"
evidence="$repo/research-results/verifast-sort4-alignment"
requested_budget=${1:-90}
[[ "$requested_budget" == 30 || "$requested_budget" == 90 ]] || { echo 'H_align allocation must be 30 or historical 90 minutes' >&2; exit 2; }
budget=$requested_budget
budget_seconds=$((budget * 60))
if [[ -n "${H_ALIGN_JOB_STARTED_EPOCH:-}" ]]; then
    [[ "$H_ALIGN_JOB_STARTED_EPOCH" =~ ^[0-9]+$ ]] || { echo 'invalid H_ALIGN_JOB_STARTED_EPOCH' >&2; exit 2; }
    now_epoch=$(date +%s)
    remaining=$((budget_seconds - now_epoch + H_ALIGN_JOB_STARTED_EPOCH))
    (( remaining > 0 )) || { echo 'H_align allocated job budget is already exhausted' >&2; exit 124; }
    budget_seconds=$remaining
fi
export VFVERSION=26.09 VFPLATFORM=linux RUSTUP_TOOLCHAIN=nightly-2026-02-05

if [[ "${2:-}" != --inside ]]; then
    [[ ! -e "$evidence" ]] || { echo "refusing to reuse prior evidence directory: $evidence" >&2; exit 2; }
    mkdir -p "$evidence"
    set +e
    /usr/bin/time -v -o "$evidence/resources.txt" \
        timeout --signal=TERM --kill-after=30s "${budget_seconds}s" \
        bash "$repo/research/challenge-8/run-verifast-sort4-alignment.sh" "$budget" --inside \
        2>&1 | tee "$evidence/execution.log"
    status=${PIPESTATUS[0]}
    set -e
    printf '%s\n' "$status" > "$evidence/exit-code.txt"
    if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
        printf '### VeriFast sort4 alignment geometry gate\n\nHosted allocated-budget gate exit: `%s`.\n' \
            "$status" >> "$GITHUB_STEP_SUMMARY"
    fi
    exit "$status"
fi
[[ -d "$evidence" ]] || { echo 'inside mode requires wrapper-created evidence directory' >&2; exit 2; }

fixture="$repo/research/challenge-8/verifast-sort4-alignment-cases.rs"
runner="$repo/research/challenge-8/run-verifast-sort4-alignment.sh"
driver="$repo/research/challenge-8/prepare-and-check-sort4-alignment.py"
[[ -f "$fixture" && -f "$driver" ]] || { echo 'alignment fixture or driver is missing' >&2; exit 2; }
{
    printf 'Source commit: '; git rev-parse HEAD
    printf 'Budget including setup and all cases: %s minutes\n' "$budget"
    printf 'VeriFast pin: %s (%s)\nRust toolchain: %s\n' "$VFVERSION" "$VFPLATFORM" "$RUSTUP_TOOLCHAIN"
    printf 'Hosted runner: %s / %s\n' "$RUNNER_ENVIRONMENT" "$RUNNER_OS"
    uname -a
    sha256sum "$fixture" "$runner" "$driver" verifast-proofs/setup-verifast-home
} > "$evidence/environment.txt"

# Install the pinned official release archive in an isolated runner-temp area.
# Verify its published digest before extraction so a pre-existing cache cannot
# substitute a different verifier binary.
vf_temp="$RUNNER_TEMP/verifast-sort4-alignment"
[[ ! -e "$vf_temp" ]] || { echo "refusing to reuse prior temporary install directory: $vf_temp" >&2; exit 2; }
mkdir -p "$vf_temp/downloads"
archive="$vf_temp/downloads/verifast-$VFVERSION-$VFPLATFORM.tar.gz"
curl --fail --silent --show-error --location \
    "https://github.com/verifast/verifast/releases/download/$VFVERSION/verifast-$VFVERSION-$VFPLATFORM.tar.gz" \
    --output "$archive"
printf 'Official VeriFast archive SHA-256:\n' >> "$evidence/environment.txt"
sha256sum "$archive" >> "$evidence/environment.txt"
printf 'Expected official archive SHA-256: da1b619fa63ba73c12ce591638ced90fd2471add6f181d0e3310657fe4df98aa\n' >> "$evidence/environment.txt"
printf '%s  %s\n' da1b619fa63ba73c12ce591638ced90fd2471add6f181d0e3310657fe4df98aa "$archive" | sha256sum -c -
tar -xzf "$archive" -C "$vf_temp"
tool_home="$vf_temp/verifast-$VFVERSION"
[[ -x "$tool_home/bin/verifast" ]] || { echo "official archive did not extract expected verifier: $tool_home" >&2; exit 2; }
rustup toolchain install "$RUSTUP_TOOLCHAIN"
{
    rustc --version --verbose
    printf 'Effective verifier home: %s\n' "$tool_home"
    find "$tool_home/bin/rust" -type f -name '*.rsspec' -print0 |
        sort -z | xargs -0 -r sha256sum
    sha256sum "$tool_home/bin/verifast" "$tool_home/bin/refinement-checker" \
        "$tool_home/bin/vf-rust-mir-exporter"
} >> "$evidence/environment.txt" 2>&1

vf_source_commit=809de4596839b739dd999f9e462242c835e3af46
vf_schema_sha=7f3ebce320a33bcb956d51b8387754729e6516f4d15ba8dfdc61e6e36f90dfd9
sudo apt-get update
sudo apt-get install --yes --no-install-recommends capnproto
capnp --version >> "$evidence/environment.txt"
schema="$evidence/vf_mir.capnp"
curl --fail --silent --show-error --location \
    "https://raw.githubusercontent.com/verifast/verifast/$vf_source_commit/src/rust_frontend/vf_mir/vf_mir.capnp" \
    --output "$schema"
printf '%s  %s\n' "$vf_schema_sha" "$schema" | sha256sum -c -
printf 'VeriFast source commit: %s\nSchema SHA-256: %s\n' \
    "$vf_source_commit" "$vf_schema_sha" >> "$evidence/environment.txt"
std_source=library/core/src/slice/sort/shared/smallsort.rs
expected_std_blob=e555fce440872898e47fd5114f32eb15401d07df
actual_std_blob=$(git hash-object "$std_source")
[[ "$actual_std_blob" == "$expected_std_blob" ]] || {
    printf 'SmallSort source blob mismatch: expected %s, got %s\n' \
        "$expected_std_blob" "$actual_std_blob" >&2
    exit 2
}
{
    printf 'SmallSort source path: %s\nSmallSort source blob: %s\n' "$std_source" "$actual_std_blob"
    sha256sum "$std_source"
} >> "$evidence/environment.txt"

compiler_sysroot=$(rustc --print sysroot)
export RUSTUP_TOOLCHAIN=nightly-2026-02-05
export LD_LIBRARY_PATH="$compiler_sysroot/lib:$tool_home/bin:${LD_LIBRARY_PATH:-}"
printf 'Compiler sysroot: %s\n' "$compiler_sysroot" >> "$evidence/environment.txt"
ldd "$tool_home/bin/verifast" > "$evidence/effective-verifast-ldd.txt"
python3 "$driver" \
    --fixture "$fixture" --workdir "$evidence/cases" --schema "$schema" \
    --tool-home "$tool_home" --compiler-sysroot "$compiler_sysroot" \
    --evidence "$evidence"
