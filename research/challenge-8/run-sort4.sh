#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0 OR MIT
set -euo pipefail

if [[ "${GITHUB_ACTIONS:-}" != true || "${RUNNER_OS:-}" != Linux || "${RUNNER_ENVIRONMENT:-}" != github-hosted ]]; then
    echo 'sort4 proofs require a GitHub-hosted Linux Actions runner' >&2
    exit 2
fi
cd "$(git rev-parse --show-toplevel)"

if [[ "${1:-}" == --stages ]]; then
    for proof in prove_sort4_values prove_sort4_stability; do
        printf '\nRunning actual sort4 stage: %s\n' "$proof"
        /usr/bin/time -v -o "research-results/$proof-resources.txt" \
            bash scripts/run-kani.sh --path . --kani-args \
            --harness "slice::sort::shared::smallsort::challenge8_sort4::$proof" \
            --exact --jobs 1 2>&1 | tee "research-results/$proof.log"
        python3 - "$proof" <<'PY'
from pathlib import Path
import re
import sys
proof = sys.argv[1]
log = Path(f'research-results/{proof}.log').read_text()
expected_covers = {'prove_sort4_values': 12, 'prove_sort4_stability': 6}[proof]
assert 'Complete - 1 successfully verified harnesses, 0 failures, 1 total.' in log
assert 'VERIFICATION:- SUCCESSFUL' in log
assert re.search(r'\*\* 0 of [1-9][0-9]* failed', log)
assert re.findall(r'\*\* (\d+) of (\d+) cover properties satisfied', log) == [
    (str(expected_covers), str(expected_covers))
]
Path(f'research-results/{proof}-acceptance.txt').write_text(
    f'PASS: one actual-body harness; zero failed checks; {expected_covers}/{expected_covers} covers\n'
)
PY
    done
    exit 0
fi

budget=${1:-90}
case "$budget" in
    30|60|90|120) ;;
    *) echo 'Budget must be 30, 60, 90 or 120 minutes' >&2; exit 2 ;;
esac
target=library/core/src/slice/sort/shared/smallsort.rs
proof_source=research/challenge-8/sort4.rs
expected_blob=e555fce440872898e47fd5114f32eb15401d07df
if [[ "$(git hash-object "$target")" != "$expected_blob" ]] || \
   ! git diff --quiet HEAD -- "$target" "$proof_source" scripts/run-kani.sh tool_config/kani-version.toml rust-toolchain.toml; then
    echo 'Target and proof/tool inputs must match the approved checked-out source' >&2
    exit 2
fi
rg -Fx 'commit = "152c6a8c875d9886a67e229247b4826d6105ccfd"' tool_config/kani-version.toml
rg -Fx 'channel = "nightly-2026-02-05"' rust-toolchain.toml
if rg -q 'pub mod challenge8_sort4' "$target"; then
    echo 'sort4 module already present; use a clean checkout' >&2
    exit 2
fi
mkdir -p research-results
{
    printf 'Source commit: '
    git rev-parse HEAD
    printf 'Selection: sort4_functional\nBudget including cold build: %s minutes\n' "$budget"
    printf 'Runner: %s/%s\n' "$RUNNER_OS" "$RUNNER_ENVIRONMENT"
    printf 'Target blob: %s\n' "$expected_blob"
    printf 'Profile: repository default checks, exact harnesses, jobs 1, unwind 6 with assertions.\n'
    printf 'No explicit uninit/valid-value/extra-pointer instrumentation; no checks disabled.\n'
    cat tool_config/kani-version.toml rust-toolchain.toml
    sha256sum "$target" "$proof_source" research/challenge-8/run-sort4.sh \
        scripts/run-kani.sh tool_config/kani-version.toml rust-toolchain.toml
    uname -a
    lscpu
    free -h
    df -h .
} > research-results/environment.txt

# Only append proof code in the disposable hosted checkout. Audit the complete
# original byte prefix rather than reconstructing or rewriting the runtime body.
cat "$proof_source" >> "$target"
python3 - <<'PY' > research-results/source-audit.txt
from pathlib import Path
import subprocess
target = 'library/core/src/slice/sort/shared/smallsort.rs'
original = subprocess.check_output(['git', 'show', 'HEAD:' + target])
proof = Path('research/challenge-8/sort4.rs').read_bytes()
assert Path(target).read_bytes() == original + proof
assert b'super::sort4_stable(' in proof
print('PASS: complete actual std source unchanged; only checked-in cfg(kani) module appended')
PY
cp "$target" research-results/smallsort-with-sort4.rs

set +e
/usr/bin/time -v -o research-results/resources.txt \
    timeout --signal=TERM --kill-after=30s "${budget}m" \
    bash research/challenge-8/run-sort4.sh --stages \
    2>&1 | tee research-results/verification.log
verification_status=${PIPESTATUS[0]}
set -e
printf '%s\n' "$verification_status" > research-results/exit-code.txt
if [[ -x kani_build/scripts/kani ]]; then
    {
        kani_build/scripts/kani --version
        git -C kani_build rev-parse HEAD
        sha256sum kani_build/scripts/kani
        if [[ -f kani_build/target/release/kani-driver ]]; then
            sha256sum kani_build/target/release/kani-driver
        fi
    } >> research-results/environment.txt 2>&1
fi
if command -v cbmc >/dev/null; then
    cbmc --version >> research-results/environment.txt 2>&1
    sha256sum "$(command -v cbmc)" >> research-results/environment.txt
fi
if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
    {
        printf '### Actual sort4 functional proofs\n\n'
        printf 'Exit: `%s`; separate four-cell buffers; full-range i32 keys; pure comparison.\n\n' "$verification_status"
        printf 'Values and tagged stability are separate actual-body harnesses. Generic safety and the stronger UB profile remain open.\n'
    } >> "$GITHUB_STEP_SUMMARY"
fi
exit "$verification_status"
