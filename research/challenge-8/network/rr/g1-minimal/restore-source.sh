#!/usr/bin/env bash
# Cloud-only restoration of actual std; no extraction, builds or source rewrites.
set -euo pipefail
[[ ${SMALLSORT_EXECUTION_PROVIDER:-} == cloud-build ]] || exit 2
: "${CLOUD_BUILD_ID:?Cloud-only source restore}"
g1_source_dir=${1:?fresh source directory required}
[[ "$g1_source_dir" == /workspace/* && ! -e "$g1_source_dir" ]] || exit 2
git init "$g1_source_dir"
git -C "$g1_source_dir" remote add origin https://github.com/Tiramisu-Cake/verify-rust-std.git
git -C "$g1_source_dir" fetch --no-tags --depth=1 origin cd371e035c7e573760c43bf934d53e8118ee3e7d
git -C "$g1_source_dir" checkout --detach FETCH_HEAD
test "$(git -C "$g1_source_dir" rev-parse HEAD)" = cd371e035c7e573760c43bf934d53e8118ee3e7d
git -C "$g1_source_dir" submodule update --init --depth=1 -- library/backtrace
test "$(git -C "$g1_source_dir/library/backtrace" rev-parse HEAD)" = d902726a1dcdc1e1c66f73d1162181b5423c645b
test -z "$(git -C "$g1_source_dir" status --porcelain --untracked-files=all)"
