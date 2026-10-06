#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0 OR MIT
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

target=library/core/src/slice/sort/shared/smallsort.rs
harness=research/challenge-8/insertion-safety-4.rs
budget=${1:-90}
mode=${2:-}
case "$budget" in
    30|60|90|120) ;;
    *) echo 'Budget must be 30, 60, 90 or 120 minutes' >&2; exit 2 ;;
esac

if [[ "${GITHUB_ACTIONS:-}" != true || "${RUNNER_OS:-}" != Linux || "${RUNNER_ENVIRONMENT:-}" != github-hosted ]]; then
    echo 'Insertion UB safety proof requires a GitHub-hosted Linux Actions runner' >&2
    exit 2
fi
if ! git diff --quiet HEAD -- "$target" "$harness"; then
    echo 'Standard-library source and insertion harness must match the checked-out commit' >&2
    exit 2
fi
if ! rg -q 'pub fn prove_outer_safety_4' "$harness" || \
    ! rg -q '#\[kani::unwind\(6\)\]' "$harness" || \
    rg -q 'loop_invariant|kani::stub_verified|kani::proof_for_contract|kani::(requires|ensures)' "$harness" || \
    [[ "$(rg -c 'kani::assume\(' "$harness")" != 2 ]] || \
    ! rg -Fq 'kani::assume(len >= 1 && len <= N);' "$harness" || \
    ! rg -Fq 'kani::assume(offset >= 1 && offset <= len);' "$harness" || \
    rg -q 'kani::assume\([^)]*(sorted|order)|assert!\([^)]*(sorted|order)' "$harness"; then
    echo 'Insertion UB harness must retain only the valid-slice length/offset preconditions' >&2
    exit 2
fi
if rg -q 'pub mod challenge8_insertion_safety|pub mod challenge8_ub_controls' "$target"; then
    echo 'Research module already injected; use a clean checkout' >&2
    exit 2
fi

mkdir -p research-results
if [[ -e research-results/insertion-ub-safety-summary.json ]]; then
    echo 'Insertion UB evidence already exists; use a clean checkout' >&2
    exit 2
fi

if [[ "$mode" != --inside ]]; then
    set +e
    /usr/bin/time -v -o research-results/insertion-ub-safety-resources.txt \
        timeout --signal=TERM --kill-after=30s "${budget}m" \
        bash "$0" "$budget" --inside 2>&1 | tee research-results/insertion-ub-safety-verification.log
    status=${PIPESTATUS[0]}
    set -e
    printf '%s\n' "$status" > research-results/insertion-ub-safety-exit-code.txt
    exit "$status"
fi

cat > research-results/insertion-ub-safety-environment.txt <<EOF
Source commit: $(git rev-parse HEAD)
Selection: insertion_ub_safety_4
Budget including cold build, compilation, and verification: ${budget} minutes
Runner OS: ${RUNNER_OS}
Runner environment: ${RUNNER_ENVIRONMENT}
Kani pin:
$(cat tool_config/kani-version.toml)
Harness assumptions: len in 1..=4 and offset in 1..=len only; no ordering precondition.
EOF
uname -a >> research-results/insertion-ub-safety-environment.txt
sha256sum "$target" "$harness" tool_config/kani-version.toml research/challenge-8/run-insertion-ub.sh scripts/run-kani.sh \
    >> research-results/insertion-ub-safety-environment.txt
git hash-object "$target" >> research-results/insertion-ub-safety-environment.txt
git rev-parse "HEAD:$target" >> research-results/insertion-ub-safety-environment.txt
printf 'Flags: -Z uninit-checks -Z valid-value-checks --extra-pointer-checks; scripts/run-kani.sh adds -Z unstable-options and repository standard args.\n' \
    >> research-results/insertion-ub-safety-environment.txt

# Append only the proof module in this disposable Actions checkout.
cat "$harness" >> "$target"
cp "$target" research-results/insertion-ub-safety-smallsort.rs

proof_log=research-results/prove_outer_safety_4_ub.log
set +e
bash scripts/run-kani.sh --path . --kani-args \
    --harness slice::sort::shared::smallsort::challenge8_insertion_safety::prove_outer_safety_4 \
    --exact --jobs 1 -Z uninit-checks -Z valid-value-checks --extra-pointer-checks \
    2>&1 | tee "$proof_log"
kani_status=${PIPESTATUS[0]}
set -e
printf '%s\n' "$kani_status" > research-results/prove_outer_safety_4_ub-exit-code.txt

if [[ -x kani_build/scripts/kani ]]; then
    kani_build/scripts/kani --version >> research-results/insertion-ub-safety-environment.txt 2>&1 || true
fi
if command -v cbmc >/dev/null; then
    cbmc --version >> research-results/insertion-ub-safety-environment.txt 2>&1 || true
fi

if python3 - "$proof_log" "$kani_status" research-results/insertion-ub-safety-summary.json <<'PY'
import json
import re
import sys
from pathlib import Path

log_path, exit_text, output_path = sys.argv[1:]
log = Path(log_path).read_text(errors="replace")
exit_code = int(exit_text)
reasons = []
check_re = re.compile(r"(?ms)^Check\s+(\d+):\s*(.*?)\n(.*?)(?=^Check\s+\d+:|\Z)")
checks = []
for match in check_re.finditer(log):
    body = match.group(3)
    status_match = re.search(r"(?m)^\s*-\s*Status:\s*(\S+)", body)
    if not status_match:
        continue
    message_match = re.search(r"(?m)^\s*-\s*Description:\s*(.*)$", body)
    checks.append({
        "check_number": match.group(1),
        "property_id": match.group(2).strip(),
        "status": status_match.group(1).upper(),
        "message": message_match.group(1).strip().strip('"') if message_match else "",
    })
failed = [check for check in checks if check["status"] in {"FAILURE", "FAILED"}]
unsupported = [check for check in failed if "unsupported" in (check["property_id"] + check["message"]).lower()]
unwind = [check for check in failed if "unwind" in check["property_id"].lower() or "unwinding assertion" in check["message"].lower()]
invalid_statuses = [
    check for check in checks
    if check["status"] not in {"SUCCESS", "UNREACHABLE", "SATISFIED"}
    or (check["status"] == "SATISFIED" and ".cover." not in check["property_id"])
]
summary_match = re.search(
    r"(?s)Manual Harness Summary:.*?Complete\s*-\s*(\d+) successfully verified harnesses,\s*(\d+) failures,\s*(\d+) total\.",
    log,
)
harness_summary = (
    {"verified": int(summary_match.group(1)), "failed": int(summary_match.group(2)), "total": int(summary_match.group(3))}
    if summary_match else None
)
verification_match = re.search(r"(?m)^\s*VERIFICATION:-\s*(SUCCESSFUL|FAILED)\s*$", log)
verification = verification_match.group(1) if verification_match else None
cover_match = re.search(r"\*\*\s*(\d+) of (\d+) cover properties satisfied", log)
covers = {"satisfied": int(cover_match.group(1)), "total": int(cover_match.group(2))} if cover_match else None
missing_arguments = re.search(
    r"(?i)(?:not enough arguments|missing required arguments?|the following required arguments were not provided)", log
)
compiler_errors = re.findall(r"(?im)^\s*(?:error(?:\[E\d+\])?:|could not compile\b|failed to compile\b).*$", log)
requested_harness = "slice::sort::shared::smallsort::challenge8_insertion_safety::prove_outer_safety_4"
if exit_code != 0:
    reasons.append(f"Kani process exit code was {exit_code}, expected 0")
if verification != "SUCCESSFUL":
    reasons.append(f"final verification status was {verification!r}, expected SUCCESSFUL")
if harness_summary != {"verified": 1, "failed": 0, "total": 1}:
    reasons.append(f"expected one verified harness and zero failures, got {harness_summary!r}")
if covers != {"satisfied": 7, "total": 7}:
    reasons.append(f"expected all seven covers satisfied, got {covers!r}")
if failed:
    reasons.append(f"{len(failed)} failed check block(s) present")
if not checks:
    reasons.append("no regular Kani check blocks were parsed")
if invalid_statuses:
    reasons.append(f"{len(invalid_statuses)} check block(s) had a non-accepted status")
if unsupported:
    reasons.append("a failed unsupported check is present")
if unwind:
    reasons.append("a failed unwind check is present")
if missing_arguments:
    reasons.append("a missing/not-enough-arguments diagnostic is present")
if compiler_errors:
    reasons.append("an anchored compiler/driver error is present")
if requested_harness not in log:
    reasons.append("requested exact harness name not found in Kani log")

result = {
    "selection": "insertion_ub_safety_4",
    "harness": requested_harness,
    "validated": not reasons,
    "process_exit": exit_code,
    "verification": verification,
    "harness_summary": harness_summary,
    "covers": covers,
    "checks": checks,
    "failed_checks": failed,
    "failed_unsupported_checks": unsupported,
    "failed_unwind_checks": unwind,
    "invalid_status_checks": invalid_statuses,
    "compiler_errors": compiler_errors,
    "reasons": reasons or ["all acceptance checks passed"],
}
Path(output_path).write_text(json.dumps(result, indent=2) + "\n")
print(f"Insertion UB safety selection: {'VALIDATED' if result['validated'] else 'NOT VALIDATED'}")
if reasons:
    for reason in reasons:
        print(f"- {reason}")
sys.exit(0 if result["validated"] else 1)
PY
then
    result=0
else
    result=$?
fi
printf '%s\n' "$result" > research-results/insertion-ub-safety-exit-code.txt
exit "$result"
