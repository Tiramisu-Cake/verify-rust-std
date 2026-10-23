#!/usr/bin/env bash
# Candidate only: invoke through the separately authorized existing dispatcher.
set -euo pipefail
[[ ${SMALLSORT_EXECUTION_PROVIDER:-} == cloud-build ]] || exit 2
: "${CLOUD_BUILD_ID:?Cloud-only candidate}"
: "${SMALLSORT_DEADLINE_EPOCH:?dispatcher deadline required}"
: "${PROOF_ROOT:=/workspace/proof}"
: "${EVIDENCE_ROOT:=/workspace/evidence}"
g1_candidate_dir="$PROOF_ROOT/research/challenge-8/network/rr/g1-minimal"
exec python3 "$g1_candidate_dir/run.py" \
  --source /workspace/g1-source --rr /opt/refinedrust \
  --freeze "$g1_candidate_dir/freeze.json" --out "$EVIDENCE_ROOT/g1"
