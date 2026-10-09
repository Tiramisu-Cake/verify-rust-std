#!/usr/bin/env bash
# Exact O26 restoration plus separate unaccepted CUT instrumentation.
set -euo pipefail
export O26_WITH_CUT_TRACE=1
exec bash "${INFRA_CLOUD_DIR:-${INFRA_ROOT:-/workspace/infra}/research/challenge-8/cloud-build}/run-o26.sh" "$@"
