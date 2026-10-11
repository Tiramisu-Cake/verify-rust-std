#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0 OR MIT
# Hosted-only OVERNIGHT-MERGE-26.10 experiments.
set -euo pipefail

[[ "${GITHUB_ACTIONS:-}" == true && "${RUNNER_ENVIRONMENT:-}" == github-hosted && "${RUNNER_OS:-}" == Linux ]] || {
  echo 'stock-26.10 harness requires GitHub-hosted Linux Actions' >&2
  exit 2
}
[[ "${GITHUB_REF:-}" == refs/heads/overnight/merge-26.10 ]] || {
  echo 'stock-26.10 harness only accepts overnight/merge-26.10' >&2
  exit 2
}
run_mode=${1:-}
[[ "$run_mode" == merge_geometry || "$run_mode" == merge_compile_only || "$run_mode" == merge_bridge_minimal || "$run_mode" == merge_len1_minimal || "$run_mode" == merge_caller_composition_minimal || "$run_mode" == merge_selected_drop_minimal ]] || {
  echo 'expected merge_geometry, merge_compile_only, merge_bridge_minimal merge_len1_minimal or merge_caller_composition_minimal run mode' >&2
  exit 2
}
job_started=$SECONDS
repo=$(git rev-parse --show-toplevel)
cd "$repo"
[[ "$(git rev-parse HEAD)" == "${GITHUB_SHA:?GITHUB_SHA is required}" ]] || {
  echo 'checkout HEAD differs from dispatched GITHUB_SHA' >&2
  exit 2
}

evidence="$repo/research-results/merge-overnight"
[[ ! -e "$evidence" ]] || { echo "refusing to reuse prior evidence: $evidence" >&2; exit 2; }
mkdir -p "$evidence"
task_temp="$RUNNER_TEMP/challenge8-merge-overnight"
[[ ! -e "$task_temp" ]] || { echo "refusing to reuse prior tool directory: $task_temp" >&2; exit 2; }
mkdir -p "$task_temp"

vf_version=26.10
vf_source_commit=f76012fb518703b1d98e243ac4f487f16877cfcb
vf_archive_sha=5ad2a65997457fd5996a27f93107ef7e52c90c0d12b63b6e67f7acbc73e90efd
vf_console_sha=9b7650ad3ab0dad3b8974ae9ba1c662ab2cd897ce1dd07215dedcbe460249ee1
vf_exporter_sha=b00c75f43ab4d89bf85f5e62a5114a238b89b720d4598d90423347b9d97ac796
vf_refiner_sha=b049c8d1b0bb350f77664e1c75c5a95966c5839984abc25c7cb629c0cba04d28
schema_sha=f48fcf29b99717c2e0cb37d4708b47eccaa3270b999e4a84093e37fbd51b7469
spec_manifest_sha=4a0911303bbb087f1f50ce85524197edbb541f31c72e8133dfbcc9cf528e03a0
spec_checks_sha=2adb5f85e2077a96e2db6b97da9af17d9324ad3c586187292854970e63078da4
source_profile_sha=8c72795b0cd452580372e963cf9620e8d32e891eae389f6f0b11034373a94c79
tool_home="$task_temp/verifast-$vf_version"
archive="$task_temp/verifast-$vf_version-linux.tar.gz"
schema="$task_temp/vf_mir.capnp"
export VFVERSION="$vf_version" VFPLATFORM=linux RUSTUP_TOOLCHAIN=nightly-2026-09-25

{
  printf 'Source SHA: '; git rev-parse HEAD
  printf 'Actions SHA: %s\nBranch: overnight/merge-26.10\nSelection: %s\n' "$GITHUB_SHA" "$run_mode"
  printf 'Actual source git commit: cd371e035c7e573760c43bf934d53e8118ee3e7d\nFull source SHA-256: 85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1\n'
  printf 'Profile: official-stock-VeriFast-%s (%s)\nRust toolchain: %s (minimal + rustc-dev + rust-src)\n' "$vf_version" "$vf_source_commit" "$RUSTUP_TOOLCHAIN"
  printf 'Runner: %s/%s\nDistinct W1 + M2a + copy + strict cleanup + zero-safe usize primitive + hidden stack-address patches; explicit pinned strict kernel extension; stock exporter/refiner/schema unchanged\n' "$RUNNER_ENVIRONMENT" "$RUNNER_OS"
  sha256sum research/challenge-8/merge/stock-26.10/*.py \
    research/challenge-8/merge/stock-26.10/*.c \
    research/challenge-8/merge/stock-26.10/*.rs \
    research/challenge-8/merge/stock-26.10/run.sh \
    research/challenge-8/networks/prove.py \
    library/core/src/slice/sort/shared/smallsort.rs
} > "$evidence/environment.txt"

printf '%s  %s\n' 994afa65a24c1deb73fd120ac88c96fa5d86eb971f58adba678c850a1153d0c4 research/challenge-8/networks/prove.py | sha256sum -c -
printf '%s  %s\n' 85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1 library/core/src/slice/sort/shared/smallsort.rs | sha256sum -c -
printf '%s  %s\n' "$spec_manifest_sha" research/challenge-8/merge/stock-26.10/vf-stock-specs.json | sha256sum -c -
printf '%s  %s\n' "$spec_checks_sha" research/challenge-8/merge/stock-26.10/vf-stock-specs.sha256 | sha256sum -c -
printf '%s  %s\n' "$source_profile_sha" research/challenge-8/merge/stock-26.10/vf-profile-source.json | sha256sum -c -

curl --fail --silent --show-error --location --max-time 40 \
  "https://github.com/verifast/verifast/releases/download/$vf_version/verifast-$vf_version-linux.tar.gz" \
  --output "$archive"
printf '%s  %s\n' "$vf_archive_sha" "$archive" | sha256sum -c -
tar -xzf "$archive" -C "$task_temp"
printf '%s  %s\n' "$vf_console_sha" "$tool_home/bin/verifast" | sha256sum -c -
printf '%s  %s\n' "$vf_exporter_sha" "$tool_home/bin/vf-rust-mir-exporter" | sha256sum -c -
printf '%s  %s\n' "$vf_refiner_sha" "$tool_home/bin/refinement-checker" | sha256sum -c -
(cd "$tool_home" && sha256sum --check "$repo/research/challenge-8/merge/stock-26.10/vf-stock-specs.sha256")
spec_count=$(find "$tool_home/bin" -type f \( -name '*.rsspec' -o -name '*.gh' -o -name '*.h' \) | wc -l)
[[ "$spec_count" -eq 58 ]] || { echo "unexpected VeriFast spec-file count: $spec_count" >&2; exit 2; }
sha256sum "$archive" "$tool_home/bin/verifast" "$tool_home/bin/vf-rust-mir-exporter" \
  "$tool_home/bin/refinement-checker" research/challenge-8/merge/stock-26.10/vf-stock-specs.json \
  research/challenge-8/merge/stock-26.10/vf-profile-source.json \
  research/challenge-8/merge/stock-26.10/vf-stock-specs.sha256 >> "$evidence/environment.txt"

timeout --signal=TERM --kill-after=5s 240s rustup toolchain install "$RUSTUP_TOOLCHAIN" \
  --profile minimal --component rustc-dev --component rust-src
sudo timeout --signal=TERM --kill-after=5s 120s apt-get update
sudo timeout --signal=TERM --kill-after=5s 120s apt-get install --yes --no-install-recommends capnproto
capnp --version >> "$evidence/environment.txt"
capnp_path=$(command -v capnp)
sha256sum "$capnp_path" >> "$evidence/environment.txt"
curl --fail --silent --show-error --location --max-time 20 \
  "https://raw.githubusercontent.com/verifast/verifast/$vf_source_commit/src/rust_frontend/vf_mir/vf_mir.capnp" \
  --output "$schema"
printf '%s  %s\n' "$schema_sha" "$schema" | sha256sum -c -
cp "$schema" "$evidence/vf_mir.capnp"
printf 'Schema SHA-256: %s\n' "$schema_sha" >> "$evidence/environment.txt"

compiler_sysroot=$(rustc --print sysroot)
export LD_LIBRARY_PATH="$compiler_sysroot/lib:$tool_home/bin:${LD_LIBRARY_PATH:-}"
{
  rustc --version --verbose
  printf 'Compiler sysroot: %s\n' "$compiler_sysroot"
  find "$tool_home/bin/rust" -type f -name '*.rsspec' -print0 | sort -z | xargs -0 -r sha256sum
  ldd "$tool_home/bin/verifast"
} >> "$evidence/environment.txt" 2>&1

run_one() {
  local label=$1 seconds=$2
  shift 2
  local status
  printf '\n=== %s ===\n' "$label"
  set +e
  timeout --signal=TERM --kill-after=5s "${seconds}s" "$@" 2>&1 | tee "$evidence/group-$label.log"
  status=${PIPESTATUS[0]}
  set -e
  printf '%s %s\n' "$label" "$status" >> "$evidence/group-status.txt"
  if [[ "$status" -ne 0 ]]; then
    suite_status=1
  fi
}

suite() {
  set -uo pipefail
  suite_status=0
  printf 'Actual engine: experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1 (DIAGNOSTIC, NOT ACCEPTED). Mathematical harness raw profile labels are historical; per-case binary SHA and build evidence bind this fresh execution.\n' > "$evidence/mathematical-profile-sidecar.txt"
  run_one rust-profile-smoke 300 python3 research/challenge-8/merge/overnight/pointer-prove.py \
    --profile experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1 \
    --scope 'early complete ordinary normal/unwind body gate; prevents a global specification error masking the full matrix' \
    --tool-home "$experimental_home" --compiler-sysroot "$compiler_sysroot" --schema "$schema" \
    --fixture research/challenge-8/merge/overnight/baseline-cases.rs \
    --cases ordinary_call_normal_unwind --evidence "$evidence/checked-profile-smoke"
  if ! python3 -c 'import json, sys; result = json.load(open(sys.argv[1])); assert result["cases"] == {"ordinary_call_normal_unwind": "PASS"} and result["classifier_controls_passed"], "Rust profile smoke failed; retain complete diagnostic evidence"' "$evidence/checked-profile-smoke/aggregate.json"
  then
    return 1
  fi
  run_one G2-compatibility 90 python3 research/challenge-8/merge/stock-26.10/prove.py \
    --tool-home "$experimental_home" --evidence "$evidence/checked-g2"
  run_one A-compatibility 90 python3 research/challenge-8/merge/stock-26.10/functional-prove.py \
    --tool-home "$experimental_home" --evidence "$evidence/checked-a"
  run_one B-compatibility 120 python3 research/challenge-8/merge/stock-26.10/order-prove.py \
    --tool-home "$experimental_home" --evidence "$evidence/checked-b"
  run_one native-baselines 150 python3 research/challenge-8/merge/overnight/native-prove.py \
    --tool-home "$experimental_home" --evidence "$evidence/checked-native"
  run_one rust-unwind-baselines 180 python3 research/challenge-8/merge/overnight/pointer-prove.py \
    --profile experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1 \
    --scope 'ordinary call normal/unwind and calibrated false-unwind/dead-body baseline controls' \
    --tool-home "$experimental_home" --compiler-sysroot "$compiler_sysroot" --schema "$schema" \
    --fixture research/challenge-8/merge/overnight/baseline-cases.rs --evidence "$evidence/checked-baselines"
  run_one callback-model-diagnostics 240 python3 research/challenge-8/merge/overnight/pointer-prove.py \
    --profile experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1 \
    --scope 'tuple2 ownership and exact HRTB output instantiation support; resource-negative admission remains calibration' \
    --tool-home "$experimental_home" --compiler-sysroot "$compiler_sysroot" --schema "$schema" \
    --fixture research/challenge-8/merge/overnight/callback-cases.rs --evidence "$evidence/checked-callback-model"
  run_one tuple2-shape-admission 180 python3 research/challenge-8/merge/overnight/m2-admission-prove.py \
    --tool-home "$experimental_home" --compiler-sysroot "$compiler_sysroot" --schema "$schema" \
    --evidence "$evidence/checked-m2-shape"
  run_one tuple2-resource-diagnostics 180 python3 research/challenge-8/merge/overnight/pointer-prove.py \
    --profile experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1 \
    --scope 'full tuple2 field owners/thread/value and unrelated physical frame; new negatives require exact intended obligations' \
    --tool-home "$experimental_home" --compiler-sysroot "$compiler_sysroot" --schema "$schema" \
    --fixture research/challenge-8/merge/overnight/m2-resource-cases.rs --evidence "$evidence/checked-m2-resources"
  run_one callback-borrow-diagnostic 90 python3 research/challenge-8/merge/overnight/pointer-prove.py \
    --profile experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1 \
    --scope 'generic callback real loan protocol; full refreshed-value normal/unwind posts; no actual-source claim' \
    --tool-home "$experimental_home" --compiler-sysroot "$compiler_sysroot" --schema "$schema" \
    --fixture research/challenge-8/merge/overnight/callback-borrow-cases.rs --evidence "$evidence/checked-callback-borrow"
  run_one prepared-hrtb-diagnostics 180 python3 research/challenge-8/merge/overnight/pointer-prove.py \
    --profile experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1 \
    --scope 'prepared real loans at exact HRTB FnMut call; full normal/unwind resources; wrong F/T/owner controls remain calibration' \
    --tool-home "$experimental_home" --compiler-sysroot "$compiler_sysroot" --schema "$schema" \
    --fixture research/challenge-8/merge/overnight/hrtb-prepared-cases.rs --evidence "$evidence/checked-hrtb-prepared"
  run_one hrtb-admission-certificate 30 python3 research/challenge-8/merge/overnight/hrtb-admission-certificate.py \
    --evidence-root "$evidence" --output "$evidence/checked-hrtb-admission"
  run_one callback-cleanup-diagnostics 180 python3 research/challenge-8/merge/overnight/pointer-prove.py \
    --profile experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1 \
    --scope 'strict opt-in callback lifetime scope and explicit normal/unwind current-value ownership recovery; controls remain calibration' \
    --tool-home "$experimental_home" --compiler-sysroot "$compiler_sysroot" --schema "$schema" \
    --fixture research/challenge-8/merge/overnight/cleanup-cases.rs --evidence "$evidence/checked-cleanup"
  run_one copy-model-diagnostics 240 python3 research/challenge-8/merge/overnight/pointer-prove.py \
    --profile experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1 \
    --scope 'trusted one-element positive-size option destination copy; full initializedness/value and single source owner/frame targets; generic invalid bytes/ZST excluded' \
    --tool-home "$experimental_home" --compiler-sysroot "$compiler_sysroot" --schema "$schema" \
    --fixture research/challenge-8/merge/overnight/copy-cases.rs --evidence "$evidence/checked-copy"
  run_one wrapping-acceptance 600 python3 research/challenge-8/merge/overnight/pointer-prove.py \
    --profile experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1 \
    --tool-home "$experimental_home" --compiler-sysroot "$compiler_sysroot" --schema "$schema" \
    --evidence "$evidence/checked-wrapping"
  run_one pointer-bridge-diagnostic 360 python3 research/challenge-8/merge/overnight/pointer-prove.py \
    --profile experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1 \
    --tool-home "$experimental_home" --compiler-sysroot "$compiler_sysroot" --schema "$schema" \
    --fixture research/challenge-8/merge/overnight/pointer-bridge-cases.rs \
    --evidence "$evidence/checked-pointer-bridge"
  run_one pointer-domain-bridge 180 python3 research/challenge-8/merge/overnight/pointer-prove.py \
    --profile experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1 \
    --scope 'checked arbitrary-index C1 pointer domain from aligned bounded disjoint array spans; no access rights; positive stride only' \
    --tool-home "$experimental_home" --compiler-sysroot "$compiler_sysroot" --schema "$schema" \
    --fixture research/challenge-8/merge/overnight/pointer-domain-cases.rs \
    --evidence "$evidence/checked-pointer-domain"
  run_one owned-array-resource-diagnostic 180 python3 research/challenge-8/merge/overnight/pointer-prove.py \
    --profile experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1 \
    --scope 'checked generic positive-stride two-cell extraction/current-owner restoration; whole-array and unrelated frame preserved; no actual body or Freeze stability claim' \
    --tool-home "$experimental_home" --compiler-sysroot "$compiler_sysroot" --schema "$schema" \
    --fixture research/challenge-8/merge/overnight/owned-array-cases.rs \
    --evidence "$evidence/checked-owned-array"
  run_one scratch-option-resource-diagnostic 180 python3 research/challenge-8/merge/overnight/pointer-prove.py \
    --profile experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1 \
    --scope 'checked positive-stride option scratch two-hole frame/current-slot restoration; no T owner creation or actual panic claim' \
    --tool-home "$experimental_home" --compiler-sysroot "$compiler_sysroot" --schema "$schema" \
    --fixture research/challenge-8/merge/overnight/scratch-resource-cases.rs \
    --evidence "$evidence/checked-scratch-options"
  run_one concrete-zst-diagnostic 180 python3 research/challenge-8/merge/overnight/pointer-prove.py \
    --profile experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1 \
    --scope 'compiler-backed concrete ZST wrapping identity without assumed size; no memory rights' \
    --tool-home "$experimental_home" --compiler-sysroot "$compiler_sysroot" --schema "$schema" \
    --fixture research/challenge-8/merge/overnight/concrete-zst-cases.rs --evidence "$evidence/checked-concrete-zst"
  run_one experimental-rust-regression 240 python3 research/challenge-8/merge/overnight/pointer-prove.py \
    --profile experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1 \
    --tool-home "$experimental_home" --compiler-sysroot "$compiler_sysroot" --schema "$schema" \
    --fixture research/challenge-8/merge/stock-26.10/pointer-cases.rs \
    --evidence "$evidence/checked-rust-regression" \
    --cases g2_steps,init_const,init_mut,destination_up,forward_left,forward_right,destination_down,pointer_order,pointer_guard,wrong_cursor,address_index
  run_one tuple-layout-entry-diagnostics 120 python3 research/challenge-8/merge/overnight/pointer-prove.py \
    --profile experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1 \
    --scope 'isolated five-shape tuple return ladder and matched entry false assertions; diagnose vacuity without trusting generated helper assumptions' \
    --tool-home "$experimental_home" --compiler-sysroot "$compiler_sysroot" --schema "$schema" \
    --cases tuple_layout_unit_entry_baseline,tuple_layout_flat_pointer_pair,tuple_layout_flat_pointer_pair_false_entry,tuple_layout_pointer_pairs,tuple_layout_pointer_pairs_false_entry,tuple_layout_nested_scalars,tuple_layout_nested_scalars_false_entry,tuple_layout_twelve_quartets,tuple_layout_twelve_quartets_false_entry \
    --fixture research/challenge-8/merge/overnight/tuple-layout-cases.rs --evidence "$evidence/checked-tuple-layout"
  run_one trace-entry-tuple-diagnostics 120 python3 research/challenge-8/merge/overnight/pointer-prove.py \
    --profile experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1 \
    --scope 'isolated exact trace precondition inhabitation versus nested tuple result representation; main contract unchanged' \
    --tool-home "$experimental_home" --compiler-sysroot "$compiler_sysroot" --schema "$schema" \
    --cases trace_generic_entry_domain,trace_u32_entry_domain,trace_generic_entry_domain_negative \
    --fixture research/challenge-8/merge/overnight/trace-precondition-cases.rs --evidence "$evidence/checked-trace-entry"
  run_one usize-source-admission 30 python3 research/challenge-8/merge/overnight/usize-multiple-admission.py \
    --output "$evidence/usize-source-admission.json"
  run_one usize-primitive-diagnostics 120 python3 research/challenge-8/merge/overnight/pointer-prove.py \
    --profile experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1 \
    --scope 'explicit trusted total zero-safe unsigned multiple primitive and independently checked source adapter; does not prove actual std primitive body' \
    --tool-home "$experimental_home" --compiler-sysroot "$compiler_sysroot" --schema "$schema" \
    --fixture research/challenge-8/merge/overnight/usize-multiple-cases.rs --evidence "$evidence/checked-usize-multiple"
  run_one stack-address-admission-diagnostics 120 python3 research/challenge-8/merge/overnight/pointer-prove.py \
    --profile experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1 \
    --scope 'ghost-only existing hidden-struct address projection; exact syntax/missing-ID and parameter admission controls, no permissions granted' \
    --tool-home "$experimental_home" --compiler-sysroot "$compiler_sysroot" --schema "$schema" \
    --fixture research/challenge-8/merge/overnight/stack-address-cases.rs --evidence "$evidence/checked-stack-address"
  run_one stack-address-role-control-preparation 65 python3 research/challenge-8/merge/overnight/stack-address-controls-prepare.py \
    --tool-home "$experimental_home" --compiler-sysroot "$compiler_sysroot" --schema "$schema" \
    --output-dir "$evidence/stack-address-role-controls"
  if [[ -f "$evidence/stack-address-role-controls/stack-address-control-cases.rs" ]]; then
    run_one stack-address-role-controls 120 python3 research/challenge-8/merge/overnight/pointer-prove.py \
      --profile experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1 \
      --scope 'two-pass normal-MIR discovered/reexported IDs for source-named Range/tuple and hidden scalar frontend refusal; no guessed IDs or permissions' \
      --tool-home "$experimental_home" --compiler-sysroot "$compiler_sysroot" --schema "$schema" \
      --fixture "$evidence/stack-address-role-controls/stack-address-control-cases.rs" --evidence "$evidence/checked-stack-role-controls"
  fi
  # The bundled Z3 configuration is unsupported at pointer_ctor sorts in
  # run37759998061; preserve its artifacts, avoid repeating setup failures.
  # Original balanced trace/entry-death evidence is retained in previous runs.
  # Its same reproducible pre-body refusal is not rerun; quartet profile keeps
  # all twelve original coordinates, helper proofs and relations.
  run_one pointer-quartet-trace-entry-negative 120 python3 research/challenge-8/merge/overnight/pointer-prove.py \
    --profile experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1 \
    --scope 'matched full G2 domain and twelve-coordinate result allocation; first-body false assertion, all original helper bodies/posts retained' \
    --tool-home "$experimental_home" --compiler-sysroot "$compiler_sysroot" --schema "$schema" \
    --fixture research/challenge-8/merge/overnight/pointer-trace-quartet-entry-negative.rs --evidence "$evidence/checked-z3-quartet-full-entry"
  run_one pointer-quartet-trace-diagnostic 400 python3 research/challenge-8/merge/overnight/pointer-prove.py \
    --profile experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1 \
    --scope 'same twelve G2 trace coordinates and complete posts in stock tuple3 of tuple4 layout; original balanced tuple profile retained' \
    --tool-home "$experimental_home" --compiler-sysroot "$compiler_sysroot" --schema "$schema" \
    --verifier-seconds 300 --fixture research/challenge-8/merge/overnight/pointer-trace-quartet-cases.rs \
    --evidence "$evidence/checked-pointer-trace-quartets"
  run_one actual-source-preparation 20 python3 research/challenge-8/merge/overnight/actual-prepare.py \
    --output "$evidence/actual-cases.rs"
  if [[ -f "$evidence/actual-cases.rs" ]]; then
    run_one actual-callee-applicability 180 python3 research/challenge-8/merge/overnight/pointer-prove.py \
      --profile experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1 \
      --scope 'unchanged actual merge_up/down diagnostic with full normal/unwind targets; distinct source positive stride writable option destination with explicit C1 domain; genuine normal/unwind loan recovery' \
      --tool-home "$experimental_home" --compiler-sysroot "$compiler_sysroot" --schema "$schema" \
      --fixture "$evidence/actual-cases.rs" --evidence "$evidence/checked-actual"
  fi
  run_one bidirectional-option-stages 120 python3 research/challenge-8/merge/overnight/pointer-prove.py \
    --profile experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1 \
    --scope 'checked exact panic option-stage lemmas and full destination frame; suffix-only negative must reach assertion' \
    --tool-home "$experimental_home" --compiler-sysroot "$compiler_sysroot" --schema "$schema" \
    --fixture research/challenge-8/merge/overnight/bidirectional-stage-cases.rs --evidence "$evidence/checked-bidirectional-stages"
  # Length-two full-body diagnostic is conclusively rejected by mandatory
  # odd/guard dead-code gates in run37759998061. Continue the joint 2/3 domain;
  # same-input stack gates and actual callee bodies remain mandatory there.
  run_one bidirectional-small-source-preparation 20 python3 research/challenge-8/merge/overnight/bidirectional-small-prepare.py \
    --output "$evidence/bidirectional-small-cases.rs"
  if [[ -f "$evidence/bidirectional-small-cases.rs" ]]; then
    run_one bidirectional-len23-diagnostic 400 python3 research/challenge-8/merge/overnight/pointer-prove.py \
      --profile experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1 \
      --scope 'unchanged actual bidirectional lengths two or three; actual callees, complete current source and scratch resources, conditional third cell and exact panic stages; both odd/even branches required' \
      --tool-home "$experimental_home" --compiler-sysroot "$compiler_sysroot" --schema "$schema" \
      --verifier-seconds 300 --fixture "$evidence/bidirectional-small-cases.rs" --evidence "$evidence/checked-bidirectional-small"
  fi
  return "$suite_status"
}

experimental_home="$task_temp/source"
bash research/challenge-8/merge/overnight/build.sh "$tool_home" "$evidence/build" "$experimental_home"

if [[ "$run_mode" == merge_compile_only || "$run_mode" == merge_bridge_minimal || "$run_mode" == merge_len1_minimal || "$run_mode" == merge_caller_composition_minimal || "$run_mode" == merge_selected_drop_minimal ]]; then
  onecell_component="$repo/research/challenge-8/merge/overnight/guard-ownership/insertion-onecell"
  if [[ "$run_mode" == merge_compile_only || "$run_mode" == merge_selected_drop_minimal ]]; then
    export SMALLSORT_MERGE_PROFILE="$repo/research/challenge-8/cloud-build/origin-layout/GLUE-PROFILE.json"
  fi
  candidate_home="$task_temp/verifast-tracked-md-source"
  preparation_evidence="$evidence/tracked-md-build-preparation"
  compile_evidence="$evidence/tracked-md-build"
  set +e
  /usr/bin/time -v -o "$evidence/tracked-md-preparation-resources.txt" \
    timeout --signal=TERM --kill-after=5s 120s \
    bash "$onecell_component/build-profile.sh" \
      "$experimental_home" "$candidate_home" "$preparation_evidence" "$evidence/build" prepare-only \
      > "$evidence/tracked-md-preparation.log" 2>&1
  preparation_status=$?
  set -e
  printf '%s\n' "$preparation_status" > "$evidence/tracked-md-preparation-exit-code.txt"
  cat "$evidence/tracked-md-preparation.log"
  (( preparation_status == 0 )) || exit "$preparation_status"

  set +e
  /usr/bin/time -v -o "$evidence/tracked-md-compile-resources.txt" \
    timeout --signal=TERM --kill-after=10s 1200s \
    bash "$repo/research/challenge-8/cloud-build/origin-layout/compile-preflight.sh" \
      "$candidate_home" "$compile_evidence" \
      > "$evidence/tracked-md-compile.log" 2>&1
  compile_status=$?
  set -e
  printf '%s\n' "$compile_status" > "$evidence/tracked-md-compile-exit-code.txt"
  cat "$evidence/tracked-md-compile.log"
  (( compile_status == 0 )) || exit "$compile_status"
  [[ "$run_mode" != merge_compile_only ]] || exit 0

  # Same required retained-six ordinary normal/unwind smoke on its own binary.
  # This is a six-patch profile, not six new consumer cases.
  python3 "$repo/research/challenge-8/merge/overnight/pointer-prove.py" \
    --profile experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1 \
    --scope 'mandatory retained-six ordinary normal/unwind smoke before minimal bridge' \
    --tool-home "$experimental_home" --compiler-sysroot "$compiler_sysroot" --schema "$schema" \
    --fixture "$repo/research/challenge-8/merge/overnight/baseline-cases.rs" \
    --cases ordinary_call_normal_unwind --evidence "$evidence/checked-profile-smoke" \
    > "$evidence/retained-six-smoke.log" 2>&1
  python3 - "$evidence/checked-profile-smoke/aggregate.json" <<'RETAINEDSMOKE'
import json,sys
x=json.load(open(sys.argv[1]))
assert x['cases']=={'ordinary_call_normal_unwind':'PASS'} and x['classifier_controls_passed'] is True
RETAINEDSMOKE
  export SMALLSORT_GLUE_OBSERVATION_DIR="$evidence/compiler-glue-observation"
  profile_name=experimental-merge-qualified-guard-onecell-v1
  [[ -z "${SMALLSORT_MERGE_PROFILE:-}" ]] || profile_name=experimental-merge-actual-glue-observation-v5
  proof_campaign=bridge-minimal-v1
  [[ "$run_mode" != merge_len1_minimal ]] || proof_campaign=len1-minimal-v1
  [[ "$run_mode" != merge_caller_composition_minimal ]] || proof_campaign=caller-composition-minimal-v1
  [[ "$run_mode" != merge_selected_drop_minimal ]] || proof_campaign=selected-drop-minimal-v1
  python3 "$onecell_component/prove.py" \
    --profile "$profile_name" \
    --profile-evidence "$compile_evidence" --tool-home "$candidate_home" \
    --compiler-sysroot "$compiler_sysroot" \
    --schema "$candidate_home/src/rust_frontend/vf_mir/vf_mir.capnp" \
    --evidence "$evidence/checked-minimal-bridge" --campaign "$proof_campaign" \
    > "$evidence/minimal-bridge.log" 2>&1
  exit 0
fi

export LD_LIBRARY_PATH="$compiler_sysroot/lib:$experimental_home/bin:/tmp/vfdeps-adf88dc/lib:${LD_LIBRARY_PATH:-}"

export evidence task_temp tool_home experimental_home compiler_sysroot schema suite_status
export -f run_one suite
printf 'Setup/build elapsed=%ss; suite bound=900s; whole step bound=1700s.\n' "$((SECONDS-job_started))" | tee "$evidence/suite-budget.txt"
set +e
/usr/bin/time -v -o "$evidence/resources.txt" timeout --signal=TERM --kill-after=5s 900s bash -c 'suite' \
  2>&1 | tee -a "$evidence/execution.log"
suite_status=${PIPESTATUS[0]}
set -e
printf '%s\n' "$suite_status" > "$evidence/exit-code.txt"
exit "$suite_status"
