#!/usr/bin/env bash
# Explicit candidate entrypoint for optional R3 ghost-column and nested TESTs.
set -euo pipefail
[[ "$#" == 1 && "$1" == o26-r3-ghost-scope-test &&
   "${LANE:-}" == o26-r3-ghost-scope-test ]] || exit 2
export O26_WITH_R3_GHOST_COLUMN_TEST=1
export O26_WITH_R3_COLUMN_NESTED_TEST=1
cloud_dir=${INFRA_CLOUD_DIR:-/workspace/infra/research/challenge-8/cloud-build}
exec bash "$cloud_dir/run-o26-r3-receiver-lane.sh" "$LANE"
