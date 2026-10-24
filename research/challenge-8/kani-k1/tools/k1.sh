#!/usr/bin/env bash
# Agent helper for the Kani K-1 lane. Reads only GitHub run metadata and the run's artifacts.
#   k1.sh find-run SHA                  wait up to 180 s for the run of commit SHA, print its id
#   k1.sh wait RUN_ID                   block until the run is completed (background task), print conclusion
#   k1.sh summary RUN_ID                download the kani-k1-summary artifact, print summary.md
#   k1.sh check-tooling RUN_ID BASE     compare the run's tooling SHA-256 with commit BASE; exit 1 on mismatch
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
      id=$(gh run list -R "$REPO" --workflow "$WORKFLOW" --commit "$sha" --limit 5 --json databaseId --jq '.[0].databaseId // empty')
      if [ -n "$id" ]; then echo "$id"; exit 0; fi
      sleep 15
    done
    die "no '$WORKFLOW' run for $sha after 180 s (was RUN-REQUEST.json changed and pushed?)" ;;
  wait)
    run=${1:-}; is_id "$run"
    until [ "$(run_field "$run" status)" = "completed" ]; do
      gh run watch "$run" -R "$REPO" --interval 60 >/dev/null 2>&1 || sleep 60
    done
    gh run view "$run" -R "$REPO" --json status,conclusion,attempt,url --jq '"run \(.url) attempt \(.attempt) status=\(.status) conclusion=\(.conclusion)"' ;;
  summary)
    run=${1:-}; is_id "$run"
    dir=$(fetch "$run" kani-k1-summary)
    cat "$dir/summary.md" ;;
  check-tooling)
    run=${1:-}; is_id "$run"; base=${2:-}; [[ "$base" =~ ^[0-9a-f]{40}$ ]] || die "full 40-hex BASE commit required"
    dir=$(fetch "$run" kani-k1-summary)
    root=$(git rev-parse --show-toplevel)
    python3 -B - "$dir/summary.json" "$base" "$root" <<'PY'
import hashlib, json, subprocess, sys
summary, base, root = json.load(open(sys.argv[1])), sys.argv[2], sys.argv[3]
tooling = summary.get("tooling_sha256") or {}
if not tooling:
    print("tooling: NO BINDINGS in summary"); sys.exit(1)
bad = 0
for path, digest in sorted(tooling.items()):
    try:
        blob = subprocess.run(["git", "-C", root, "show", f"{base}:{path}"], capture_output=True, check=True).stdout
        want = hashlib.sha256(blob).hexdigest()
    except subprocess.CalledProcessError:
        want = "MISSING"
    ok = digest == want
    bad += not ok
    print(f"{'ok  ' if ok else 'DIFF'} {path} run={digest[:16]} base={want[:16]}")
sys.exit(1 if bad else 0)
PY
    ;;
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
