#!/usr/bin/env bash
set -euo pipefail
[[ "${GITHUB_ACTIONS:-}" == true && "${RUNNER_ENVIRONMENT:-}" == github-hosted && "${RUNNER_OS:-}" == Linux ]] || exit 2
[[ "${GITHUB_REF:-}" == refs/heads/research/overnight-select-sort4-26.10 ]] || exit 2
repo=$(git rev-parse --show-toplevel)
cd "$repo"
ev="$repo/research-results/overnight-s6"
mkdir -p "$ev"
if [[ "${1:-}" != --inside ]]; then
 remaining=$((1080 - $(date +%s) + OVERNIGHT_JOB_STARTED_EPOCH))
 (( remaining > 0 )) || exit 124
 set +e
 timeout --signal=TERM --kill-after=10s "${remaining}s" bash "$0" --inside 2>&1 | tee "$ev/execution.log"
 code=${PIPESTATUS[0]}
 printf '%s\n' "$code" > "$ev/exit-code.txt"
 exit "$code"
fi
stage() {
 local name=$1; shift
 local code=0
 /usr/bin/time -v -o "$ev/$name-resources.txt" "$@" > "$ev/$name.log" 2>&1 || code=$?
 printf '%s\n' "$code" > "$ev/$name-exit-code.txt"
 cat "$ev/$name.log"
 return "$code"
}
export RUSTUP_TOOLCHAIN=nightly-2026-09-25
task_temp="$RUNNER_TEMP/overnight-s6"
mkdir -p "$task_temp"
stock_archive="$task_temp/verifast-26.10-linux.tar.gz"
stock_home="$task_temp/verifast-26.10"
source_home="$task_temp/source"
patch_file="$repo/research/challenge-8/overnight-s6/verifast-s6-26.10-candidate.patch"
cfg_patch="$repo/research/challenge-8/verifast-manuallydrop-new-cfg-2610.patch"
printf 'Proof SHA: %s\nProfile: experimental-s6+cfg+a1-inhabited+a1-transmute+tuple2+a1-link+h2a+h2b+callback-unwind-diag-26.10\n' "$(git rev-parse HEAD)" > "$ev/environment.txt"
sha256sum "$patch_file" >> "$ev/environment.txt"
stage download curl -fL --retry 2 -o "$stock_archive" https://github.com/verifast/verifast/releases/download/26.10/verifast-26.10-linux.tar.gz
printf '%s  %s\n' 5ad2a65997457fd5996a27f93107ef7e52c90c0d12b63b6e67f7acbc73e90efd "$stock_archive" | sha256sum -c -
stage extract tar -xzf "$stock_archive" -C "$task_temp"
stage source-checkout git clone --depth 1 --branch 26.10 https://github.com/verifast/verifast.git "$source_home"
[[ "$(git -C "$source_home" rev-parse HEAD)" == f76012fb518703b1d98e243ac4f487f16877cfcb ]] || exit 2
printf '%s  %s\n' f48fcf29b99717c2e0cb37d4708b47eccaa3270b999e4a84093e37fbd51b7469 "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" | sha256sum -c -
stage packages sudo apt-get install --yes --no-install-recommends build-essential m4 patch unzip capnproto
stage compiler rustup toolchain install "$RUSTUP_TOOLCHAIN" --profile minimal --component rustc-dev --component llvm-tools-preview --component rust-src
compiler_sysroot=$(rustc --print sysroot)
export LD_LIBRARY_PATH="$compiler_sysroot/lib:$stock_home/bin:${LD_LIBRARY_PATH:-}"
stage stock-baseline python3 research/challenge-8/check-stock-2610.py --tool-home "$stock_home" --schema "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" --compiler-sysroot "$compiler_sysroot" --evidence "$ev/stock/cases" --deadline-epoch "$((OVERNIGHT_JOB_STARTED_EPOCH+1000))"
export SORT4_SELECT_PROFILE=experimental-s6-26.10-v1
stage s6-stock-capture python3 research/challenge-8/overnight-s6/diagnose-s6.py --tool-home "$stock_home" --schema "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" --compiler-sysroot "$compiler_sysroot" --evidence "$ev/s6-stock-capture"
stage patch-check git -C "$source_home" apply --check "$patch_file"
stage patch-apply git -C "$source_home" apply "$patch_file"
stage cfg-patch-check git -C "$source_home" apply --check "$cfg_patch"
stage cfg-patch-apply git -C "$source_home" apply "$cfg_patch"
for component in overnight-helper/verifast-a1-assert-inhabited-26.10.patch overnight-helper/verifast-a1-pointer-transmute-26.10.patch overnight-callback/verifast-tuple2-own-26.10.patch overnight-helper/verifast-a1-transmute-linkage-26.10.patch overnight-guard/verifast-h2a-generic-guard-link-26.10.patch overnight-callback/verifast-callback-unwind-26.10.patch overnight-guard/verifast-h2b-nominal-drop-template-26.10.patch; do
 component_patch="$repo/research/challenge-8/$component"
 sha256sum "$component_patch" >> "$ev/environment.txt"
 stage "$(basename "$component" .patch)-check" git -C "$source_home" apply --check "$component_patch"
 stage "$(basename "$component" .patch)-apply" git -C "$source_home" apply "$component_patch"
done
git -C "$source_home" diff > "$ev/applied.patch"
printf '%s\n' bin/rust/std/lib.rsspec src/rust_frontend/vf_mir_translator/rust_parser.ml src/rust_frontend/vf_mir_translator/vf_mir_translator.ml > "$ev/allowed-files.txt"
git -C "$source_home" diff --name-only > "$ev/modified-files.txt"
cmp "$ev/allowed-files.txt" "$ev/modified-files.txt"
# Immutable Actions cache: only a console plus its exact applied-diff manifest.
# Every other tool/spec is re-established and audited from the pinned sources.
console_cache="$RUNNER_TEMP/overnight-console-cache"
profile_diff_sha=$(sha256sum "$ev/applied.patch" | cut -d' ' -f1)
if [[ -f "$console_cache/verifast" && -f "$console_cache/manifest.txt" ]]; then
 read -r cache_diff_sha cache_console_sha < "$console_cache/manifest.txt"
 [[ "$cache_diff_sha" == "$profile_diff_sha" ]] || exit 2
 [[ "$(sha256sum "$console_cache/verifast" | cut -d' ' -f1)" == "$cache_console_sha" ]] || exit 2
 cp "$console_cache/verifast" "$source_home/bin/verifast"
 printf 'CACHE_HIT %s %s\n' "$cache_diff_sha" "$cache_console_sha" > "$ev/console-cache.txt"
else
 deps_archive="$task_temp/vfdeps-adf88dc-linux.txz"
 stage deps-download curl -fL --retry 2 -o "$deps_archive" https://github.com/verifast/vfdeps/releases/download/25.01/vfdeps-adf88dc-linux.txz
 printf '%s  %s\n' 8d022c93d51a1d13ec1e782d767c60462405f6865d5ee416f82d6234e93ee580 "$deps_archive" | sha256sum -c -
 stage deps-extract sudo tar -xjf "$deps_archive" -C /
 ln -s /vfdeps-adf88dc /tmp/vfdeps-adf88dc
 export PATH="/tmp/vfdeps-adf88dc/bin:$PATH"
 export CAPNP_INC_DIR=/tmp/vfdeps-adf88dc/include
 export LD_LIBRARY_PATH="$compiler_sysroot/lib:$source_home/bin:/tmp/vfdeps-adf88dc/lib:${LD_LIBRARY_PATH:-}"
 stage decoder-install cargo install --locked --git https://github.com/btj/capnpc-ocaml-decoder --rev 2d6606d9b59cd0c88a66729f3f076c10c0c8e0b2
 stage console-build make -C "$source_home/src" ../bin/verifast WITHOUT_LABLGTK=yes VERBOSE=yes
 mkdir -p "$console_cache"
 cp "$source_home/bin/verifast" "$console_cache/verifast"
 printf '%s %s\n' "$profile_diff_sha" "$(sha256sum "$console_cache/verifast" | cut -d' ' -f1)" > "$console_cache/manifest.txt"
 printf 'HOSTED_BUILD %s\n' "$profile_diff_sha" > "$ev/console-cache.txt"
fi
cp -an "$stock_home/bin/." "$source_home/bin/"
if [[ -d "$stock_home/lib" ]]; then mkdir -p "$source_home/lib"; cp -an "$stock_home/lib/." "$source_home/lib/"; fi
for binary in vf-rust-mir-exporter refinement-checker vf-cxx-ast-exporter libz3.so; do cmp "$stock_home/bin/$binary" "$source_home/bin/$binary"; done
python3 - "$stock_home" "$source_home" "$ev" <<'AUDIT'
import hashlib,json,pathlib,sys
stock,src,ev=map(pathlib.Path,sys.argv[1:]); h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a={str(p.relative_to(stock)):p for p in (stock/'bin/rust').rglob('*.rsspec')}
b={str(p.relative_to(src)):p for p in (src/'bin/rust').rglob('*.rsspec')}
assert a.keys()==b.keys()
assert all(a[k].read_bytes()==b[k].read_bytes() for k in a if k!='bin/rust/std/lib.rsspec')
assert a['bin/rust/std/lib.rsspec'].read_bytes()!=b['bin/rust/std/lib.rsspec'].read_bytes()
(ev/'spec-audit.json').write_text(json.dumps({k:h(a[k]) for k in a},indent=2)+'\n')
(ev/'profile-hashes.json').write_text(json.dumps({k:h(src/k) for k in ['bin/verifast','bin/vf-rust-mir-exporter','bin/refinement-checker','bin/rust/std/lib.rsspec','src/rust_frontend/vf_mir/vf_mir.capnp','src/rust_frontend/vf_mir_translator/vf_mir_translator.ml','src/rust_frontend/vf_mir_translator/rust_parser.ml']},indent=2)+'\n')
AUDIT
{
 rustc --version --verbose
 capnp --version
 if command -v ocamlc >/dev/null; then ocamlc -version; else printf 'OCaml: cached console, build tool not installed\n'; fi
 if command -v dune >/dev/null; then dune --version; else printf 'Dune: cached console, build tool not installed\n'; fi
 sha256sum "$stock_archive" "$patch_file" "$source_home/bin/verifast" "$stock_home/bin/verifast"
} >> "$ev/environment.txt"
ldd "$source_home/bin/verifast" > "$ev/console-ldd.txt"
if grep -q 'not found' "$ev/console-ldd.txt"; then exit 2; fi
export SORT4_SELECT_PROFILE=experimental-s6-26.10-v1
stage s6-diagnostic python3 research/challenge-8/overnight-s6/diagnose-s6.py --tool-home "$source_home" --schema "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" --compiler-sysroot "$compiler_sysroot" --evidence "$ev/s6-diagnostic"
# Independent diagnostics run before the larger component matrix. Their stage
# failures are retained; neither diagnostic collection nor a green workflow
# implies acceptance of helper/callback/actual Rust.
linkage_status=0
stage constructor-linkage python3 research/challenge-8/overnight-linkage/check-constructor-linkage.py --tool-home "$source_home" --schema "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" --compiler-sysroot "$compiler_sysroot" --evidence "$ev/constructor-linkage" --deadline-epoch "$((OVERNIGHT_JOB_STARTED_EPOCH+1020))" || linkage_status=$?
asptr_status=0
stage asptr-linkage python3 research/challenge-8/overnight-linkage/check-asptr-linkage.py --tool-home "$source_home" --schema "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" --compiler-sysroot "$compiler_sysroot" --evidence "$ev/asptr-linkage" --deadline-epoch "$((OVERNIGHT_JOB_STARTED_EPOCH+1020))" || asptr_status=$?
intrinsic_drop_status=0
stage intrinsic-drop-linkage python3 research/challenge-8/overnight-linkage/check-intrinsic-drop-linkage.py --tool-home "$source_home" --schema "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" --compiler-sysroot "$compiler_sysroot" --evidence "$ev/intrinsic-drop-linkage" --deadline-epoch "$((OVERNIGHT_JOB_STARTED_EPOCH+1020))" || intrinsic_drop_status=$?
projection_status=0
stage actual-projection python3 research/challenge-8/overnight-helper/check-actual-projection.py --tool-home "$source_home" --schema "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" --compiler-sysroot "$compiler_sysroot" --evidence "$ev/actual-projection" --deadline-epoch "$((OVERNIGHT_JOB_STARTED_EPOCH+1020))" || projection_status=$?
helper_status=0
stage helper-certificates python3 research/challenge-8/overnight-helper/test-helper-certificates.py || helper_status=$?
stage helper-capture python3 research/challenge-8/overnight-helper/check-helper.py --tool-home "$source_home" --schema "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" --compiler-sysroot "$compiler_sysroot" --evidence "$ev/helper" --deadline-epoch "$((OVERNIGHT_JOB_STARTED_EPOCH+700))" --actual-capture --a1-linkage-proof --g1-variants symbolic_frame,two_frames || helper_status=$?
g1_callee_status=0
stage isolated-forget-callee python3 research/challenge-8/overnight-helper/check-forget-callee.py --tool-home "$source_home" --schema "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" --compiler-sysroot "$compiler_sysroot" --evidence "$ev/g1-callee" --deadline-epoch "$((OVERNIGHT_JOB_STARTED_EPOCH+1020))" || g1_callee_status=$?
g1_call_status=0
stage generic-forget-call-lane python3 research/challenge-8/overnight-helper/check-forget-call-lane.py --tool-home "$source_home" --schema "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" --compiler-sysroot "$compiler_sysroot" --evidence "$ev/g1-call-lane" --deadline-epoch "$((OVERNIGHT_JOB_STARTED_EPOCH+1020))" || g1_call_status=$?
owner_completion_status=0
for variant in positive false_post pointee_rights thread_duplication wrong_pointer; do
 stage "owner-post-completion-$variant" python3 research/challenge-8/overnight-helper/check-owner-post-completion.py --tool-home "$source_home" --schema "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" --compiler-sysroot "$compiler_sysroot" --evidence "$ev/owner-post-completion/$variant" --deadline-epoch "$((OVERNIGHT_JOB_STARTED_EPOCH+1020))" --variant "$variant" || owner_completion_status=$?
done
owner_projection_status=0
stage actual-owner-projection python3 research/challenge-8/overnight-helper/check-actual-owner-projection.py --tool-home "$source_home" --schema "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" --compiler-sysroot "$compiler_sysroot" --evidence "$ev/actual-owner-projection" --deadline-epoch "$((OVERNIGHT_JOB_STARTED_EPOCH+1020))" --prove --owner-post-completion || owner_projection_status=$?
tuple_status=0
stage tuple2-capture python3 research/challenge-8/overnight-callback/run-tuple2-own-cases.py --repo-root "$repo" --source-checkout "$source_home" --tool-home "$source_home" --schema "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" --compiler-sysroot "$compiler_sysroot" --evidence "$ev/tuple2" --deadline-epoch "$((OVERNIGHT_JOB_STARTED_EPOCH+800))" --cumulative-profile --callback-unwind-matrix --release-support-home "$stock_home" --release-archive "$stock_archive" || tuple_status=$?
generic_drop_status=0
stage generic-pointer-drop-capture python3 research/challenge-8/overnight-guard/capture-generic-pointer-drop.py --tool-home "$source_home" --schema "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" --compiler-sysroot "$compiler_sysroot" --evidence "$ev/generic-pointer-drop" --deadline-epoch "$((OVERNIGHT_JOB_STARTED_EPOCH+1020))" || generic_drop_status=$?
guard_link_status=0
stage generic-guard-linkage python3 research/challenge-8/overnight-guard/capture-guard-linkage.py --guard-root "$repo" --variants positive method_operand guard_operand --tool-home "$source_home" --schema "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" --compiler-sysroot "$compiler_sysroot" --evidence "$ev/generic-guard-linkage" --deadline-epoch "$((OVERNIGHT_JOB_STARTED_EPOCH+1020))" || guard_link_status=$?
guard_template_status=0
stage nominal-guard-template python3 research/challenge-8/overnight-guard/capture-guard-linkage.py --guard-root "$repo" --template-root "$repo" --variants positive method_operand guard_operand owner_predicate field_visibility missing_cell wrong_target duplicate_owner_post --tool-home "$source_home" --schema "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" --compiler-sysroot "$compiler_sysroot" --evidence "$ev/nominal-guard-template" --deadline-epoch "$((OVERNIGHT_JOB_STARTED_EPOCH+1020))" || guard_template_status=$?
guard_owner_status=0
stage nominal-guard-owner-capture python3 research/challenge-8/overnight-guard/capture-guard-owner.py --tool-home "$source_home" --schema "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" --compiler-sysroot "$compiler_sysroot" --evidence "$ev/guard-owner" --deadline-epoch "$((OVERNIGHT_JOB_STARTED_EPOCH+1020))" || guard_owner_status=$?
sort4_status=0
stage actual-sort4-memory-pre python3 research/challenge-8/overnight-sort4/capture.py --repo-root "$repo" --tool-home "$source_home" --schema "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" --compiler-sysroot "$compiler_sysroot" --evidence "$ev/actual-sort4-memory-pre" --deadline-epoch "$((OVERNIGHT_JOB_STARTED_EPOCH+900))" --memory-pre || sort4_status=$?
sort4_borrow_status=0
stage actual-sort4-borrow-prefix python3 research/challenge-8/overnight-sort4/capture.py --repo-root "$repo" --tool-home "$source_home" --schema "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" --compiler-sysroot "$compiler_sysroot" --evidence "$ev/actual-sort4-borrow-prefix" --deadline-epoch "$((OVERNIGHT_JOB_STARTED_EPOCH+1020))" --borrow-prefix || sort4_borrow_status=$?
copy_status=0
stage scratch-copy-capture python3 research/challenge-8/overnight-memory/check-copy-scratch.py --tool-home "$source_home" --schema "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" --compiler-sysroot "$compiler_sysroot" --evidence "$ev/scratch-copy" --deadline-epoch "$((OVERNIGHT_JOB_STARTED_EPOCH+1020))" || copy_status=$?
# H2a changes the frontend profile: run a fresh full S6 regression.
matrix_status=0
stage s6-full-matrix python3 research/challenge-8/overnight-s6/accept-s6.py --stock-home "$stock_home" --tool-home "$source_home" --schema "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" --compiler-sysroot "$compiler_sysroot" --evidence "$ev/s6-full" --deadline-epoch "$((OVERNIGHT_JOB_STARTED_EPOCH+1020))" || matrix_status=$?
printf 'constructor_linkage_stage=%s\nasptr_linkage_stage=%s\nintrinsic_drop_linkage_stage=%s\nactual_projection_stage=%s\nhelper_stage=%s\ng1_callee_stage=%s\ng1_call_lane_stage=%s\nowner_completion_stage=%s\nowner_projection_stage=%s\ntuple2_stage=%s\ngeneric_drop_capture_stage=%s\nguard_link_capture_stage=%s\nguard_template_stage=%s\nguard_owner_capture_stage=%s\nsort4_capture_stage=%s\nsort4_borrow_stage=%s\ncopy_capture_stage=%s\ns6_matrix_stage=%s\ncombined_profile=EXPERIMENTAL_UNTIL_NEW_COMPONENT_ACCEPTANCE\n' "$linkage_status" "$asptr_status" "$intrinsic_drop_status" "$projection_status" "$helper_status" "$g1_callee_status" "$g1_call_status" "$owner_completion_status" "$owner_projection_status" "$tuple_status" "$generic_drop_status" "$guard_link_status" "$guard_template_status" "$guard_owner_status" "$sort4_status" "$sort4_borrow_status" "$copy_status" "$matrix_status" > "$ev/aggregate-stage-status.txt"
(( linkage_status == 0 && asptr_status == 0 && intrinsic_drop_status == 0 && projection_status == 0 && helper_status == 0 && g1_callee_status == 0 && g1_call_status == 0 && owner_completion_status == 0 && owner_projection_status == 0 && tuple_status == 0 && generic_drop_status == 0 && guard_link_status == 0 && guard_template_status == 0 && guard_owner_status == 0 && sort4_status == 0 && sort4_borrow_status == 0 && copy_status == 0 && matrix_status == 0 ))
