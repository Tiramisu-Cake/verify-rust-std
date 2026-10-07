#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0 OR MIT
set -euo pipefail
[[ "${GITHUB_ACTIONS:-}" == true && "${RUNNER_ENVIRONMENT:-}" == github-hosted && "${RUNNER_OS:-}" == Linux ]] || { echo 'GitHub-hosted Linux only' >&2; exit 2; }
[[ "${GITHUB_REF:-}" == refs/heads/challenge-8/networks ]] || exit 2
selection=${1:?network selection required}
scope_args=()
inner_limit=420
case "$selection" in
  ranks9) size=9 ;;
  ranks13) size=13 ;;
  ranks13_symbolic) size=13; scope_args=(--scope symbolic); inner_limit=270 ;;
  *) exit 2 ;;
esac
repo=$(git rev-parse --show-toplevel)
cd "$repo"
evidence="$repo/research-results/networks-ranks"
mkdir -p "$evidence"
task_temp="$RUNNER_TEMP/challenge8-networks-ranks-$size"
mkdir "$task_temp"
archive="$task_temp/verifast-26.09-linux.tar.gz"
tool_home="$task_temp/verifast-26.09"
{
  printf 'Source SHA: '; git rev-parse HEAD
  printf 'Actions SHA: %s\nProfile: official-stock-26.09\nPhase: finite-SWO-rank\nNetwork: %s\n' "$GITHUB_SHA" "$size"
  printf 'Source pin: 809de4596839b739dd999f9e462242c835e3af46\n'
  printf 'Hosted: %s/%s\nNo tool patch or local build\n' "$RUNNER_ENVIRONMENT" "$RUNNER_OS"
  if [[ "$selection" == ranks13_symbolic ]]; then
    printf 'Scope: partial symbolic N13 component; exact literal-domain specialization remains unaccepted\n'
  fi
  sha256sum "$0" research/challenge-8/networks/prove.py research/challenge-8/networks/prove-ranks.py research/challenge-8/networks/swo-rank.c library/core/src/slice/sort/shared/smallsort.rs
} > "$evidence/environment.txt"
[[ "$(git rev-parse HEAD)" == "$GITHUB_SHA" ]] || exit 2
printf '%s  %s\n' 994afa65a24c1deb73fd120ac88c96fa5d86eb971f58adba678c850a1153d0c4 research/challenge-8/networks/prove.py | sha256sum -c -
curl --fail --silent --show-error --location --max-time 60 \
  https://github.com/verifast/verifast/releases/download/26.09/verifast-26.09-linux.tar.gz --output "$archive"
printf '%s  %s\n' da1b619fa63ba73c12ce591638ced90fd2471add6f181d0e3310657fe4df98aa "$archive" | sha256sum -c -
tar -xzf "$archive" -C "$task_temp"
export LD_LIBRARY_PATH="$tool_home/bin:${LD_LIBRARY_PATH:-}"
sha256sum "$archive" "$tool_home/bin/verifast" >> "$evidence/environment.txt"
# One independent job: exact selections retain the 8min/420s limits;
# symbolic N13 uses a 5min job/270s inner limit with evidence reserve.
set +e
/usr/bin/time -v -o "$evidence/resources.txt" timeout --signal=TERM --kill-after=5s "${inner_limit}s" \
  python3 research/challenge-8/networks/prove-ranks.py --size "$size" "${scope_args[@]}" --tool-home "$tool_home" --evidence "$evidence/checked" \
  2>&1 | tee "$evidence/execution.log"
status=${PIPESTATUS[0]}
set -e
printf '%s\n' "$status" > "$evidence/exit-code.txt"
exit "$status"
