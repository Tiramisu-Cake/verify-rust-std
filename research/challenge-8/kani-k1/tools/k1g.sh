#!/usr/bin/env bash
# Agent helper for the Kani K-1 resource lane (32 GB) on Cloud Build, project smallsort-k1. Same verbs as
# k1.sh (CircleCI); runs are identified by Cloud Build build ids. gcloud runs with its own configuration
# directory and the dispatcher service account, so the machine's default gcloud setup is never touched.
# The account can submit builds to the pool and read the run bucket, nothing else.
#   k1g.sh dispatch BRANCH              start the lane on the pushed BRANCH, print the build id
#   k1g.sh wait BUILD                   block until the build ends (background task), print its status
#   k1g.sh watch BUILD                  Codex: detached wait, then one `codex queue` into $CODEX_THREAD_ID; end the turn
#   k1g.sh summary BUILD                download the summary, print summary.md
#   k1g.sh check-tooling BUILD BASE     lane files of the build's commit equal BASE; exit 1 otherwise
#   k1g.sh log-grep BUILD REGEX [MAX]   bounded grep of kani.log (MAX <= 200 matching lines)
#   k1g.sh log-lines BUILD START [N]    bounded slice of kani.log (N <= 200 lines)
#   k1g.sh peaks BUILD                  per-command memory peaks file of the run (small)
#   k1g.sh budget                       pool minutes used and reserved in the project, against the cap
#   k1g.sh build-tail BUILD [N]         coordinator only: last N <= 120 lines of the Cloud Build log, for setup failures
set -euo pipefail

PROJECT=${K1_GCP_PROJECT:-smallsort-k1}
REGION=us-central1
POOL=projects/$PROJECT/locations/$REGION/workerPools/k1-highmem4
BUCKET=$PROJECT-k1-runs
BUILD_SA=k1-build@$PROJECT.iam.gserviceaccount.com
DISP_SA=k1-dispatcher@$PROJECT.iam.gserviceaccount.com
KEY=${K1_GCP_KEY:-/root/.config/smallsort-ci/k1-gcp-key.json}
GCFG=${K1_GCLOUD_CONFIG:-/root/.config/smallsort-ci/k1-gcloud}
CACHE=${K1_CACHE:-${TMPDIR:-/tmp}/kani-k1-gcb}
# Paid pool time. The owner capped all 32 GB builds at $10 (2026-10-26); 370 min x $0.02612 = $9.66 leaves
# a margin for billing rounding. dispatch refuses a build whose timeout would take used + reserved minutes
# over CAP_MINUTES; raising it is the owner's decision.
CAP_MINUTES=370
PRICE_PER_MINUTE=0.02612            # e2-highmem-4 private pool, us-central1, USD
OVERHEAD_MINUTES=30                 # checkout, deps, Kani build, summary, upload; see gcb-k1.sh
LANE_PATHS=(.circleci .github/workflows research/challenge-8/kani-k1/tools research/challenge-8/kani-k1/gcb
            scripts/run-kani.sh tool_config/kani-version.toml rust-toolchain.toml .gitmodules .cargo library/.cargo
            library/Cargo.toml library/Cargo.lock)
BOUND_FILES=(research/challenge-8/kani-k1/gcb/cloudbuild.yaml research/challenge-8/kani-k1/tools/kani_k1.py
             research/challenge-8/kani-k1/tools/gcb-k1.sh scripts/run-kani.sh tool_config/kani-version.toml)
TOOLS=$(cd "$(dirname "$0")" && pwd)

die() { echo "k1g.sh: $*" >&2; exit 2; }
is_build() { [[ "$1" =~ ^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$ ]] || die "build id must be a UUID: $1"; }
[ -r "$KEY" ] || die "dispatcher key $KEY not readable"

G() { CLOUDSDK_CONFIG="$GCFG" gcloud --quiet --account="$DISP_SA" --project="$PROJECT" "$@"; }
auth() {
  if [ ! -d "$GCFG" ]; then (umask 077; mkdir -p "$GCFG"); fi
  if ! CLOUDSDK_CONFIG="$GCFG" gcloud auth list --filter="account:$DISP_SA" --format='value(account)' 2>/dev/null | grep -q .; then
    CLOUDSDK_CONFIG="$GCFG" gcloud auth activate-service-account "$DISP_SA" --key-file="$KEY" --quiet >/dev/null 2>&1 \
      || die "cannot activate $DISP_SA with $KEY"
  fi
}
jqr() { python3 -c "import json,sys; d=json.load(sys.stdin); print(eval(sys.argv[1], {'d': d}))" "$1"; }
describe() { G builds describe "$1" --region="$REGION" --format=json; }
TERMINAL=" SUCCESS FAILURE INTERNAL_ERROR TIMEOUT CANCELLED EXPIRED "

# budget: prints the ledger, sets USED and RESERVED (minutes). Finished builds count start..finish rounded
# up; queued or running ones count their full timeout.
ledger() {
  local out
  out=$(G builds list --region="$REGION" --limit=1000 --format=json | python3 -B "$TOOLS/kani_k1.py" ledger) \
    || die "cannot compute the pool-minute ledger"
  read -r BUILDS USED RESERVED <<< "$out"
  [ "$BUILDS" -lt 1000 ] || die "1000 or more builds listed: the ledger may undercount; owner decision needed"
}

fetch() {  # fetch BUILD -> directory with summary/ and log/; only for finished builds, whose uploads are final
  local id=$1 dir="$CACHE/$1" tmp status
  if [ ! -d "$dir" ]; then
    status=$(describe "$id" | jqr "d.get('status')")
    [[ "$TERMINAL" == *" $status "* ]] || die "build $id is not finished (status $status); wait for it first"
    mkdir -p "$CACHE"
    tmp=$(mktemp -d "$CACHE/.fetch.XXXXXX")
    if ! G storage ls "gs://$BUCKET/runs/$id/**" > "$tmp/index.txt" 2> "$tmp/ls.err"; then
      grep -q "matched no objects" "$tmp/ls.err" || { rm -rf "$tmp"; die "listing gs://$BUCKET/runs/$id failed: $(head -c 300 "$tmp/ls.err")"; }
    fi
    # Nothing uploaded: not cached, since a listing is final only once the upload step has run.
    [ -s "$tmp/index.txt" ] || { rm -rf "$tmp"; die "build $id uploaded nothing: treat as RUNNER_ERROR (setup failure, timeout or cancel)"; }
    while IFS= read -r url; do
      rel=${url#gs://$BUCKET/runs/$id/}
      [[ "$rel" =~ ^(summary|log)/[A-Za-z0-9._-]+$ ]] && [[ "$rel" != *..* ]] || continue
      mkdir -p "$tmp/$(dirname "$rel")"
      G storage cp "$url" "$tmp/$rel" >/dev/null 2>&1 || { rm -rf "$tmp"; die "download failed: $rel"; }
    done < "$tmp/index.txt"
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
    work=$(mktemp -d); trap 'rm -rf "$work"' EXIT
    git show "$sha:research/challenge-8/kani-k1/RUN-REQUEST.json" > "$work/request.json" 2>/dev/null || die "no RUN-REQUEST.json at $sha"
    git show "$sha:research/challenge-8/kani-k1/gcb/cloudbuild.yaml" > "$work/cloudbuild.yaml" 2>/dev/null || die "no gcb/cloudbuild.yaml at $sha"
    # Validate here with this checkout's kani_k1.py: a request the lane would reject must not cost pool time.
    python3 -B "$TOOLS/kani_k1.py" validate "$work/request.json" --args-out "$work/args" \
      --require-runner gcb-e2-highmem-4 --max-total-minutes 60 >/dev/null || die "request rejected (see above)"
    total=$(python3 -c 'import json,sys; r=json.load(open(sys.argv[1])); print(len(r["harnesses"]) * r["harness_timeout_minutes"])' "$work/request.json")
    timeout=$(( total + OVERHEAD_MINUTES ))
    auth
    # One dispatch at a time on this machine: the duplicate check, the ledger and the submit must not interleave.
    exec 9> "$GCFG/dispatch.lock"
    flock -w 300 9 || die "another k1g.sh dispatch holds $GCFG/dispatch.lock"
    dup=$(G builds list --region="$REGION" --limit=1000 --format='value(id)' --filter="substitutions._SHA=$sha")
    [ -z "$dup" ] || die "build(s) $(echo $dup) already ran $sha; change and push RUN-REQUEST.json for a new run"
    ledger
    if [ $(( USED + RESERVED + timeout )) -gt "$CAP_MINUTES" ]; then
      die "budget: used $USED + reserved $RESERVED + this build's timeout $timeout min > cap $CAP_MINUTES min; owner decision needed"
    fi
    id=$(G builds submit --no-source --async --config="$work/cloudbuild.yaml" --region="$REGION" --worker-pool="$POOL" \
           --service-account="projects/$PROJECT/serviceAccounts/$BUILD_SA" --gcs-log-dir="gs://$BUCKET/logs" \
           --timeout="${timeout}m" --substitutions="_SHA=$sha,_BRANCH=$branch,_BUCKET=$BUCKET" \
           --format='value(id)') || die "submit failed"
    is_build "$id"
    echo "budget after submit: used $USED + reserved $((RESERVED + timeout)) of $CAP_MINUTES min (~\$$(python3 -c "print(f'{($USED + $RESERVED + $timeout) * $PRICE_PER_MINUTE:.2f}')") at most)" >&2
    echo "$id" ;;
  wait)
    id=${1:-}; is_build "$id"; auth
    limit=$(describe "$id" | jqr "int(d.get('timeout', '5400s').rstrip('s'))")
    deadline=$(( $(date +%s) + limit + 30 * 60 ))
    while :; do
      status=$(describe "$id" 2>/dev/null | jqr "d.get('status')" 2>/dev/null || echo unknown)
      [[ "$TERMINAL" == *" $status "* ]] && break
      [ "$(date +%s)" -lt "$deadline" ] || die "build $id not finished $(( limit / 60 + 30 )) min after wait started (status $status)"
      sleep 60
    done
    echo "build $id status=$status" ;;
  watch)
    # A detached waiter without a model: when the build ends it queues a message into the calling Codex
    # thread (the delivery the SmallSort watcher uses, WAIT-EXPERIMENT.md) and exits. Unlike that watcher it
    # retries: up to 3 attempts 2 min apart until `codex queue` exits 0. A duplicate wakeup only makes the agent
    # re-read a summary; a lost one idles an unattended agent. Outcome in the watch log. No active Codex goal.
    id=${1:-}; is_build "$id"; auth
    thread=${CODEX_THREAD_ID:-}
    [[ "$thread" =~ ^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$ ]] || die "CODEX_THREAD_ID is not set: use a foreground wait"
    link=/root/.codex/app-server-control/app-server-control.sock   # the daemon republishes it on restart
    sock=$(readlink -f "$link" 2>/dev/null || true)
    [ -n "$sock" ] && [ -S "$sock" ] || die "no Codex app-server control socket: use a foreground wait"
    command -v codex >/dev/null || die "codex not on PATH: use a foreground wait"
    mkdir -p "$CACHE"; log="$CACHE/watch-$id.log"
    [ ! -e "$log" ] || die "build $id is already watched (log $log)"
    setsid nohup bash -c '
      "$1" wait "$2" > "$3" 2>&1; rc=$?
      msg="k1g watch: $(tail -n 1 "$3" | cut -c1-200) (wait exit $rc). Next: k1g.sh summary $2"
      for attempt in 1 2 3; do
        if timeout 60 codex queue --remote "unix://$(readlink -f "$4")" --thread "$5" --message "$msg (delivery attempt $attempt)" >> "$3" 2>&1; then
          echo "DELIVERED attempt $attempt" >> "$3"; exit 0
        fi
        echo "DELIVERY_FAILED_OR_UNKNOWN attempt $attempt" >> "$3"; [ "$attempt" = 3 ] || sleep 120
      done
    ' k1g-watch "$TOOLS/k1g.sh" "$id" "$log" "$link" "$thread" < /dev/null > /dev/null 2>&1 &
    echo "watching build $id for thread $thread (log $log). End the turn now; a queued message will wake it." ;;
  summary)
    id=${1:-}; is_build "$id"; auth
    dir=$(fetch "$id")
    if [ -f "$dir/log/stage-error.txt" ]; then
      echo "--- first failed stage, last lines (setup diagnostics, not Kani output):" >&2
      head -n 41 "$dir/log/stage-error.txt" | cut -c1-300 >&2
    fi
    [ -f "$dir/summary/summary.md" ] || die "build $id has no summary: treat as RUNNER_ERROR (timeout, cancel or setup failure)"
    cat "$dir/summary/summary.md" ;;
  peaks)
    id=${1:-}; is_build "$id"; auth
    dir=$(fetch "$id")
    [ -f "$dir/log/peaks.txt" ] || die "build $id has no peaks.txt"
    head -c 8000 "$dir/log/peaks.txt"; [ -f "$dir/log/machine.txt" ] && cat "$dir/log/machine.txt" ;;
  check-tooling)
    # The commit comes from the Cloud Build record (substitution _SHA), the lane files are compared with
    # BASE by local git, and the summary must bind exactly BOUND_FILES.
    id=${1:-}; is_build "$id"; base=${2:-}; [[ "$base" =~ ^[0-9a-f]{40}$ ]] || die "full 40-hex BASE commit required"
    auth
    head=$(describe "$id" | jqr "(d.get('substitutions') or {}).get('_SHA', '')")
    [[ "$head" =~ ^[0-9a-f]{40}$ ]] || die "cannot read the commit of build $id"
    git cat-file -e "$head^{commit}" 2>/dev/null || git fetch -q origin "$head" || die "commit $head not available locally"
    git cat-file -e "$base^{commit}" 2>/dev/null || die "BASE $base not available locally"
    pool=$(describe "$id" | jqr "((d.get('options') or {}).get('pool') or {}).get('name', '')")
    if [ "$pool" = "$POOL" ]; then echo "ok   build ran in pool $pool"; else echo "DIFF build pool '$pool' != $POOL"; exit 1; fi
    if git diff --quiet "$base" "$head" -- "${LANE_PATHS[@]}"; then
      echo "ok   lane files (${LANE_PATHS[*]}) at build commit $head equal BASE $base"
    else
      echo "DIFF lane files changed between BASE and build commit:"; git diff --stat "$base" "$head" -- "${LANE_PATHS[@]}"; exit 1
    fi
    dir=$(fetch "$id")
    [ -f "$dir/summary/summary.json" ] || die "build $id has no summary.json"
    rc=0
    python3 -B - "$dir/summary/summary.json" "$head" "$base" "$id" "${BOUND_FILES[@]}" <<'PY' || rc=1
import hashlib, json, subprocess, sys
summary, head, base, build, paths = json.load(open(sys.argv[1])), sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5:]
bad = 0
if summary.get("head_sha") != head:
    print(f"DIFF summary head_sha {summary.get('head_sha')} != build commit {head}"); bad += 1
if (summary.get("run") or {}).get("id") != build:
    print(f"DIFF summary run id {(summary.get('run') or {}).get('id')} != build {build}"); bad += 1
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
    id=${1:-}; is_build "$id"; re=${2:-}; [ -n "$re" ] || die "regex required"
    max=${3:-60}; [[ "$max" =~ ^[0-9]+$ ]] && [ "$max" -le 200 ] || die "MAX must be <= 200"
    auth; dir=$(fetch "$id"); [ -f "$dir/log/kani.log" ] || die "build $id has no kani.log"
    grep -n -E -m "$max" -- "$re" "$dir/log/kani.log" | cut -c1-400 || echo "(no match)" ;;
  log-lines)
    id=${1:-}; is_build "$id"; start=${2:-}; count=${3:-80}
    [[ "$start" =~ ^[0-9]+$ ]] || die "START must be a line number"
    [[ "$count" =~ ^[0-9]+$ ]] && [ "$count" -le 200 ] || die "N must be <= 200"
    auth; dir=$(fetch "$id"); [ -f "$dir/log/kani.log" ] || die "build $id has no kani.log"
    sed -n "${start},$((start + count - 1))p" "$dir/log/kani.log" | cut -c1-400 ;;
  budget)
    auth; ledger
    echo "builds $BUILDS; pool minutes used $USED, reserved by unfinished builds $RESERVED, cap $CAP_MINUTES"
    python3 -c "print(f'at most ~\${($USED + $RESERVED) * $PRICE_PER_MINUTE:.2f} of ~\${$CAP_MINUTES * $PRICE_PER_MINUTE:.2f}')" ;;
  build-tail)
    id=${1:-}; is_build "$id"; n=${2:-60}; [[ "$n" =~ ^[0-9]+$ ]] && [ "$n" -le 120 ] || die "N must be <= 120"
    auth; G storage cat "gs://$BUCKET/logs/log-$id.txt" | tail -n "$n" | cut -c1-300 ;;
  *)
    sed -n '5,16p' "$0"; exit 2 ;;
esac
