#!/usr/bin/env bash
# CircleCI stages of the Kani K-1 lane (called from .circleci/config.yml). Each stage records its
# outcome in k1-out/ so that the summary always names what happened; only `build` and `gate` exit
# non-zero (build: so that a failed Kani build is never cached; gate: the job verdict).
#   validate | deps | build | verify | summarize | gate
set -euo pipefail

K1_TOOLS=research/challenge-8/kani-k1/tools
K1_REQUEST=research/challenge-8/kani-k1/RUN-REQUEST.json
K1_OUT=k1-out
# The free plan stops a job after 60 min and then uploads nothing. Harness budget per request is 40 min;
# the verify step is additionally cut at 53 min after validation so that summary and artifacts survive.
MAX_TOTAL_MINUTES=40
VERIFY_DEADLINE_MINUTES=53
LANE_RUNNER=circleci-linux-large
# Verification runs in a cgroup capped below the VM's 15 GB: an OOM then kills CBMC inside the cgroup
# (Kani reports "CBMC appears to have run out of memory") instead of the whole VM, whose job ends as
# infrastructure_fail with no artifacts. The organizers' ubuntu-latest runner has 16 GB.
MEMCAP_BYTES=$((13 * 1024 * 1024 * 1024))
CG=/sys/fs/cgroup/k1-verify
mkdir -p "$K1_OUT"

kani_commit() { grep '^commit *=' tool_config/kani-version.toml | sed 's/^commit *= *"\(.*\)"/\1/'; }
valid() { [ -f "$K1_OUT/valid" ]; }

# Moves this shell (and so everything verify starts) into $CG; records ENFORCED or UNAVAILABLE with a reason.
memcap_enter() {
  local why=""
  if [ ! -f /sys/fs/cgroup/cgroup.controllers ]; then why="cgroup v2 is not mounted at /sys/fs/cgroup"
  elif ! grep -qw memory /sys/fs/cgroup/cgroup.controllers; then why="the memory controller is not available"
  elif ! { grep -qw memory /sys/fs/cgroup/cgroup.subtree_control \
           || echo +memory | sudo tee /sys/fs/cgroup/cgroup.subtree_control >/dev/null; }; then why="cannot enable the memory controller"
  elif ! { sudo mkdir -p "$CG" && echo "$MEMCAP_BYTES" | sudo tee "$CG/memory.max" >/dev/null; }; then why="cannot create $CG"
  elif [ -f "$CG/memory.swap.max" ] && ! echo 0 | sudo tee "$CG/memory.swap.max" >/dev/null; then why="cannot disable swap in $CG"
  elif ! echo $$ | sudo tee "$CG/cgroup.procs" >/dev/null; then why="cannot move the verify shell into $CG"
  elif ! grep -qx '0::/k1-verify' /proc/$$/cgroup; then why="the verify shell is not in $CG after the move"
  fi
  if [ -n "$why" ]; then
    printf 'state=UNAVAILABLE\nreason=%s\n' "$why" > "$K1_OUT/memcap.txt"
  else
    local swap=on
    if [ "$(cat "$CG/memory.swap.max" 2>/dev/null)" = 0 ] || ! awk '$1 == "SwapTotal:" && $2 > 0 {f = 1} END {exit !f}' /proc/meminfo; then
      swap=off
    fi
    printf 'state=ENFORCED\nmax_bytes=%s\nswap=%s\n' "$(cat "$CG/memory.max")" "$swap" > "$K1_OUT/memcap.txt"
  fi
  cat "$K1_OUT/memcap.txt"
}

memcap_record() {
  grep -q '^state=ENFORCED' "$K1_OUT/memcap.txt" || return 0
  { echo "peak_bytes=$(cat "$CG/memory.peak" 2>/dev/null || true)"
    echo "oom_kill=$(awk '$1 == "oom_kill" {print $2}' "$CG/memory.events" 2>/dev/null || true)"; } >> "$K1_OUT/memcap.txt"
  cat "$K1_OUT/memcap.txt"
}

case "${1:-}" in
  validate)
    date +%s > "$K1_OUT/start"
    touch "$K1_OUT/validated"
    if [[ "${CIRCLE_BRANCH:-}" != experiment/kani-k1-* ]]; then
      echo "lane runs only on experiment/kani-k1-* branches, not '${CIRCLE_BRANCH:-}'" > "$K1_OUT/request-error.txt"
    elif python3 -B "$K1_TOOLS/kani_k1.py" validate "$K1_REQUEST" --args-out "$K1_OUT/kani-args.txt" \
           --max-total-minutes "$MAX_TOTAL_MINUTES" --require-runner "$LANE_RUNNER" 2> "$K1_OUT/request-error.txt"; then
      touch "$K1_OUT/valid"
    fi
    cat "$K1_OUT/request-error.txt" >&2 || true ;;

  deps)
    valid || exit 0
    rm -f "$K1_OUT/deps.ok"
    sudo apt-get update -qq
    sudo apt-get install -y -qq jq time >/dev/null
    if ! command -v rustup >/dev/null && [ ! -x "$HOME/.cargo/bin/rustup" ]; then
      curl -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal --default-toolchain none
    fi
    echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> "$BASH_ENV"
    df -h / | tail -1
    touch "$K1_OUT/deps.ok" ;;

  build)
    # Non-zero when skipped too: save_cache runs only after success, and an entry saved without a
    # Kani build would occupy the cache key for good.
    valid || { echo "request invalid: Kani build skipped"; exit 1; }
    commit=$(kani_commit); test -n "$commit"
    rm -f "$K1_OUT/build.ok"
    if [ -d kani_build/.git ] && [ "$(git -C kani_build rev-parse HEAD 2>/dev/null)" = "$commit" ] \
       && [ -x kani_build/scripts/kani ] && [ -d kani_build/target/kani/bin ]; then
      echo "restored Kani build at $commit"
      cached=1
    else
      rm -rf kani_build && mkdir kani_build
      git -C kani_build init -q .
      git -C kani_build remote add origin https://github.com/model-checking/kani.git
      git -C kani_build fetch --depth 1 origin "$commit" --quiet
      git -C kani_build checkout "$commit" --quiet
      (cd kani_build && GIT_LFS_SKIP_SMUDGE=1 git submodule update --init --recursive --depth 1 --quiet)
      cached=0
    fi
    # CBMC/kissat live outside the cache, so install them on every run (same script as run-kani.sh).
    (cd kani_build && source kani-dependencies && ./scripts/setup/ubuntu/install_deps.sh)
    (cd kani_build && rustup toolchain install)
    if [ "$cached" = 0 ]; then (cd kani_build && cargo build-dev --release); fi
    test "$(git -C kani_build rev-parse HEAD)" = "$commit"
    kani_build/scripts/kani --version
    touch "$K1_OUT/build.ok" ;;

  verify)
    valid && [ -f "$K1_OUT/build.ok" ] || exit 0
    args=()
    while IFS= read -r line; do [ -n "$line" ] && args+=("$line"); done < "$K1_OUT/kani-args.txt"
    remaining=$(( $(cat "$K1_OUT/start") + VERIFY_DEADLINE_MINUTES * 60 - $(date +%s) ))
    if [ "$remaining" -le 120 ]; then
      echo "no time left before the 60-minute job cap; verification not started" | tee "$K1_OUT/verify-skipped"
      exit 0
    fi
    memcap_enter
    set +e
    # GNU time -v reports on stderr (to time.txt); Kani output goes through tee; time exits with the
    # inner pipeline status (pipefail). timeout keeps the job inside its cap; a cut run is PARTIAL.
    timeout --kill-after=30 "$remaining" /usr/bin/time -v bash -c 'set -o pipefail; scripts/run-kani.sh --path "$PWD" --kani-args "$@" 2>&1 | tee "k1-out/kani.log"' k1 "${args[@]}" 2> "$K1_OUT/time.txt"
    echo $? > "$K1_OUT/rc"
    memcap_record
    set -e ;;

  summarize)
    req_err=""
    if [ -f "$K1_OUT/validated" ] && ! valid; then
      req_err=$(head -c 300 "$K1_OUT/request-error.txt" 2>/dev/null || true)
      [ -n "$req_err" ] || req_err="request rejected before Kani ran"
    fi
    if [ ! -f "$K1_OUT/validated" ]; then build_outcome=not-started          # checkout/submodule failure
    elif ! valid; then build_outcome=skipped
    elif [ ! -f "$K1_OUT/deps.ok" ]; then build_outcome=deps-failure
    elif [ -f "$K1_OUT/verify-skipped" ]; then build_outcome=verify-skipped
    elif [ -f "$K1_OUT/build.ok" ]; then build_outcome=success
    else build_outcome=failure; fi
    log_args=()
    [ -f "$K1_OUT/kani.log" ] && log_args=(--log "$K1_OUT/kani.log")
    os=$(. /etc/os-release && echo "$PRETTY_NAME")
    hw="$(nproc) CPU $(lscpu | sed -n 's/^Model name: *//p' | head -1), $(free -g | awk '/^Mem:/{print $2}') GiB"
    python3 -B "$K1_TOOLS/kani_k1.py" summarize --request "$K1_REQUEST" "${log_args[@]}" \
      --time "$K1_OUT/time.txt" --exit-code "$(cat "$K1_OUT/rc" 2>/dev/null || true)" \
      --head-sha "${CIRCLE_SHA1:-}" --kani-commit "$(kani_commit || true)" --request-error "$req_err" \
      --build-outcome "$build_outcome" --memcap "$K1_OUT/memcap.txt" --run-id "${CIRCLE_BUILD_NUM:-}" --run-attempt "" \
      --image-os "$os" --image-version "$hw" \
      --bind .circleci/config.yml --bind "$K1_TOOLS/kani_k1.py" --bind "$K1_TOOLS/circleci-k1.sh" \
      --bind scripts/run-kani.sh --bind tool_config/kani-version.toml \
      --out-dir "$K1_OUT/summary"
    cat "$K1_OUT/summary/summary.md" ;;

  gate)
    python3 -B "$K1_TOOLS/kani_k1.py" gate "$K1_OUT/summary/summary.json" ;;

  *)
    echo "usage: circleci-k1.sh validate|deps|build|verify|summarize|gate" >&2; exit 2 ;;
esac
