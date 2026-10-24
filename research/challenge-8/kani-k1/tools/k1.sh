#!/usr/bin/env bash
# Agent helper for the Kani K-1 lane. Reads only GitHub run metadata and the run's artifacts.
#   k1.sh find-run SHA                  wait up to 180 s for the run of commit SHA, print its id
#   k1.sh wait RUN_ID                   block until the run is completed (background task), print conclusion
#   k1.sh summary RUN_ID                download the kani-k1-summary artifact, print summary.md
#   k1.sh check-tooling RUN_ID BASE     lane files of the run's commit equal BASE (git diff + summary hashes); exit 1 otherwise
#   k1.sh log-grep RUN_ID REGEX [MAX]   bounded grep of kani.log (MAX <= 200 matching lines)
#   k1.sh log-lines RUN_ID START [N]    bounded slice of kani.log (N <= 200 lines)
set -euo pipefail

REPO=${K1_REPO:-Tiramisu-Cake/verify-rust-std}
WORKFLOW="SmallSort Kani K1"
CACHE=${K1_CACHE:-${TMPDIR:-/tmp}/kani-k1-runs}

die() { echo "k1.sh: $*" >&2; exit 2; }
is_id() { [[ "$1" =~ ^[0-9]+$ ]] || die "run id must be numeric: $1"; }

run_field() { gh run view "$1" -R "$REPO" --json "$2" --jq ".$2"; }

fetch() {  # fetch RUN_ID ARTIFACT -> prints directory; cache is keyed by run id and attempt
  local run=$1 name=$2 attempt dir tmp
  attempt=$(run_field "$run" attempt)
  dir="$CACHE/$run-$attempt/$name"
  if [ ! -d "$dir" ]; then
    mkdir -p "$(dirname "$dir")"
    tmp=$(mktemp -d "$(dirname "$dir")/.fetch.XXXXXX")
    if ! gh run download "$run" -R "$REPO" -n "$name" -D "$tmp" >/dev/null; then
      rm -rf "$tmp"; die "artifact $name of run $run not available"
    fi
    mv -T "$tmp" "$dir" 2>/dev/null || rm -rf "$tmp"   # another fetch won the race: keep its copy
  fi
  echo "$dir"
}

cmd=${1:-}; shift || true
case "$cmd" in
  find-run)
    sha=${1:-}; [[ "$sha" =~ ^[0-9a-f]{40}$ ]] || die "full 40-hex commit SHA required"
    for _ in $(seq 1 12); do
      # Not --workflow: gh resolves workflow names only from the default branch, and this one lives on
      # the experiment branches.
      id=$(gh run list -R "$REPO" --commit "$sha" --limit 20 --json databaseId,workflowName \
             --jq "map(select(.workflowName == \"$WORKFLOW\")) | .[0].databaseId // empty")
      if [ -n "$id" ]; then echo "$id"; exit 0; fi
      sleep 15
    done
    die "no '$WORKFLOW' run for $sha after 180 s (was RUN-REQUEST.json changed and pushed?)" ;;
  wait)
    run=${1:-}; is_id "$run"
    deadline=$(( $(date +%s) + 300 * 60 ))   # job timeout 240 min + plan job + queue margin
    until [ "$(run_field "$run" status 2>/dev/null || echo unknown)" = "completed" ]; do
      [ "$(date +%s)" -lt "$deadline" ] || die "run $run not completed after 300 min; check it manually"
      gh run watch "$run" -R "$REPO" --interval 60 >/dev/null 2>&1 || sleep 60
    done
    gh run view "$run" -R "$REPO" --json status,conclusion,attempt,url --jq '"run \(.url) attempt \(.attempt) status=\(.status) conclusion=\(.conclusion)"' ;;
  summary)
    run=${1:-}; is_id "$run"
    dir=$(fetch "$run" kani-k1-summary)
    cat "$dir/summary.md" ;;
  check-tooling)
    # Independent of what the run reports: the run's commit comes from GitHub, the lane files are
    # compared with BASE by local git, and the summary must bind exactly the same four files.
    run=${1:-}; is_id "$run"; base=${2:-}; [[ "$base" =~ ^[0-9a-f]{40}$ ]] || die "full 40-hex BASE commit required"
    head=$(run_field "$run" headSha)
    [[ "$head" =~ ^[0-9a-f]{40}$ ]] || die "cannot read headSha of run $run"
    git cat-file -e "$head^{commit}" 2>/dev/null || git fetch -q origin "$head" || die "commit $head not available locally"
    git cat-file -e "$base^{commit}" 2>/dev/null || die "BASE $base not available locally"
    dir=$(fetch "$run" kani-k1-summary)
    paths=(.github/workflows/smallsort-kani-k1.yml research/challenge-8/kani-k1/tools/kani_k1.py
           scripts/run-kani.sh tool_config/kani-version.toml)
    # Whole workflow and tools directories: a second workflow could otherwise upload a forged summary.
    lane=(.github/workflows research/challenge-8/kani-k1/tools scripts/run-kani.sh tool_config/kani-version.toml)
    rc=0
    event=$(run_field "$run" event)
    if [ "$event" != "push" ]; then echo "DIFF run event is '$event', expected push"; rc=1; fi
    if git diff --quiet "$base" "$head" -- "${lane[@]}"; then
      echo "ok   workflows, lane tools, run-kani.sh and kani-version.toml at run commit $head equal BASE $base"
    else
      echo "DIFF lane files changed between BASE and run commit:"; git diff --stat "$base" "$head" -- "${lane[@]}"; rc=1
    fi
    python3 -B - "$dir/summary.json" "$head" "$base" "${paths[@]}" <<'PY' || rc=1
import hashlib, json, subprocess, sys
summary, head, base, paths = json.load(open(sys.argv[1])), sys.argv[2], sys.argv[3], sys.argv[4:]
bad = 0
if summary.get("head_sha") != head:
    print(f"DIFF summary head_sha {summary.get('head_sha')} != GitHub headSha {head}"); bad += 1
tooling = summary.get("tooling_sha256") or {}
if sorted(tooling) != sorted(paths):
    print(f"DIFF summary binds {sorted(tooling)}, expected exactly {sorted(paths)}"); bad += 1
for path in paths:
    blob = subprocess.run(["git", "show", f"{base}:{path}"], capture_output=True).stdout
    want = hashlib.sha256(blob).hexdigest()
    got = tooling.get(path, "ABSENT")
    ok = got == want
    bad += not ok
    print(f"{'ok  ' if ok else 'DIFF'} {path} summary={got[:16]} base={want[:16]}")
sys.exit(1 if bad else 0)
PY
    exit "$rc" ;;
  log-grep)
    run=${1:-}; is_id "$run"; re=${2:-}; [ -n "$re" ] || die "regex required"
    max=${3:-60}; [[ "$max" =~ ^[0-9]+$ ]] && [ "$max" -le 200 ] || die "MAX must be <= 200"
    dir=$(fetch "$run" kani-k1-log)
    grep -n -E -m "$max" -- "$re" "$dir/kani.log" | cut -c1-400 || echo "(no match)" ;;
  log-lines)
    run=${1:-}; is_id "$run"; start=${2:-}; count=${3:-80}
    [[ "$start" =~ ^[0-9]+$ ]] || die "START must be a line number"
    [[ "$count" =~ ^[0-9]+$ ]] && [ "$count" -le 200 ] || die "N must be <= 200"
    dir=$(fetch "$run" kani-k1-log)
    sed -n "${start},$((start + count - 1))p" "$dir/kani.log" | cut -c1-400 ;;
  *)
    sed -n '2,9p' "$0"; exit 2 ;;
esac
