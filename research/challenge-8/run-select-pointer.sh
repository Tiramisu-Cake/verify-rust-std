#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0 OR MIT
# Temporary S6 hosted normal-MIR diagnostic dispatch. Full v2 runner is retained
# for restoration after this one diagnostic run.
set -euo pipefail
exec bash research/challenge-8/run-select-pointer-normal-capture.sh "$@"
