#!/usr/bin/env bash
set -euo pipefail
export O26_WITH_A1_ISOLATED_TEST=1
export O26_WITH_OWNER_CONTROLS=1
exec bash "$(dirname "$0")/run-o26-refresh.sh"
