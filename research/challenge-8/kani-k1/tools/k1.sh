#!/usr/bin/env bash
# Agent helper for the Kani K-1 lane on CircleCI. Reads only CircleCI pipeline/job metadata and the
# job's artifacts. The API token is read from a root-only file and passed to curl as a config on
# stdin, so it never appears in process arguments or output.
#   k1.sh dispatch BRANCH               start the lane on the pushed BRANCH, print the job number
#   k1.sh wait JOB                      block until the job ends (background task), print its status
#   k1.sh watch JOB                     Codex: detached wait, then `codex queue` into $CODEX_THREAD_ID; end the turn
#   k1.sh summary JOB                   download the summary artifact, print summary.md
#   k1.sh check-tooling JOB BASE        lane files of the job's commit equal BASE; exit 1 otherwise
#   k1.sh log-grep JOB REGEX [MAX]      bounded grep of kani.log (MAX <= 200 matching lines)
#   k1.sh log-lines JOB START [N]       bounded slice of kani.log (N <= 200 lines)
set -euo pipefail

API=https://circleci.com/api/v2
SLUG=circleci/PBSy8HxcMvQrUER5EX8Ah2/SwwrwNYuSGo1ny9mvHtPZ2   # project Verify-rust-std
DEFINITION=0bc9e80e-1660-4795-b651-949e3fd4a945              # pipeline definition .circleci/config.yml (no triggers)
TOKEN_FILE=${K1_CIRCLE_TOKEN_FILE:-/root/.config/smallsort-ci/circleci-token}
CACHE=${K1_CACHE:-${TMPDIR:-/tmp}/kani-k1-jobs}
# Everything that shapes the Kani build or the verify-std run besides the proof sources themselves.
LANE_PATHS=(.circleci .github/workflows research/challenge-8/kani-k1/tools scripts/run-kani.sh tool_config/kani-version.toml
            rust-toolchain.toml .gitmodules .cargo library/.cargo library/Cargo.toml library/Cargo.lock)
BOUND_FILES=(.circleci/config.yml research/challenge-8/kani-k1/tools/kani_k1.py
             research/challenge-8/kani-k1/tools/circleci-k1.sh scripts/run-kani.sh tool_config/kani-version.toml)

die() { echo "k1.sh: $*" >&2; exit 2; }
is_job() { [[ "$1" =~ ^[0-9]+$ ]] || die "job number must be numeric: $1"; }
[ -r "$TOKEN_FILE" ] || die "CircleCI token file $TOKEN_FILE not readable"

# curl with the token header; prints the body, fails with a short message on HTTP >= 400.
cci() {
  local out code
  out=$(mktemp)
  code=$(printf 'header = "Circle-Token: %s"\n' "$(tr -d '\n\r ' < "$TOKEN_FILE")" \
         | curl -sS -K - -o "$out" -w '%{http_code}' "$@") || { rm -f "$out"; die "request failed: ${*: -1}"; }
  if [ "$code" -ge 400 ]; then
    echo "k1.sh: HTTP $code for ${*: -1}: $(head -c 300 "$out")" >&2; rm -f "$out"; exit 2
  fi
  cat "$out"; rm -f "$out"
}
# Artifact download: the token goes only to CircleCI; a redirect target is fetched without it.
artifact_get() {  # artifact_get URL OUTFILE
  local meta code location
  [[ "$1" =~ ^https://([a-z0-9-]+\.)*(circleci\.com|circle-artifacts\.com)/ ]] || die "unexpected artifact host: ${1%%\?*}"
  meta=$(printf 'header = "Circle-Token: %s"\n' "$(tr -d '\n\r ' < "$TOKEN_FILE")" \
         | curl -sS -K - -o "$2" -w '%{http_code} %{redirect_url}' "$1") || die "artifact request failed"
  code=${meta%% *}; location=${meta#* }
  if [[ "$code" =~ ^30[1278]$ ]]; then
    [ -n "$location" ] || die "artifact redirect without a location: ${1%%\?*}"
    curl -sS -f -o "$2" "$location" || die "artifact redirect download failed"
  elif [ "$code" -ge 400 ]; then
    die "HTTP $code for artifact $1"
  fi
}
# Pipeline revision: OAuth projects report vcs.revision, GitHub App projects trigger_parameters.
REV_EXPR="(d.get('vcs') or {}).get('revision') or ((d.get('trigger_parameters') or {}).get('git') or {}).get('checkout_sha') or ((d.get('trigger_parameters') or {}).get('github_app') or {}).get('commit_sha') or ''"
jqr() { python3 -c "import json,sys; d=json.load(sys.stdin); print(eval(sys.argv[1], {'d': d}))" "$1"; }

job_status() { cci "$API/project/$SLUG/job/$1" | jqr "d.get('status')"; }
TERMINAL=" success failed canceled infrastructure_fail timedout not_run terminated-unknown unauthorized "

fetch() {  # fetch JOB -> directory with summary/ and log/ artifacts; only for finished jobs, which are immutable
  local job=$1 dir="$CACHE/$1" tmp status
  if [ ! -d "$dir" ]; then
    status=$(job_status "$job")
    [[ "$TERMINAL" == *" $status "* ]] || die "job $job is not finished (status $status); wait for it first"
    mkdir -p "$CACHE"
    tmp=$(mktemp -d "$CACHE/.fetch.XXXXXX")
    cci "$API/project/$SLUG/$job/artifacts" | python3 -c '
import json, sys
for a in json.load(sys.stdin).get("items", []):
    print(a["path"] + "\t" + a["url"])' > "$tmp/index.tsv"
    while IFS=$'\t' read -r path url; do
      [[ "$path" =~ ^(summary|log)/[A-Za-z0-9._-]+$ ]] && [[ "$path" != *..* ]] || continue
      mkdir -p "$tmp/$(dirname "$path")"
      artifact_get "$url" "$tmp/$path"
    done < "$tmp/index.tsv"
    mv -T "$tmp" "$dir" 2>/dev/null || rm -rf "$tmp"
  fi
  echo "$dir"
}

cmd=${1:-}; shift || true
case "$cmd" in
  dispatch)
    branch=${1:-}; [[ "$branch" =~ ^experiment/kani-k1-[a-z]+-[0-9]{8}$ ]] || die "branch must be experiment/kani-k1-<name>-<date>"
    git fetch -q origin "$branch" || die "branch $branch is not published"
    sha=$(git rev-parse "origin/$branch")
    [ "$(git rev-parse "$branch" 2>/dev/null)" = "$sha" ] || die "local $branch differs from origin; push it first"
    git show "$sha:research/challenge-8/kani-k1/RUN-REQUEST.json" >/dev/null 2>&1 || die "no RUN-REQUEST.json at $sha"
    page=""; for _ in 1 2 3; do   # the three most recent pages (about 60 pipelines)
      resp=$(cci "$API/project/$SLUG/pipeline${page:+?page-token=$page}")
      dup=$(jqr "[p['number'] for p in d.get('items', []) if p.get('state') != 'errored' and (lambda d: $REV_EXPR)(p) == '$sha']" <<< "$resp")
      [ "$dup" = "[]" ] || die "pipeline(s) $dup already ran $sha; change and push RUN-REQUEST.json for a new run"
      page=$(jqr "d.get('next_page_token') or ''" <<< "$resp"); [ -n "$page" ] || break
    done
    body=$(python3 -c 'import json,sys; b=sys.argv[1]; print(json.dumps({"definition_id": sys.argv[2], "config": {"branch": b}, "checkout": {"branch": b}, "parameters": {"run_k1": True}}))' "$branch" "$DEFINITION")
    pid=$(cci -X POST -H 'Content-Type: application/json' -d "$body" "$API/project/$SLUG/pipeline/run" | jqr "d['id']")
    for _ in $(seq 1 18); do
      p=$(cci "$API/pipeline/$pid")
      state=$(jqr "d.get('state')" <<< "$p")
      if [ "$state" = "errored" ]; then die "pipeline errored: $(jqr "d.get('errors')" <<< "$p" | head -c 600)"; fi
      rev=$(jqr "$REV_EXPR" <<< "$p")
      wf=$(cci "$API/pipeline/$pid/workflow" | jqr "d['items'][0]['id'] if d.get('items') else ''")
      if [ -n "$wf" ]; then
        job=$(cci "$API/workflow/$wf/job" | jqr "next((j.get('job_number') or '' for j in d.get('items', []) if j.get('name') == 'k1'), '')")
        if [ -n "$job" ] && [ "$job" != "None" ]; then
          if [ "$rev" != "$sha" ]; then
            cci -X POST "$API/workflow/$wf/cancel" >/dev/null || true
            die "pipeline revision $rev differs from $sha (branch moved?); its job $job was canceled"
          fi
          echo "$job"; exit 0
        fi
      fi
      sleep 10
    done
    die "pipeline $pid has no k1 job after 180 s" ;;
  wait)
    job=${1:-}; is_job "$job"
    deadline=$(( $(date +%s) + 90 * 60 ))   # the job itself is capped at 60 min on the free plan
    while :; do
      status=$(job_status "$job" 2>/dev/null || echo unknown)
      [[ "$TERMINAL" == *" $status "* ]] && break
      [ "$(date +%s)" -lt "$deadline" ] || die "job $job not finished after 90 min (status $status)"
      sleep 60
    done
    echo "job $job status=$status" ;;
  watch)
    # Same delivery as k1g.sh watch: a detached waiter without a model queues one message into the calling
    # Codex thread when the job ends, up to 3 attempts 2 min apart, the control socket re-resolved each time
    # (the daemon republishes it on restart). Outcome in the watch log. No active Codex goal.
    job=${1:-}; is_job "$job"
    thread=${CODEX_THREAD_ID:-}
    [[ "$thread" =~ ^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$ ]] || die "CODEX_THREAD_ID is not set: use a foreground wait"
    link=/root/.codex/app-server-control/app-server-control.sock
    sock=$(readlink -f "$link" 2>/dev/null || true)
    [ -n "$sock" ] && [ -S "$sock" ] || die "no Codex app-server control socket: use a foreground wait"
    command -v codex >/dev/null || die "codex not on PATH: use a foreground wait"
    mkdir -p "$CACHE"; log="$CACHE/watch-$job.log"
    [ ! -e "$log" ] || die "job $job is already watched (log $log)"
    setsid nohup bash -c '
      "$1" wait "$2" > "$3" 2>&1; rc=$?
      msg="k1 watch: $(tail -n 1 "$3" | cut -c1-200) (wait exit $rc). Next: k1.sh summary $2"
      for attempt in 1 2 3; do
        if timeout 60 codex queue --remote "unix://$(readlink -f "$4")" --thread "$5" --message "$msg (delivery attempt $attempt)" >> "$3" 2>&1; then
          echo "DELIVERED attempt $attempt" >> "$3"; exit 0
        fi
        echo "DELIVERY_FAILED_OR_UNKNOWN attempt $attempt" >> "$3"; [ "$attempt" = 3 ] || sleep 120
      done
    ' k1-watch "$(readlink -f "$0")" "$job" "$log" "$link" "$thread" < /dev/null > /dev/null 2>&1 &
    echo "watching job $job for thread $thread (log $log). End the turn now; a queued message will wake it." ;;
  summary)
    job=${1:-}; is_job "$job"
    dir=$(fetch "$job")
    [ -f "$dir/summary/summary.md" ] || die "job $job has no summary artifact: treat as RUNNER_ERROR (job timed out or was canceled?)"
    cat "$dir/summary/summary.md" ;;
  check-tooling)
    # Independent of what the job reports: the commit comes from the CircleCI pipeline, the lane
    # files are compared with BASE by local git, and the summary must bind exactly BOUND_FILES.
    job=${1:-}; is_job "$job"; base=${2:-}; [[ "$base" =~ ^[0-9a-f]{40}$ ]] || die "full 40-hex BASE commit required"
    pid=$(cci "$API/project/$SLUG/job/$job" | jqr "d['pipeline']['id']")
    p=$(cci "$API/pipeline/$pid")
    head=$(jqr "$REV_EXPR" <<< "$p")
    trigger=$(jqr "(d.get('trigger') or {}).get('type')" <<< "$p")
    [[ "$head" =~ ^[0-9a-f]{40}$ ]] || die "cannot read the pipeline revision of job $job"
    git cat-file -e "$head^{commit}" 2>/dev/null || git fetch -q origin "$head" || die "commit $head not available locally"
    git cat-file -e "$base^{commit}" 2>/dev/null || die "BASE $base not available locally"
    echo "pipeline trigger: $trigger"
    # Compare the lane before downloading anything the job produced.
    if git diff --quiet "$base" "$head" -- "${LANE_PATHS[@]}"; then
      echo "ok   lane files (${LANE_PATHS[*]}) at job commit $head equal BASE $base"
    else
      echo "DIFF lane files changed between BASE and job commit:"; git diff --stat "$base" "$head" -- "${LANE_PATHS[@]}"; exit 1
    fi
    dir=$(fetch "$job")
    [ -f "$dir/summary/summary.json" ] || die "job $job has no summary.json"
    rc=0
    python3 -B - "$dir/summary/summary.json" "$head" "$base" "${BOUND_FILES[@]}" <<'PY' || rc=1
import hashlib, json, subprocess, sys
summary, head, base, paths = json.load(open(sys.argv[1])), sys.argv[2], sys.argv[3], sys.argv[4:]
bad = 0
if summary.get("head_sha") != head:
    print(f"DIFF summary head_sha {summary.get('head_sha')} != pipeline revision {head}"); bad += 1
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
    job=${1:-}; is_job "$job"; re=${2:-}; [ -n "$re" ] || die "regex required"
    max=${3:-60}; [[ "$max" =~ ^[0-9]+$ ]] && [ "$max" -le 200 ] || die "MAX must be <= 200"
    dir=$(fetch "$job"); [ -f "$dir/log/kani.log" ] || die "job $job has no kani.log"
    grep -n -E -m "$max" -- "$re" "$dir/log/kani.log" | cut -c1-400 || echo "(no match)" ;;
  log-lines)
    job=${1:-}; is_job "$job"; start=${2:-}; count=${3:-80}
    [[ "$start" =~ ^[0-9]+$ ]] || die "START must be a line number"
    [[ "$count" =~ ^[0-9]+$ ]] && [ "$count" -le 200 ] || die "N must be <= 200"
    dir=$(fetch "$job"); [ -f "$dir/log/kani.log" ] || die "job $job has no kani.log"
    sed -n "${start},$((start + count - 1))p" "$dir/log/kani.log" | cut -c1-400 ;;
  *)
    sed -n '5,11p' "$0"; exit 2 ;;
esac
