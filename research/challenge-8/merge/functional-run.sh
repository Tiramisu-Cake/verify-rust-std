#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0 OR MIT
set -euo pipefail
[[ "${GITHUB_ACTIONS:-}" == true && "${RUNNER_ENVIRONMENT:-}" == github-hosted && "${RUNNER_OS:-}" == Linux ]] || { echo 'GitHub-hosted Linux only' >&2; exit 2; }
[[ "${GITHUB_REF:-}" == refs/heads/challenge-8/merge ]] || exit 2
[[ "${1:-}" == merge_functional_ids ]] || exit 2
repo=$(git rev-parse --show-toplevel)
cd "$repo"
evidence="$repo/research-results/merge-functional-ids"
mkdir -p "$evidence"
task_temp="$RUNNER_TEMP/challenge8-merge-functional-ids"
mkdir "$task_temp"
archive="$task_temp/verifast-26.09-linux.tar.gz"
tool_home="$task_temp/verifast-26.09"
{
  printf 'Source SHA: '; git rev-parse HEAD
  printf 'Actions SHA: %s\nProfile: official-stock-26.09\nPhase: merge-functional-ids-A\n' "$GITHUB_SHA"
  printf 'Source pin: 809de4596839b739dd999f9e462242c835e3af46\n'
  printf 'Hosted: %s/%s\nNo tool patch or local build\n' "$RUNNER_ENVIRONMENT" "$RUNNER_OS"
  sha256sum "$0" research/challenge-8/merge/functional-prove.py research/challenge-8/merge/functional-ids.c research/challenge-8/merge/prove.py research/challenge-8/merge/geometry.c research/challenge-8/networks/prove.py library/core/src/slice/sort/shared/smallsort.rs
} > "$evidence/environment.txt"
[[ "$(git rev-parse HEAD)" == "$GITHUB_SHA" ]] || exit 2
printf '%s  %s\n' 32d009716b6b3dacc7f300ced0a1950a90ff0d8872253d7d63efe627a221774f research/challenge-8/merge/prove.py | sha256sum -c -
printf '%s  %s\n' 4594f159400bcfeeea87e3086e5765472d121dced7385bd2ef216a83bf24dea8 research/challenge-8/merge/geometry.c | sha256sum -c -
printf '%s  %s\n' 994afa65a24c1deb73fd120ac88c96fa5d86eb971f58adba678c850a1153d0c4 research/challenge-8/networks/prove.py | sha256sum -c -
printf '%s  %s\n' 32574fd06623190132f213cbfeaeca5bd466e3c802ca97a2174e24fd3c240959 library/core/src/slice/sort/shared/smallsort.rs | sha256sum -c -
curl --fail --silent --show-error --location --max-time 60 \
  https://github.com/verifast/verifast/releases/download/26.09/verifast-26.09-linux.tar.gz --output "$archive"
printf '%s  %s\n' da1b619fa63ba73c12ce591638ced90fd2471add6f181d0e3310657fe4df98aa "$archive" | sha256sum -c -
tar -xzf "$archive" -C "$task_temp"
printf '%s  %s\n' dc672335da76fe1bb06cf7ebca916185c34edb65466df0a937645a437c7f0ecc "$tool_home/bin/verifast" | sha256sum -c -
export LD_LIBRARY_PATH="$tool_home/bin:${LD_LIBRARY_PATH:-}"
sha256sum "$archive" "$tool_home/bin/verifast" >> "$evidence/environment.txt"
# Six-minute hosted job; five-minute proof process; each case has the
# unchanged frozen classifier's 180-second bound.
set +e
/usr/bin/time -v -o "$evidence/resources.txt" timeout --signal=TERM --kill-after=5s 300s \
  python3 research/challenge-8/merge/functional-prove.py --tool-home "$tool_home" --evidence "$evidence/checked" \
  2>&1 | tee "$evidence/execution.log"
status=${PIPESTATUS[0]}
set -e
printf '%s\n' "$status" > "$evidence/exit-code.txt"
exit "$status"
