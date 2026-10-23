#!/usr/bin/env bash
# Warm diagnostic entrypoint candidate. No phase/image admission is implied.
set -euo pipefail
[[ ${1:-} == network-rr-g1 ]] || exit 2
[[ ${SMALLSORT_EXECUTION_PROVIDER:-} == cloud-build ]] || exit 2
: "${CLOUD_BUILD_ID:?Cloud-only G1}"
export PROOF_ROOT=${PROOF_ROOT:-/workspace/proof}
export EVIDENCE_ROOT=${EVIDENCE_ROOT:-/workspace/evidence}
case ${NETWORK_STAGE:-} in
 cold-image) exec bash "${INFRA_ROOT:-/workspace/infra}/research/challenge-8/cloud-build/network-rr/cold-image.sh" ;;
 warm-g1) exec bash "$PROOF_ROOT/research/challenge-8/network/rr/g1-minimal/entrypoint.sh" ;;
 *) printf 'registered NETWORK_STAGE required\n' >&2; exit 2 ;;
esac
