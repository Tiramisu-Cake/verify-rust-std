#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0 OR MIT
# Recipe dispatcher target for the separately budgeted merge-only lane.
set -euo pipefail

[[ "${1:-}" == merge ]] || {
  printf 'expected merge recipe lane\n' >&2
  exit 2
}
proof_root=${PROOF_ROOT:-/workspace/proof}
[[ "$proof_root" == /workspace/* ]] || {
  printf 'proof root must stay inside /workspace\n' >&2
  exit 2
}
exec bash "$proof_root/research/challenge-8/merge/cloud-build/merge.sh"
