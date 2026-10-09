#!/usr/bin/env bash
# Only the narrow caller-entry diagnostic; use the canonical frozen O26 setup.
set -euo pipefail
[[ "$#" == 1 && "$1" == o26-sort4-caller-entry &&
   "${LANE:-}" == o26-sort4-caller-entry ]] || exit 2
export O26_WITH_OWNER_CONTROLS=0
export O26_WITH_A1_ISOLATED_TEST=0
export O26_WITH_CUT_RELOCATE=0
export O26_WITH_STRICT_CUT_CONTROLS=0
export O26_WITH_STRICT_CUT_FALSE_POSTS=0
export O26_REUSE_STRICT_MATRIX=0
export O26_WITH_SORT4_CAPTURE=0
export O26_WITH_COORDINATION_REGRESSION=0
export O26_WITH_NESTED_PROOF_ORDER_TEST=0
export O26_WITH_SORT4_AST_PROBE=0
export O26_WITH_WRAPPER_REBASE_CAPTURE=0
export O26_WITH_WRAPPER_INPUT_RELATION_CAPTURE=0
export O26_WITH_WRAPPER_REBASE_PROFILE=0
export O26_WITH_WRAPPER_COMP19_TEST=0
export O26_WITH_R3_PROFILE=0
export O26_WITH_GENERIC_NEW_CAPTURE=0
export O26_WITH_SORT4_POSTMARK_PRINT_TEST=0
cloud_dir=${INFRA_CLOUD_DIR:-/workspace/infra/research/challenge-8/cloud-build}
exec bash "$cloud_dir/run-o26-refresh.sh" "$1"
