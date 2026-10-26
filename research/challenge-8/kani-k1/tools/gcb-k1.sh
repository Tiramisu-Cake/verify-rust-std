#!/usr/bin/env bash
# Cloud Build stages of the Kani K-1 resource lane (32 GB, called from gcb/cloudbuild.yaml). Cloud Build
# steps share only /workspace, so deps, Kani build and verification run in one container: `all` runs every
# stage, records each outcome in k1-out/, always summarizes, stages the upload and writes the gate verdict
# to k1-out/gate.rc. It exits 0 itself, so that the upload step always runs; the gate step exits with gate.rc.
# No memory cap: the point of this lane is how much memory each tool needs. kani_k1.py sample-mem records
# per-command peaks instead.
#   all | validate | deps | build | verify | summarize | gate
set -euo pipefail

K1_TOOLS=research/challenge-8/kani-k1/tools
K1_REQUEST=research/challenge-8/kani-k1/RUN-REQUEST.json
K1_OUT=k1-out
LANE_RUNNER=gcb-e2-highmem-4
# Requests are capped at 720 harness-minutes (kani_k1.py; extended layer, owner decision 2026-10-26). k1g.sh sets the paid build timeout to the
# request's harness total + 30 min; verify is cut at total + 24 min after validation (compilation and goto
# instrumentation are outside Kani's per-harness timeout), leaving time for summary and upload.
MAX_TOTAL_MINUTES=720
VERIFY_SLACK_MINUTES=24
mkdir -p "$K1_OUT"
# Cloud Build sets HOME=/builder/home while the step runs as root, and rustup refuses a HOME that differs
# from root's home directory.
export HOME=/root
export PATH="$HOME/.cargo/bin:$PATH" DEBIAN_FRONTEND=noninteractive

kani_commit() { grep '^commit *=' tool_config/kani-version.toml | sed 's/^commit *= *"\(.*\)"/\1/'; }
valid() { [ -f "$K1_OUT/valid" ]; }
total_minutes() { python3 -B -c 'import json,sys; r=json.load(open(sys.argv[1])); print(len(r["harnesses"]) * r["harness_timeout_minutes"])' "$K1_REQUEST"; }

stage() {
  case "$1" in
    validate)
      date +%s > "$K1_OUT/start"
      touch "$K1_OUT/validated"
      # ubuntu:24.04 has neither python3 nor git; install the minimum to validate, the rest comes in deps.
      apt-get update -qq && apt-get install -y -qq --no-install-recommends python3 git >/dev/null
      if [[ "${K1_BRANCH:-}" != experiment/kani-k1-* ]]; then
        echo "lane runs only on experiment/kani-k1-* branches, not '${K1_BRANCH:-}'" > "$K1_OUT/request-error.txt"
      elif [ "$(git rev-parse HEAD)" != "${K1_SHA:-}" ]; then
        echo "checkout $(git rev-parse HEAD) differs from requested ${K1_SHA:-}" > "$K1_OUT/request-error.txt"
      elif python3 -B "$K1_TOOLS/kani_k1.py" validate "$K1_REQUEST" --args-out "$K1_OUT/kani-args.txt" \
             --max-total-minutes "$MAX_TOTAL_MINUTES" --require-runner "$LANE_RUNNER" 2> "$K1_OUT/request-error.txt"; then
        touch "$K1_OUT/valid"
      fi
      cat "$K1_OUT/request-error.txt" >&2 || true ;;

    deps)
      valid || return 0
      rm -f "$K1_OUT/deps.ok"
      # The container lacks what GitHub/CircleCI images preinstall. sudo: Kani's install_deps.sh calls it;
      # lsb-release: install_cbmc.sh picks the CBMC .deb by `lsb_release -rs`; bash-completion: a Depends of
      # that .deb, installed with plain dpkg -i; time/procps: measurements.
      apt-get install -y -qq --no-install-recommends sudo ca-certificates curl git jq time procps unzip \
        build-essential python3 lsb-release bash-completion pkg-config libssl-dev xz-utils file >/dev/null
      if ! command -v rustup >/dev/null; then
        curl -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal --default-toolchain none
      fi
      df -h / | tail -1
      touch "$K1_OUT/deps.ok" ;;

    build)
      valid && [ -f "$K1_OUT/deps.ok" ] || return 0
      commit=$(kani_commit); test -n "$commit"
      rm -f "$K1_OUT/build.ok"
      rm -rf kani_build && mkdir kani_build
      git -C kani_build init -q .
      git -C kani_build remote add origin https://github.com/model-checking/kani.git
      git -C kani_build fetch --depth 1 origin "$commit" --quiet
      git -C kani_build checkout "$commit" --quiet
      (cd kani_build && GIT_LFS_SKIP_SMUDGE=1 git submodule update --init --recursive --depth 1 --quiet)
      (cd kani_build && source kani-dependencies && ./scripts/setup/ubuntu/install_deps.sh)
      (cd kani_build && rustup toolchain install)
      (cd kani_build && cargo build-dev --release)
      test "$(git -C kani_build rev-parse HEAD)" = "$commit"
      kani_build/scripts/kani --version
      touch "$K1_OUT/build.ok" ;;

    verify)
      valid && [ -f "$K1_OUT/build.ok" ] || return 0
      args=()
      while IFS= read -r line; do [ -n "$line" ] && args+=("$line"); done < "$K1_OUT/kani-args.txt"
      remaining=$(( $(cat "$K1_OUT/start") + ($(total_minutes) + VERIFY_SLACK_MINUTES) * 60 - $(date +%s) ))
      if [ "$remaining" -le 120 ]; then
        echo "no time left before the build timeout; verification not started" | tee "$K1_OUT/verify-skipped"
        return 0
      fi
      { free -b | awk '/^Mem:/{print "mem_total_bytes=" $2} /^Swap:/{print "swap_total_bytes=" $2}'
        echo "verify_start_after_validate_s=$(( $(date +%s) - $(cat "$K1_OUT/start") ))"
        echo "verify_budget_s=$remaining"; } | tee "$K1_OUT/machine.txt"
      python3 -B "$K1_TOOLS/kani_k1.py" sample-mem --out "$K1_OUT/peaks.txt" --interval 2 &
      sampler=$!
      set +e
      # Same shape as the CircleCI lane: GNU time -v on stderr (time.txt), Kani output through tee; a run cut
      # by timeout is PARTIAL.
      timeout --kill-after=30 "$remaining" /usr/bin/time -v bash -c 'set -o pipefail; scripts/run-kani.sh --path "$PWD" --kani-args "$@" 2>&1 | tee "k1-out/kani.log"' k1 "${args[@]}" 2> "$K1_OUT/time.txt"
      echo $? > "$K1_OUT/rc"
      kill -TERM "$sampler" 2>/dev/null; wait "$sampler"
      set -e ;;

    summarize)
      req_err=""
      if [ -f "$K1_OUT/validated" ] && ! valid; then
        req_err=$(head -c 300 "$K1_OUT/request-error.txt" 2>/dev/null || true)
        [ -n "$req_err" ] || req_err="request rejected before Kani ran"
      fi
      if [ ! -f "$K1_OUT/validated" ]; then build_outcome=not-started
      elif ! valid; then build_outcome=skipped
      elif [ ! -f "$K1_OUT/deps.ok" ]; then build_outcome=deps-failure
      elif [ -f "$K1_OUT/verify-skipped" ]; then build_outcome=verify-skipped
      elif [ -f "$K1_OUT/build.ok" ]; then build_outcome=success
      else build_outcome=failure; fi
      log_args=(); peaks_args=()
      [ -f "$K1_OUT/kani.log" ] && log_args=(--log "$K1_OUT/kani.log")
      [ -f "$K1_OUT/build.ok" ] && valid && peaks_args=(--peaks "$K1_OUT/peaks.txt")
      os=$(. /etc/os-release && echo "$PRETTY_NAME")
      mem=$(free -b 2>/dev/null | awk '/^Mem:/{printf "%.1f GiB", $2 / 2^30}' || true)
      hw="$(nproc) CPU $(sed -n 's/^model name\t*: *//p' /proc/cpuinfo | head -1), ${mem:-? GiB} (container view; pool per Cloud Build record)"
      python3 -B "$K1_TOOLS/kani_k1.py" summarize --request "$K1_REQUEST" "${log_args[@]}" "${peaks_args[@]}" \
        --time "$K1_OUT/time.txt" --exit-code "$(cat "$K1_OUT/rc" 2>/dev/null || true)" \
        --head-sha "$(git rev-parse HEAD)" --kani-commit "$(kani_commit || true)" --request-error "$req_err" \
        --build-outcome "$build_outcome" --run-id "${K1_BUILD_ID:-}" --run-attempt "" \
        --image-os "$os" --image-version "$hw" \
        --bind research/challenge-8/kani-k1/gcb/cloudbuild.yaml --bind "$K1_TOOLS/kani_k1.py" \
        --bind "$K1_TOOLS/gcb-k1.sh" --bind scripts/run-kani.sh --bind tool_config/kani-version.toml \
        --out-dir "$K1_OUT/summary"
      cat "$K1_OUT/summary/summary.md" ;;

    gate)
      python3 -B "$K1_TOOLS/kani_k1.py" gate "$K1_OUT/summary/summary.json" ;;

    *)
      echo "usage: gcb-k1.sh all|validate|deps|build|verify|summarize|gate" >&2; return 2 ;;
  esac
}

if [ "${1:-}" != all ]; then stage "${1:-}"; exit; fi

# `all`: each stage runs as its own bash process. A subshell would not do: errexit is ignored in anything
# on the left of `||`, so a failed command would not stop its stage before the stage's ok marker.
# A failed stage leaves the last 40 lines of its output in stage-error.txt (uploaded; k1g.sh summary shows it).
for s in validate deps build verify summarize; do
  echo "== stage $s"
  if ! bash "$0" "$s" 2>&1 | tee "$K1_OUT/stage-$s.log"; then
    echo "stage $s failed with exit ${PIPESTATUS[0]}"
    [ -f "$K1_OUT/stage-error.txt" ] || { echo "stage $s:"; tail -n 40 "$K1_OUT/stage-$s.log" | cut -c1-300; } > "$K1_OUT/stage-error.txt"
  fi
done
rc=1
if [ -f "$K1_OUT/summary/summary.json" ]; then
  bash "$0" gate && rc=0 || rc=$?
fi
echo "$rc" > "$K1_OUT/gate.rc"
# Upload set: the same paths the CircleCI lane publishes, plus the memory peaks and machine view.
rm -rf "$K1_OUT/upload" && mkdir -p "$K1_OUT/upload/summary" "$K1_OUT/upload/log"
cp "$K1_OUT"/summary/summary.{md,json} "$K1_OUT/upload/summary/" 2>/dev/null || true
for f in kani.log time.txt request-error.txt peaks.txt machine.txt stage-error.txt; do
  [ -f "$K1_OUT/$f" ] && cp "$K1_OUT/$f" "$K1_OUT/upload/log/$f"
done
touch "$K1_OUT/upload/summary/.staged" "$K1_OUT/upload/log/.staged"   # both directories exist for the upload step
exit 0
