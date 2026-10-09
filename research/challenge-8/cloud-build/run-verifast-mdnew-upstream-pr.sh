#!/usr/bin/env bash
# Native upstream test lane using the shared pinned source-build/provenance setup.
set -euo pipefail
lane=${1:?usage: run-verifast-mdnew-upstream-pr.sh verifast-mdnew-upstream-pr}
[[ "$lane" == verifast-mdnew-upstream-pr ]] || { echo 'unexpected lane' >&2; exit 2; }
exec bash "$(dirname "$0")/run-verifast-mdnew-cfg.sh" "$lane"
