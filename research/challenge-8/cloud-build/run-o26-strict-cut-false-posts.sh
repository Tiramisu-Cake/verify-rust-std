#!/usr/bin/env bash
# Frozen O26 baseline, mapped-ID relocation, strictCUT matrix, false posts.
set -euo pipefail
[[ "$#" == 1 && "$1" == o26-strict-cut-false-posts &&
   "${LANE:-}" == o26-strict-cut-false-posts ]] || exit 2

export O26_WITH_OWNER_CONTROLS=0
export O26_WITH_A1_ISOLATED_TEST=0
export O26_WITH_SORT4_CAPTURE=0
export O26_WITH_COORDINATION_REGRESSION=0
export O26_WITH_NESTED_PROOF_ORDER_TEST=0
export O26_WITH_SORT4_AST_PROBE=0
export O26_WITH_WRAPPER_REBASE_CAPTURE=0
export O26_WITH_WRAPPER_INPUT_RELATION_CAPTURE=0
export O26_WITH_WRAPPER_REBASE_PROFILE=0
export O26_WITH_WRAPPER_COMP19_TEST=0
export O26_WITH_CUT_RELOCATE=1
export O26_WITH_STRICT_CUT_CONTROLS=1
export O26_WITH_STRICT_CUT_FALSE_POSTS=1

cloud_dir=${INFRA_CLOUD_DIR:-/workspace/infra/research/challenge-8/cloud-build}
exec bash "$cloud_dir/run-o26-refresh.sh" "$1"
