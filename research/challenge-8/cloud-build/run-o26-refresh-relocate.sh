#!/usr/bin/env bash
set -euo pipefail
export O26_WITH_CUT_RELOCATE=1
cloud_dir=${INFRA_CLOUD_DIR:-/workspace/infra/research/challenge-8/cloud-build}
exec bash "$cloud_dir/run-o26-refresh.sh"
