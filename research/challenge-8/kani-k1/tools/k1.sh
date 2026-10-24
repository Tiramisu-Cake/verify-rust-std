#!/usr/bin/env bash
# Agent helper for the Kani K-1 lane. Reads only GitHub run metadata and the run's artifacts.
#   k1.sh find-run SHA           wait up to 180 s for the run of commit SHA, print its id
#   k1.sh wait RUN_ID            block until the run ends (use as a background task), print conclusion
#   k1.sh summary RUN_ID         download the kani-k1-summary artifact, print summary.md
#   k1.sh log-grep RUN_ID REGEX [MAX]      bounded grep of kani.log (MAX <= 200 matching lines)
#   k1.sh log-lines RUN_ID START [COUNT]   bounded slice of kani.log (COUNT <= 200 lines)
set -euo pipefail

REPO=${K1_REPO:-Tiramisu-Cake/verify-rust-std}
WORKFLOW="SmallSort Kani K1"
CACHE=${K1_CACHE:-${TMPDIR:-/tmp}/kani-k1-runs}

die() { echo "k1.sh: $*" >&2; exit 2; }
is_id() { [[ "$1" =~ ^[0-9]+$ ]] || die "run id must be numeric: $1"; }

fetch() {  # fetch RUN_ID ARTIFACT -> prints directory
  local run=$1 name=$2 dir="$CACHE/$1/$2"
  if [ ! -d "$dir" ]; then
    mkdir -p "$dir.tmp"
    gh run download "$run" -R "$REPO" -n "$name" -D "$dir.tmp" >/dev/null || { rm -rf "$dir.tmp"; die "artifact $name of run $run not available"; }
    mv "$dir.tmp" "$dir"
  fi
  echo "$dir"
}

cmd=${1:-}; shift || true
case "$cmd" in
  find-run)
    sha=${1:-}; [[ "$sha" =~ ^[0-9a-f]{40}$ ]] || die "full 40-hex commit SHA required"
    for _ in $(seq 1 12); do
      id=$(gh run list -R "$REPO" --workflow "$WORKFLOW" --commit "$sha" --limit 5 --json databaseId --jq '.[0].databaseId // empty')
      if [ -n "$id" ]; then echo "$id"; exit 0; fi
      sleep 15
    done
    die "no '$WORKFLOW' run for $sha after 180 s (was RUN-REQUEST.json changed and pushed?)" ;;
  wait)
    run=${1:-}; is_id "$run"
    gh run watch "$run" -R "$REPO" --interval 60 >/dev/null 2>&1 || true
    gh run view "$run" -R "$REPO" --json status,conclusion,url --jq '"run \(.url) status=\(.status) conclusion=\(.conclusion)"' ;;
  summary)
    run=${1:-}; is_id "$run"
    dir=$(fetch "$run" kani-k1-summary)
    cat "$dir/summary.md" ;;
  log-grep)
    run=${1:-}; is_id "$run"; re=${2:-}; [ -n "$re" ] || die "regex required"
    max=${3:-60}; [[ "$max" =~ ^[0-9]+$ ]] && [ "$max" -le 200 ] || die "MAX must be <= 200"
    dir=$(fetch "$run" kani-k1-log)
    grep -n -E -m "$max" -- "$re" "$dir/kani.log" | cut -c1-400 || echo "(no match)" ;;
  log-lines)
    run=${1:-}; is_id "$run"; start=${2:-}; count=${3:-80}
    [[ "$start" =~ ^[0-9]+$ ]] || die "START must be a line number"
    [[ "$count" =~ ^[0-9]+$ ]] && [ "$count" -le 200 ] || die "COUNT must be <= 200"
    dir=$(fetch "$run" kani-k1-log)
    sed -n "${start},$((start + count - 1))p" "$dir/kani.log" | cut -c1-400 ;;
  *)
    sed -n '2,8p' "$0"; exit 2 ;;
esac
