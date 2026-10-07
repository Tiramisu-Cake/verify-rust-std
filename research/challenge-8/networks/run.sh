#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0 OR MIT
set -euo pipefail
[[ "${GITHUB_ACTIONS:-}" == true && "${RUNNER_ENVIRONMENT:-}" == github-hosted && "${RUNNER_OS:-}" == Linux ]] || { echo 'GitHub-hosted Linux only' >&2; exit 2; }
[[ "${GITHUB_REF:-}" == refs/heads/challenge-8/networks ]] || exit 2
selection=${1:?network selection required}
case "$selection" in
  networks9) size=9 ;;
  networks13) size=13 ;;
  *) exit 2 ;;
esac
repo=$(git rev-parse --show-toplevel)
cd "$repo"
evidence="$repo/research-results/networks"
mkdir -p "$evidence"
task_temp="$RUNNER_TEMP/challenge8-networks-$size"
mkdir "$task_temp"
archive="$task_temp/verifast-26.09-linux.tar.gz"
tool_home="$task_temp/verifast-26.09"
{
  printf 'Source SHA: '; git rev-parse HEAD
  printf 'Actions SHA: %s\nProfile: official-stock-26.09\nNetwork: %s\n' "$GITHUB_SHA" "$size"
  printf 'Source pin: 809de4596839b739dd999f9e462242c835e3af46\n'
  printf 'Hosted: %s/%s\nNo tool patch or local build\n' "$RUNNER_ENVIRONMENT" "$RUNNER_OS"
  sha256sum "$0" research/challenge-8/networks/prove.py library/core/src/slice/sort/shared/smallsort.rs
} > "$evidence/environment.txt"
[[ "$(git rev-parse HEAD)" == "$GITHUB_SHA" ]] || exit 2
curl --fail --silent --show-error --location --max-time 60 \
  https://github.com/verifast/verifast/releases/download/26.09/verifast-26.09-linux.tar.gz --output "$archive"
printf '%s  %s\n' da1b619fa63ba73c12ce591638ced90fd2471add6f181d0e3310657fe4df98aa "$archive" | sha256sum -c -
tar -xzf "$archive" -C "$task_temp"
export LD_LIBRARY_PATH="$tool_home/bin:${LD_LIBRARY_PATH:-}"
sha256sum "$archive" "$tool_home/bin/verifast" >> "$evidence/environment.txt"
# One independent job, full cold preparation included. Workflow cap10min,
# inner reserve60s for evidence; never consume the other direction's budget.
set +e
/usr/bin/time -v -o "$evidence/resources.txt" timeout --signal=TERM --kill-after=5s 480s \
  python3 research/challenge-8/networks/prove.py --size "$size" --tool-home "$tool_home" --evidence "$evidence/checked" \
  2>&1 | tee "$evidence/execution.log"
status=${PIPESTATUS[0]}
set -e
printf '%s\n' "$status" > "$evidence/exit-code.txt"
exit "$status"
