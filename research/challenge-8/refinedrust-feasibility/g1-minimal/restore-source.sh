#!/usr/bin/env bash
# Cloud-only restoration of actual std; no extraction, builds or source rewrites.
set -euo pipefail
[[ ${SMALLSORT_EXECUTION_PROVIDER:-} == cloud-build ]] || exit 2
: "${CLOUD_BUILD_ID:?Cloud-only source restore}"
g1_source_dir=${1:?fresh source directory required}
[[ "$g1_source_dir" == /workspace/* && ! -e "$g1_source_dir" ]] || exit 2
git init "$g1_source_dir"
git -C "$g1_source_dir" remote add origin https://github.com/Tiramisu-Cake/verify-rust-std.git
git -C "$g1_source_dir" fetch --no-tags --depth=1 origin c7ca8c467aecf10a4b53039372ee97714f854ee3
git -C "$g1_source_dir" checkout --detach FETCH_HEAD
test "$(git -C "$g1_source_dir" rev-parse HEAD)" = c7ca8c467aecf10a4b53039372ee97714f854ee3
git -C "$g1_source_dir" submodule update --init --depth=1 -- library/backtrace
test "$(git -C "$g1_source_dir/library/backtrace" rev-parse HEAD)" = 28ec93b503bf0410745bc3d571bf3dc1caac3019
test -z "$(git -C "$g1_source_dir" status --porcelain --untracked-files=all)"
