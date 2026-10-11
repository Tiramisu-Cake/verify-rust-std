#!/usr/bin/env bash
# Candidate entrypoint. Production dispatcher owns upload/accounting, not this file.
set -euo pipefail
: "${BUILD_ID:?Cloud-only G1}"
: "${RR_G1_AUTHORIZATION_FILE:?independently reviewed execution receipt required}"
: "${RR_G1_SOURCE_DIR:?exact restored source checkout required}"
: "${RR_G1_EVIDENCE_DIR:?fresh evidence directory required}"
mission_g1_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$mission_g1_dir/run.py" --repo "$RR_G1_SOURCE_DIR" \
  --rr /opt/refinedrust --out "$RR_G1_EVIDENCE_DIR" \
  --authorization "$RR_G1_AUTHORIZATION_FILE"
