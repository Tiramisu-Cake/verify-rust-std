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
evidence_root=${EVIDENCE_ROOT:-/workspace/evidence}
[[ "$evidence_root" == /workspace/* ]] || {
  printf 'evidence root must stay inside /workspace\n' >&2
  exit 2
}
mode_card="$proof_root/research/challenge-8/cloud-build/origin-layout/R13-UPLOAD-MODE-20261021.json"
synthetic_generator="$proof_root/research/challenge-8/cloud-build/origin-layout/r13-synthetic-upload.py"
normal_merge="$proof_root/research/challenge-8/merge/cloud-build/merge.sh"
r13_required=${R13_UPLOAD_REQUIRED:-false}
[[ "$r13_required" == true || "$r13_required" == false ]] || {
  printf 'invalid R13 upload-required marker\n' >&2
  exit 2
}
if [[ "$r13_required" == true ]]; then
  [[ -f "$mode_card" && ! -L "$mode_card" ]] || {
    printf 'R13 upload is required but its selected mode card is missing or unsafe\n' >&2
    exit 2
  }
fi
if [[ -e "$mode_card" || -L "$mode_card" ]]; then
  [[ -f "$mode_card" && ! -L "$mode_card" ]] || {
    printf 'R13 upload mode card must be a regular non-symlink file\n' >&2
    exit 2
  }
  [[ -f "$synthetic_generator" && ! -L "$synthetic_generator" ]] || {
    printf 'R13 synthetic upload dispatcher is missing or unsafe\n' >&2
    exit 2
  }
  mode=$(python3 "$synthetic_generator" mode "$mode_card") || {
    printf 'R13 upload mode card validation failed\n' >&2
    exit 2
  }
  case "$mode" in
    synthetic-upload)
      exec python3 "$synthetic_generator" generate "$mode_card" "$evidence_root"
      ;;
    proof-r11)
      exec bash "$normal_merge"
      ;;
    *)
      printf 'unsupported R13 upload mode\n' >&2
      exit 2
      ;;
  esac
fi
exec bash "$normal_merge"
