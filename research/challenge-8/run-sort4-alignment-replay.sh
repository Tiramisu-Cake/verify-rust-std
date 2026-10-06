#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0 OR MIT
# Hosted-only replay of the two pinned historical H_align artifacts.
set -euo pipefail

if [[ "${GITHUB_ACTIONS:-}" != true || "${RUNNER_ENVIRONMENT:-}" != github-hosted || "${RUNNER_OS:-}" != Linux ]]; then
    echo 'H_align artifact replay requires a GitHub-hosted Linux Actions runner' >&2
    exit 2
fi
[[ -n "${GH_TOKEN:-}" ]] || { echo 'GH_TOKEN is required for read-only Actions artifact access' >&2; exit 2; }

repo='Tiramisu-Cake/verify-rust-std'
root=$(git rev-parse --show-toplevel)
bundle="$root/research-results/sort4-alignment-replay"
[[ ! -e "$bundle" ]] || { echo "refusing to reuse replay evidence directory: $bundle" >&2; exit 2; }
mkdir -p "$bundle/downloads" "$bundle/evidence" "$bundle/run-meta" "$bundle/artifact-meta"

download_and_extract() {
    local run_id=$1 artifact_id=$2 expected_sha=$3
    local archive="$bundle/downloads/$run_id.zip"
    local run_json="$bundle/run-meta/$run_id.json"
    local artifact_json="$bundle/artifact-meta/$artifact_id.json"
    local extract="$bundle/evidence/$run_id"
    gh api "repos/$repo/actions/runs/$run_id" > "$run_json"
    gh api "repos/$repo/actions/artifacts/$artifact_id" > "$artifact_json"
    gh api "repos/$repo/actions/artifacts/$artifact_id/zip" > "$archive"
    printf '%s  %s\n' "$expected_sha" "$archive" | tee -a "$bundle/archive-integrity.txt" | sha256sum -c -
    mkdir -p "$extract"
    python3 - "$archive" "$extract" <<'PY'
import pathlib
import sys
import zipfile

archive = pathlib.Path(sys.argv[1])
destination = pathlib.Path(sys.argv[2]).resolve()
with zipfile.ZipFile(archive) as bundle:
    for member in bundle.infolist():
        target = (destination / member.filename).resolve()
        if target != destination and destination not in target.parents:
            raise SystemExit(f"archive member escapes extraction root: {member.filename}")
    bundle.extractall(destination)
PY
    [[ -f "$extract/verifast-sort4-alignment/aggregate.json" ]] || {
        echo "run $run_id archive has an unexpected artifact layout" >&2; exit 2;
    }
}

download_and_extract 37529855468 11443817617 f1ca30c7bc50125c09a901e9442ef2af8e596bc06e3dbd6c50bebb4e00ef663f
download_and_extract 37532204465 11445280961 7ef6d71628a06b3c853cd165a3984669b1b4e1d4e1e282f87ec7998ce87411cd

python3 "$root/research/challenge-8/replay-sort4-alignment-evidence.py" \
    --classifier "$root/research/challenge-8/prepare-and-check-sort4-alignment.py" \
    --evidence-root "$bundle/evidence" \
    --output "$bundle/reclassification" \
    --run-metadata "37529855468=$bundle/run-meta/37529855468.json" \
    --run-metadata "37532204465=$bundle/run-meta/37532204465.json" \
    --artifact-metadata "11443817617=$bundle/artifact-meta/11443817617.json" \
    --artifact-metadata "11445280961=$bundle/artifact-meta/11445280961.json"

python3 "$root/research/challenge-8/test-sort4-alignment-classifier.py" \
    --classifier "$root/research/challenge-8/prepare-and-check-sort4-alignment.py" \
    --replay "$root/research/challenge-8/replay-sort4-alignment-evidence.py" \
    --evidence-root "$bundle/evidence" \
    > "$bundle/reclassification/classifier-tests.log" 2>&1
cat "$bundle/reclassification/classifier-tests.log"

printf 'H_ALIGN_RECLASSIFICATION_DIR=%s\n' "$bundle" >> "${GITHUB_ENV:?}"
printf 'H_align saved-evidence replay passed. Result: `%s/reclassification.json`.\n' \
    "$bundle/reclassification" >> "${GITHUB_STEP_SUMMARY:?}"
