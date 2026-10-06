#!/usr/bin/env bash
# Reprocess one immutable Actions artifact. This mode never invokes RAPx/Cargo.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
[[ "${1:-}" == 30 ]] || { echo 'Replay budget must be 30 minutes' >&2; exit 2; }
[[ "${GITHUB_ACTIONS:-}" == true && "${RUNNER_OS:-}" == Linux && "${RUNNER_ENVIRONMENT:-}" == github-hosted ]] || {
    echo 'Executable replay requires GitHub-hosted Linux Actions' >&2; exit 2;
}
classifier=research/challenge-8/classify-rapx-applicability.py
tests=research/challenge-8/test-rapx-applicability-classifier.py
for input in "$classifier" "$tests" "$0" .github/workflows/smallsort-research.yml; do
    git ls-files --error-unmatch "$input" >/dev/null
    git diff --quiet HEAD -- "$input"
done

repo=Tiramisu-Cake/verify-rust-std
source_run=37508888778
source_sha=929ea803ffff1c4f534716cc8c37bbbfa06a5960
artifact_id=11434810024
archive_sha=d9c5300fd4ac5c6267a8516e33ff4a8ba713795dc9e393e6eff3d8f2a71edf38
out=research-results/rapx-evidence-replay
mkdir -p "$out/historical"
started=$(date +%s)
finish() {
    local code=$?
    trap - EXIT
    printf '%s\n' "$code" > "$out/replay-exit-code.txt"
    printf '%s\n' "$(( $(date +%s) - started ))" > "$out/elapsed-seconds.txt"
    find "$out" -type f ! -name artifact-sha256.txt -print0 | sort -z | xargs -0 sha256sum > "$out/artifact-sha256.txt"
    exit "$code"
}
trap finish EXIT

gh api "repos/$repo/actions/runs/$source_run" > "$out/original-run-metadata.json"
gh api "repos/$repo/actions/artifacts/$artifact_id" > "$out/original-artifact-metadata.json"
archive="$RUNNER_TEMP/rapx-evidence-$artifact_id.zip"
gh api "repos/$repo/actions/artifacts/$artifact_id/zip" > "$archive"
printf '%s  %s\n' "$archive_sha" "$archive" | sha256sum -c - > "$out/archive-sha-check.txt"
source_dir="$RUNNER_TEMP/rapx-evidence-$artifact_id"
mkdir -p "$source_dir"
# Extraction and metadata validation run only here, on the hosted runner.
python3 - "$archive" "$source_dir" "$out" "$source_sha" <<'PY'
import json, pathlib, sys, zipfile
archive, destination, out, source_sha = sys.argv[1:]
out = pathlib.Path(out)
run = json.loads((out / 'original-run-metadata.json').read_text())
artifact = json.loads((out / 'original-artifact-metadata.json').read_text())
assert run['id'] == 37508888778 and run['head_sha'] == source_sha
assert run['head_branch'] == 'challenge-8/research' and run['event'] == 'workflow_dispatch'
assert run['status'] == 'completed' and run['conclusion'] == 'success'
assert artifact['id'] == 11434810024 and not artifact['expired']
assert artifact['workflow_run']['id'] == run['id']
assert artifact['workflow_run']['head_sha'] == source_sha
assert artifact['digest'] == 'sha256:d9c5300fd4ac5c6267a8516e33ff4a8ba713795dc9e393e6eff3d8f2a71edf38'
with zipfile.ZipFile(archive) as z:
    for name in z.namelist():
        path = pathlib.PurePosixPath(name)
        assert not path.is_absolute() and '..' not in path.parts
        assert path.parts[0] == 'rapx-applicability', name
    z.extractall(destination)
environment = pathlib.Path(destination, 'rapx-applicability/experiment-environment.txt').read_text()
assert f'Source commit: {source_sha}\n' in environment
print('PASS original run/artifact identity and source commit')
PY

evidence="$source_dir/rapx-applicability"
cp "$evidence/gate-a-summary.json" "$out/historical/gate-a-summary.json"
for name in zst_aligned zst_source_misaligned zst_destination_misaligned u64_aligned u64_source_misaligned u64_destination_misaligned; do
    cp "$evidence/$name.json" "$out/historical/$name.json"
    sha256sum "$evidence/$name.log" "$evidence/$name-contracts.log" \
        "$evidence/$name-exit-code.txt" "$evidence/$name-contracts-exit-code.txt" >> "$out/source-input-hashes.txt"
done
# Tests mutate temporary copies; the archived input is immutable to this job.
chmod -R a-w "$source_dir"
sha256sum "$classifier" "$tests" "$0" .github/workflows/smallsort-research.yml > "$out/processor-file-hashes.txt"
python3 - "$out" "$(git rev-parse HEAD)" "$source_sha" <<'PY'
import json, pathlib, sys
out, processor_sha, source_sha = sys.argv[1:]
pathlib.Path(out, 'replay-identity.json').write_text(json.dumps({
    'processor_commit': processor_sha,
    'replay_run': __import__('os').environ['GITHUB_RUN_ID'],
    'original_run': 37508888778, 'original_source_commit': source_sha,
    'original_artifact': 11434810024,
    'original_archive_sha256': 'd9c5300fd4ac5c6267a8516e33ff4a8ba713795dc9e393e6eff3d8f2a71edf38',
    'historical_manual_closeout_commit': '3e628c6a2d1197c069abf46fba33b3453c2de57f',
    'mode': 'saved-evidence-replay', 'new_verification': False,
}, indent=2) + '\n')
PY

set +e
/usr/bin/time -v -o "$out/tests-resources.txt" \
    timeout --signal=TERM --kill-after=15s 1500s \
    python3 "$tests" --evidence-dir "$evidence" 2>&1 | tee "$out/tests.log"
test_code=${PIPESTATUS[0]}
set -e
printf '%s\n' "$test_code" > "$out/tests-exit-code.txt"
(( test_code == 0 )) || exit "$test_code"

for name in zst_aligned zst_source_misaligned zst_destination_misaligned u64_aligned u64_source_misaligned u64_destination_misaligned; do
    python3 "$classifier" --case "$name" \
        --exit-code "$(cat "$evidence/$name-exit-code.txt")" \
        --contract-exit-code "$(cat "$evidence/$name-contracts-exit-code.txt")" \
        --verify-log "$evidence/$name.log" --contracts "$evidence/$name-contracts.log" \
        --out "$out/$name.json" | tee -a "$out/classifications.log"
done
python3 - "$classifier" "$out" <<'PY'
import importlib.util, json, pathlib, sys
spec = importlib.util.spec_from_file_location('replay_classifier', sys.argv[1])
classifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(classifier)
out = pathlib.Path(sys.argv[2])
records = [json.loads((out / f'{name}.json').read_text()) for name in classifier.CASES]
summary = classifier.summarize(records)
summary['identity'] = json.loads((out / 'replay-identity.json').read_text())
(out / 'automatic-gate-a-report.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps({k: v for k, v in summary.items() if k not in ('cases', 'records', 'identity')}, indent=2))
# Command success is independent of the semantic gate's NO-GO. Rejected or
# incomplete evidence must fail the replay closeout, rather than claim success.
assert summary['commands_succeeded'] and summary['evidence_parsed'], summary
assert summary['gate_outcome'] == 'NO-GO', summary
PY
