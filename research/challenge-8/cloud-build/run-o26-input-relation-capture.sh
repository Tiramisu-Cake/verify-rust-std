#!/usr/bin/env bash
# Source-only input-relation capture after the canonical O26 baseline.
set -euo pipefail
[[ "$#" == 1 && "$1" == o26-input-relation-capture &&
   "${LANE:-}" == o26-input-relation-capture ]] || exit 2
export O26_WITH_OWNER_CONTROLS=0
export O26_WITH_A1_ISOLATED_TEST=0
export O26_WITH_CUT_RELOCATE=0
export O26_WITH_STRICT_CUT_CONTROLS=0
export O26_WITH_STRICT_CUT_FALSE_POSTS=0
export O26_WITH_SORT4_CAPTURE=0
export O26_WITH_COORDINATION_REGRESSION=0
export O26_WITH_NESTED_PROOF_ORDER_TEST=0
export O26_WITH_SORT4_AST_PROBE=0
export O26_WITH_WRAPPER_REBASE_CAPTURE=0
export O26_WITH_WRAPPER_REBASE_PROFILE=0
export O26_WITH_WRAPPER_COMP19_TEST=0
export O26_WITH_WRAPPER_INPUT_RELATION_CAPTURE=1
unset SORT4_WRAPPER_REBASE_REPO_ROOT SORT4_WRAPPER_REBASE_ADMISSION \
  SORT4_ACTUAL_OWNER_NINE_ADMISSION SORT4_A1_NINE_REPO_ROOT
cloud_dir=${INFRA_CLOUD_DIR:-/workspace/infra/research/challenge-8/cloud-build}
exec bash "$cloud_dir/run-o26-refresh.sh" "$1"
