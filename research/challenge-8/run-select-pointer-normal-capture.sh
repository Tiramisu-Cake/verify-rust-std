#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0 OR MIT
# One hosted diagnostic export of the archived S6v2 projected actual helper.
set -euo pipefail
[[ "${GITHUB_ACTIONS:-}" == true && "${RUNNER_ENVIRONMENT:-}" == github-hosted && "${RUNNER_OS:-}" == Linux ]] || { echo 'requires GitHub-hosted Linux' >&2; exit 2; }
. /etc/os-release
[[ "$ID" == ubuntu && "$VERSION_ID" == 22.04 ]] || { echo 'requires Ubuntu 22.04' >&2; exit 2; }
repo=$(git rev-parse --show-toplevel)
cd "$repo"
evidence="$repo/research-results/select-pointer"
budget=${1:?budget minutes required}
[[ "$budget" == 30 ]] || { echo 'phase allocates 30 minutes per hosted run' >&2; exit 2; }
if [[ "${2:-}" != --inside ]]; then
    [[ ! -e "$evidence" ]] || { echo 'refuse existing evidence' >&2; exit 2; }
    mkdir -p "$evidence"
    remaining=$((budget * 60 - 120))
    if [[ -n "${SORT4_CONSTRUCTOR_JOB_STARTED_EPOCH:-}" ]]; then
        [[ "$SORT4_CONSTRUCTOR_JOB_STARTED_EPOCH" =~ ^[0-9]+$ ]] || exit 2
        remaining=$((remaining - $(date +%s) + SORT4_CONSTRUCTOR_JOB_STARTED_EPOCH))
    fi
    (( remaining > 0 )) || exit 124
    set +e
    /usr/bin/time -v -o "$evidence/resources.txt" timeout --signal=TERM --kill-after=30s "${remaining}s" bash "$0" "$budget" --inside 2>&1 | tee "$evidence/execution.log"
    status=${PIPESTATUS[0]}
    set -e
    printf '%s\n' "$status" > "$evidence/exit-code.txt"
    exit "$status"
fi
[[ -d "$evidence" ]] || exit 2
run_stage() {
    local stage=$1
    shift
    set +e
    /usr/bin/time -v -o "$evidence/$stage-resources.txt" "$@" > "$evidence/$stage.log" 2>&1
    local result=$?
    set -e
    printf '%s\n' "$result" > "$evidence/$stage-exit-code.txt"
    cat "$evidence/$stage.log"
    return "$result"
}
export RUSTUP_TOOLCHAIN=nightly-2026-02-05
source_pin=809de4596839b739dd999f9e462242c835e3af46
archive_sha=da1b619fa63ba73c12ce591638ced90fd2471add6f181d0e3310657fe4df98aa
exporter_sha=2b8ebb5373d0bdd82cc163f5a298a4291b89dcdb8630a01bf74149987f2d5e0c
schema_sha=7f3ebce320a33bcb956d51b8387754729e6516f4d15ba8dfdc61e6e36f90dfd9
patch_sha=8e62e6c3044fda7533637d242fb5e8a575eac0d7600213e8e3ba00a182dc0d7c
printf '%s  %s\n' "$patch_sha" "$repo/research/challenge-8/verifast-select-pointer-drop.patch" | sha256sum -c -
task_temp="$RUNNER_TEMP/select-pointer-normal-capture"
[[ ! -e "$task_temp" ]] || exit 2
mkdir -p "$task_temp"
stock_archive="$task_temp/verifast-26.09-linux.tar.gz"
stock_home="$task_temp/verifast-26.09"
source_home="$task_temp/source"
{
    printf 'Source SHA: '; git rev-parse HEAD
    printf 'Diagnostic: stock normal MIR export only; no verifier or proof\n'
    printf 'Archived fixture: run 37645561507 / source 85ec1711700ff85c899b18b7e021f076aeddb8e6 / artifact 11493408570\n'
    printf 'Archived compact SHA256: b160edcd347c02ffafcd94ac0258e805d488bed10a500b64cd3e632b5d8d49ae\n'
    printf 'Stock release: VeriFast 26.09 / source %s / compiler %s\n' "$source_pin" "$RUSTUP_TOOLCHAIN"
    printf 'S6v2 semantic patch pinned but not applied: %s\n' "$patch_sha"
    sha256sum "$0" "$repo/research/challenge-8/capture-select-pointer-normal-mir.py"
} > "$evidence/environment.txt"
run_stage python-syntax env PYTHONPYCACHEPREFIX="$task_temp/python-cache" python3 -m py_compile research/challenge-8/capture-select-pointer-normal-mir.py
run_stage stock-download curl -fL --retry 3 -o "$stock_archive" https://github.com/verifast/verifast/releases/download/26.09/verifast-26.09-linux.tar.gz
printf '%s  %s\n' "$archive_sha" "$stock_archive" | sha256sum -c -
run_stage stock-extract tar -xzf "$stock_archive" -C "$task_temp"
printf '%s  %s\n' "$exporter_sha" "$stock_home/bin/vf-rust-mir-exporter" | sha256sum -c -
run_stage source-checkout git clone --depth 1 --branch 26.09 https://github.com/verifast/verifast.git "$source_home"
[[ "$(git -C "$source_home" rev-parse HEAD)" == "$source_pin" ]] || exit 2
printf '%s  %s\n' "$schema_sha" "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" | sha256sum -c -
run_stage compiler-install rustup toolchain install "$RUSTUP_TOOLCHAIN" --profile minimal --component rustc-dev --component llvm-tools-preview
run_stage capnp-install bash -c 'sudo apt-get update && sudo apt-get install --yes --no-install-recommends capnproto'
compiler_sysroot=$(rustc --print sysroot)
{
    rustc --version --verbose
    capnp --version
    sha256sum "$stock_home/bin/vf-rust-mir-exporter" "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp"
} >> "$evidence/environment.txt"
run_stage normal-export-diagnostic python3 research/challenge-8/capture-select-pointer-normal-mir.py --stock-home "$stock_home" --schema "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" --compiler-sysroot "$compiler_sysroot" --evidence "$evidence/normal-ghost-capture"
