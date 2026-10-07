#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0 OR MIT
# Hosted-only stock VeriFast pointer/index projection evidence collector.
set -euo pipefail

[[ "${GITHUB_ACTIONS:-}" == true && "${RUNNER_ENVIRONMENT:-}" == github-hosted && "${RUNNER_OS:-}" == Linux ]] || {
  echo 'merge pointer harness requires GitHub-hosted Linux Actions' >&2
  exit 2
}
[[ "${GITHUB_REF:-}" == refs/heads/challenge-8/merge ]] || {
  echo 'merge pointer harness only accepts challenge-8/merge' >&2
  exit 2
}
[[ "${1:-}" == merge_geometry ]] || {
  echo 'expected workflow proof selection merge_geometry' >&2
  exit 2
}
cases=${2:-all}
repo=$(git rev-parse --show-toplevel)
cd "$repo"
[[ "$(git rev-parse HEAD)" == "${GITHUB_SHA:?GITHUB_SHA is required}" ]] || {
  echo 'checkout HEAD differs from dispatched GITHUB_SHA' >&2
  exit 2
}

evidence="$repo/research-results/merge-pointer"
[[ ! -e "$evidence" ]] || { echo "refusing to reuse prior evidence: $evidence" >&2; exit 2; }
mkdir -p "$evidence"
task_temp="$RUNNER_TEMP/challenge8-merge-pointer"
[[ ! -e "$task_temp" ]] || { echo "refusing to reuse prior tool directory: $task_temp" >&2; exit 2; }
mkdir -p "$task_temp"

vf_version=26.09
vf_source_commit=809de4596839b739dd999f9e462242c835e3af46
archive_sha=da1b619fa63ba73c12ce591638ced90fd2471add6f181d0e3310657fe4df98aa
console_sha=dc672335da76fe1bb06cf7ebca916185c34edb65466df0a937645a437c7f0ecc
schema_sha=7f3ebce320a33bcb956d51b8387754729e6516f4d15ba8dfdc61e6e36f90dfd9
tool_home="$task_temp/verifast-$vf_version"
archive="$task_temp/verifast-$vf_version-linux.tar.gz"
schema="$evidence/vf_mir.capnp"
export VFVERSION="$vf_version" VFPLATFORM=linux RUSTUP_TOOLCHAIN=nightly-2026-02-05

{
  printf 'Source SHA: '; git rev-parse HEAD
  printf 'Actions SHA: %s\nBranch: challenge-8/merge\nProof selection: merge_geometry / sort4_component=range\n' "$GITHUB_SHA"
  printf 'Profile: official-stock-VeriFast-%s\nTool source: %s\n' "$vf_version" "$vf_source_commit"
  printf 'Rust toolchain: %s\nRunner: %s/%s\n' "$RUSTUP_TOOLCHAIN" "$RUNNER_ENVIRONMENT" "$RUNNER_OS"
  sha256sum research/challenge-8/merge/pointer-run.sh research/challenge-8/merge/pointer-prove.py \
    research/challenge-8/merge/prove.py research/challenge-8/merge/pointer-cases.rs \
    library/core/src/slice/sort/shared/smallsort.rs
} > "$evidence/environment.txt"

curl --fail --silent --show-error --location --max-time 30 \
  "https://github.com/verifast/verifast/releases/download/$vf_version/verifast-$vf_version-linux.tar.gz" \
  --output "$archive"
printf '%s  %s\n' "$archive_sha" "$archive" | sha256sum -c -
tar -xzf "$archive" -C "$task_temp"
printf '%s  %s\n' "$console_sha" "$tool_home/bin/verifast" | sha256sum -c -
sha256sum "$archive" "$tool_home/bin/verifast" "$tool_home/bin/vf-rust-mir-exporter" \
  "$tool_home/bin/refinement-checker" >> "$evidence/environment.txt"

timeout --signal=TERM --kill-after=5s 120s rustup toolchain install "$RUSTUP_TOOLCHAIN"
sudo timeout --signal=TERM --kill-after=5s 90s apt-get update
sudo timeout --signal=TERM --kill-after=5s 90s apt-get install --yes --no-install-recommends capnproto
capnp --version >> "$evidence/environment.txt"
curl --fail --silent --show-error --location --max-time 30 \
  "https://raw.githubusercontent.com/verifast/verifast/$vf_source_commit/src/rust_frontend/vf_mir/vf_mir.capnp" \
  --output "$schema"
printf '%s  %s\n' "$schema_sha" "$schema" | sha256sum -c -
printf 'Schema SHA-256: %s\n' "$schema_sha" >> "$evidence/environment.txt"

compiler_sysroot=$(rustc --print sysroot)
export LD_LIBRARY_PATH="$compiler_sysroot/lib:$tool_home/bin:${LD_LIBRARY_PATH:-}"
{
  rustc --version --verbose
  printf 'Compiler sysroot: %s\n' "$compiler_sysroot"
  find "$tool_home/bin/rust" -type f -name '*.rsspec' -print0 | sort -z | xargs -0 -r sha256sum
  ldd "$tool_home/bin/verifast"
} >> "$evidence/environment.txt" 2>&1

set +e
/usr/bin/time -v -o "$evidence/resources.txt" \
  timeout --signal=TERM --kill-after=5s 300s \
  python3 research/challenge-8/merge/pointer-prove.py \
    --tool-home "$tool_home" --compiler-sysroot "$compiler_sysroot" \
    --schema "$schema" --evidence "$evidence/checked" --cases "$cases" \
    2>&1 | tee "$evidence/execution.log"
status=${PIPESTATUS[0]}
set -e
printf '%s\n' "$status" > "$evidence/exit-code.txt"
exit "$status"
