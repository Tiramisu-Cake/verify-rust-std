#!/usr/bin/env bash
# Opt-in Cloud lane combining the existing profile and one component-19 TEST.
set -euo pipefail
[[ "${1:-}" == o26-wrapper-controls ]] || exit 2
export O26_WITH_OWNER_CONTROLS=0
export O26_WITH_A1_ISOLATED_TEST=0
export O26_WITH_CUT_RELOCATE=0
export O26_WITH_SORT4_CAPTURE=0
export O26_WITH_COORDINATION_REGRESSION=0
export O26_WITH_NESTED_PROOF_ORDER_TEST=0
export O26_WITH_SORT4_AST_PROBE=0
export O26_WITH_WRAPPER_REBASE_CAPTURE=0
export O26_WITH_WRAPPER_REBASE_PROFILE=1
export O26_WITH_WRAPPER_COMP19_TEST=1
cloud_dir=${INFRA_CLOUD_DIR:-/workspace/infra/research/challenge-8/cloud-build}
exec bash "$cloud_dir/run-o26-refresh.sh"
