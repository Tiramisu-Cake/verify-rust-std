#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0 OR MIT
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

target=library/core/src/slice/sort/shared/smallsort.rs
controls=research/challenge-8/ub-controls.rs
classifier=research/challenge-8/classify-ub-controls.py
budget=${1:-90}
profile=${2:-all}
case "$budget" in
    30|60|90|120) ;;
    *) echo 'Budget must be 30, 60, 90 or 120 minutes' >&2; exit 2 ;;
esac
case "$profile" in
    all)
        selected_controls=(
            positive_initialized_read
            positive_valid_bool_pointer_read
            negative_uninitialized_i32_read
            negative_invalid_bool_read
            negative_misaligned_u32_read
            negative_null_u32_read
            negative_immutable_static_write
        )
        ;;
    immutable_observation)
        selected_controls=(
            positive_initialized_read
            positive_valid_bool_pointer_read
            negative_immutable_static_write_observed
        )
        ;;
    *) echo 'Profile must be all or immutable_observation' >&2; exit 2 ;;
esac

if [[ "${GITHUB_ACTIONS:-}" != true || "${RUNNER_OS:-}" != Linux || "${RUNNER_ENVIRONMENT:-}" != github-hosted ]]; then
    echo 'UB controls require a GitHub-hosted Linux Actions runner' >&2
    exit 2
fi
if ! git diff --quiet HEAD -- "$target" "$controls" "$classifier"; then
    echo 'Target source and UB control inputs must match the checked-out commit' >&2
    exit 2
fi
if rg -q 'pub mod challenge8_ub_controls' "$target"; then
    echo 'UB-control module already present; use a clean checkout' >&2
    exit 2
fi

mkdir -p research-results
if [[ -e research-results/ub-controls-summary.json ]]; then
    echo 'UB-control evidence already exists; use a clean checkout' >&2
    exit 2
fi
started_epoch=$(date +%s)
cat > research-results/ub-controls-environment.txt <<EOF
Source commit: $(git rev-parse HEAD)
Selection: ${PROOF_SELECTION:-ub_detector_controls}
Profile: ${profile}
Budget including cold build and selected controls: ${budget} minutes
Runner OS: ${RUNNER_OS}
Runner environment: ${RUNNER_ENVIRONMENT}
Kani pin:
$(cat tool_config/kani-version.toml)
EOF
uname -a >> research-results/ub-controls-environment.txt
sha256sum "$target" "$controls" "$classifier" tool_config/kani-version.toml >> research-results/ub-controls-environment.txt
sha256sum research/challenge-8/run-ub-controls.sh scripts/run-kani.sh >> research-results/ub-controls-environment.txt
git hash-object "$target" >> research-results/ub-controls-environment.txt
git rev-parse "HEAD:$target" >> research-results/ub-controls-environment.txt
printf 'Flags: -Z uninit-checks -Z valid-value-checks --extra-pointer-checks; scripts/run-kani.sh adds -Z unstable-options and its standard args.\n' >> research-results/ub-controls-environment.txt

cat "$controls" >> "$target"
cp "$target" research-results/smallsort-with-ub-controls.rs

finalize_evidence() {
    local status="$1"
    local write_summary="${2:-yes}"
    local -a records=()
    local name
    for name in "${selected_controls[@]}"; do
        [[ -f "research-results/ub-${name}.json" ]] && records+=("research-results/ub-${name}.json")
    done
    if [[ "$write_summary" == yes ]]; then
        python3 "$classifier" --aggregate --profile "$profile" --out research-results/ub-controls-summary.json "${records[@]}" || true
    fi
    printf '%s\n' "$status" > research-results/ub-controls-exit-code.txt
    if [[ -x kani_build/scripts/kani ]]; then
        kani_build/scripts/kani --version >> research-results/ub-controls-environment.txt 2>&1 || true
    fi
    if command -v cbmc >/dev/null; then
        cbmc --version >> research-results/ub-controls-environment.txt 2>&1 || true
    fi
    printf 'Elapsed suite seconds: %s\n' "$(( $(date +%s) - started_epoch ))" >> research-results/ub-controls-environment.txt
}

run_one() {
    local name="$1"
    local expected="$2"
    local log="research-results/ub-${name}.log"
    local json="research-results/ub-${name}.json"
    local exit_file="research-results/ub-${name}-exit-code.txt"
    local now remaining code classify_code
    now=$(date +%s)
    remaining=$(( budget * 60 - (now - started_epoch) ))
    if (( remaining <= 0 )); then
        echo 'Suite verification budget exhausted before next control' >&2
        return 124
    fi

    printf '\nRunning UB control: %s (%s)\n' "$name" "$expected"
    if /usr/bin/time -v -o "research-results/ub-${name}-resources.txt" \
        timeout --signal=TERM --kill-after=30s "${remaining}s" \
        bash scripts/run-kani.sh --path . --kani-args \
        --harness "slice::sort::shared::smallsort::challenge8_ub_controls::$name" \
        --exact --jobs 1 -Z uninit-checks -Z valid-value-checks --extra-pointer-checks \
        2>&1 | tee "$log"; then
        code=0
    else
        code=${PIPESTATUS[0]}
    fi
    printf '%s\n' "$code" > "$exit_file"

    if python3 "$classifier" --control "$name" --exit-code "$code" --log "$log" --out "$json"; then
        classify_code=0
    else
        classify_code=$?
    fi
    if [[ "$code" -eq 124 ]]; then
        return 124
    fi
    if [[ "$expected" == positive && "$classify_code" -ne 0 ]]; then
        echo "Positive control $name failed classification; stopping before negative controls." >&2
        return 1
    fi
    return 0
}

if run_one positive_initialized_read positive; then result=0; else result=$?; fi
if (( result != 0 )); then
    finalize_evidence "$result"
    exit "$result"
fi
if run_one positive_valid_bool_pointer_read positive; then result=0; else result=$?; fi
if (( result != 0 )); then
    finalize_evidence "$result"
    exit "$result"
fi

if [[ "$profile" == immutable_observation ]]; then
    negative_controls=(negative_immutable_static_write_observed)
else
    negative_controls=(
        negative_uninitialized_i32_read
        negative_invalid_bool_read
        negative_misaligned_u32_read
        negative_null_u32_read
        negative_immutable_static_write
    )
fi
for name in "${negative_controls[@]}"; do
    if run_one "$name" negative; then result=0; else result=$?; fi
    if (( result == 124 )); then
        finalize_evidence 124
        exit 124
    fi
done

set +e
aggregate_records=()
for name in "${selected_controls[@]}"; do
    aggregate_records+=("research-results/ub-${name}.json")
done
python3 "$classifier" --aggregate --profile "$profile" --out research-results/ub-controls-summary.json \
    "${aggregate_records[@]}"
suite_status=$?
set -e
finalize_evidence "$suite_status" no

if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
    {
        printf '### Kani UB detector controls\n\n'
        printf 'Profile: `%s`; suite classification exit code: `%s`.\n\n' "$profile" "$suite_status"
        printf 'This result measures detector controls only; it is not a SmallSort proof. See `research-results/ub-controls-summary.json` for each property, diagnostic, cover count, and reason.\n'
    } >> "$GITHUB_STEP_SUMMARY"
fi
exit "$suite_status"
