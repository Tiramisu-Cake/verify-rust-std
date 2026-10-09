#!/usr/bin/env bash
# Explicit committed entrypoint for the nested R3 receiver diagnostic.
set -euo pipefail
[[ "$#" == 1 && "$1" == o26-r3-ghost-scope-test &&
   "${LANE:-}" == o26-r3-ghost-scope-test ]] || exit 2
export O26_WITH_R3_RECEIVER_TEST=1
cloud_dir=${INFRA_CLOUD_DIR:-/workspace/infra/research/challenge-8/cloud-build}
exec bash "$cloud_dir/run-o26-r3-ghost-scope-lane.sh" "$LANE"
