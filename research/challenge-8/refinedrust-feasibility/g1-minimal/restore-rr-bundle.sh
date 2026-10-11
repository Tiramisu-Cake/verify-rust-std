#!/usr/bin/env bash
# Cloud Build only: restore the exact, externally reviewed RefinedRust bundle.
set -euo pipefail

die() { printf 'restore-rr-bundle: %s\n' "$*" >&2; exit 2; }

[[ "${SMALLSORT_EXECUTION_PROVIDER:-}" == cloud-build ]] || die 'SMALLSORT_EXECUTION_PROVIDER must be cloud-build'
[[ -n "${CLOUD_BUILD_ID:-}" ]] || die 'CLOUD_BUILD_ID is required'
[[ -d /workspace ]] || die '/workspace is required'

[[ $# == 3 ]] || die 'usage: restore-rr-bundle.sh BUNDLE_PATH APPROVED_SHA256 DESTINATION'
bundle=$1
approved_sha=$2
destination=$3

[[ "$approved_sha" =~ ^[0-9a-f]{64}$ ]] || die 'approved SHA256 must be 64 lowercase hex characters'
[[ -f "$bundle" ]] || die 'bundle file is missing'
bundle=$(realpath -e -- "$bundle")
[[ ! -e "$destination" && ! -L "$destination" ]] || die 'destination must be fresh'
destination_parent=${destination%/*}
destination_name=${destination##*/}
[[ -n "$destination_name" && -d "$destination_parent" ]] || die 'destination parent must already exist'
destination_parent=$(cd -- "$destination_parent" && pwd -P)
case "$destination_parent" in
  /workspace|/workspace/*|/opt|/opt/*) ;;
  *) die 'destination must resolve below /workspace or /opt' ;;
esac
destination="$destination_parent/$destination_name"

actual_sha=$(sha256sum -- "$bundle" | cut -d ' ' -f 1)
[[ "$actual_sha" == "$approved_sha" ]] || die 'bundle SHA256 mismatch'

expected_commit=332d945fafa14bf55c0c8390cb35ec4b0c012cff
expected_tree=b33bcccbbbd6168ac73e0c7238a1edddbe34057c
git clone --quiet --no-checkout "$bundle" "$destination"
git -C "$destination" bundle verify "$bundle"
git -C "$destination" checkout --quiet --detach "$expected_commit"
[[ "$(git -C "$destination" rev-parse HEAD)" == "$expected_commit" ]] || die 'commit mismatch'
[[ "$(git -C "$destination" rev-parse 'HEAD^{tree}')" == "$expected_tree" ]] || die 'tree mismatch'
[[ -z "$(git -C "$destination" status --porcelain --untracked-files=all)" ]] || die 'checkout is not clean'
printf 'restored commit %s tree %s at %s (bundle sha256 %s)\n' "$expected_commit" "$expected_tree" "$destination" "$actual_sha"
