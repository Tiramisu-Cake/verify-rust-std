# KANI3300 D0-P — coordinator-only fork CI request

Prepared source: baseline `a0a2386001a15fecfe2facc2f6cd87f3dee13b60`; diagnostic `955cd015649aa79be511fe1732d48fdc8535741f`; diagnostic tree `1c724bf33763251340efbdf9a8486a6278cafdc4`.
Local candidate `/root/kani-fix-3300-d0`, branch `diagnostics/kani-3300-raweq-d0`, UNPUSHED.
Only the coordinator may publish this exact SHA to its Kani fork and start the existing fork workflow.
Research publication stopped on concurrent g0 HEAD `adc8ecab69`; see HANDOFF.json for the isolated local research commit destination.
No workflow/source/model repair is included. Cloud budget is $0. No command below was executed here.
Full diff: `diagnostic.patch`, SHA256 `027634fa0c0f84c8b7d39d69904f0c032e6c9984dac63a78a90b955f7f65972b`. Publication must preserve the candidate commit identity;
coordinator can read the local clone directly. Reapplying a patch with a different commit is a new identity, requiring rebinding.

## Fixed inputs and setup gates

- Whole original `tests/expected/uninit/maybe-uninit-initialized/main.rs`, SHA256 `df6292d1fdc472cb41e6e7d707a6bc4f8b190a3f206a7f208e635a8d0b5f9e5c`; `fixture-main.rs` is an exact archival copy, not a new test.
- Rust `nightly-2026-10-23`, compiler commit `7189d39d9ce936881b8132c6addeaf3e295cd455`.
- CBMC/goto-instrument `6.11.0`, Kissat `4.0.1` (`kani-dependencies`). Standard default solver selection unchanged.
- Target Linux `x86_64-unknown-linux-gnu`, 64-bit pointers, little endian. Record actual full rustc -vV, sysroot manifest,
  target/data-layout string, machine model, CPU affinity/export workers, available memory/time limits, compiler/driver/solver binary hashes.
  Version labels alone do not pin sysroot/binary identity: mismatches or missing pins are STOP setup, never a result.
- Use the existing fork build procedure at each exact SHA (standard `cargo build-dev -- --release`, CI ONLY),
  with identical immutable Kani/Rust sysroot artifacts and build options. No B1I source or workflow patch in candidate.
- At least two available CPUs/export workers for all paired cases. Original normal prewarm must be present;
  no fresh transformer/cache reset, no reordered prewarm, no changed harnesses, no guessed order from CLI/text.
- Allowed diagnostic env: `KANI_D0_DIR` (fresh absolute case-private directory), `KANI_D0_CASE` (A/B/AB/BA/D),
  `D0_REAL_CBMC` (absolute pre-shim CBMC path, SHA256 pinned), `D0_CAPTURE_DIR` (case-private CI-only retained JSON).
  Do not collect the general environment. Reject inherited KANI_LOG/extra flags/config; record only explicit input argv and allowlisted fields.
- `capture_cbmc.py` is a Linux CI-only PATH shim called `cbmc`; it neither adds options nor changes stdout.
  Install its symlink in a fresh directory at the head of PATH after recording the real executable path/hash.
  Require completed capture metadata, no signal, captured_complete=true and dropped_bytes=0 before curation.
  capture_state!=COMPLETE or wrapper_signal/child_signal!=null, RUNNING/timeout/cap/missing metadata means INCOMPLETE, regardless of a result prefix.

## Four requested cases and controls

| case | exact manual compiler roots | actual codegen order | process/cache policy |
|---|---|---|---|
| A | `array_value_as_used_by_merge_output` | singleton | fresh compiler process, one unit/cache |
| B | `partial_copy_preserves_written_byte` | singleton | fresh compiler process, one unit/cache |
| AB | same A+B | A then B | one process/unit/shared transformer, unchanged normal prewarm |
| BA | same A+B | B then A | same input/options/prewarm policy as AB, override only after normal order |
| D control | same A+B | native computed order, no override | diagnostic duplicate, normal prewarm |

Each invocation compiles the whole unchanged file; `--harness`/`--exact` reach the compiler and filter roots before grouping.
The unit's root set has size two in AB/BA/D; each original codegen/global-pass invocation still starts from one harness.
Do NOT change `starting_items` to a joint pair, which would change the model. Per-root prejoin graphs and final graphs refer
exactly to those existing invocations, associated with unit/cache identity.

Coordinator recipe (paths KANI, OUT, RESEARCH resolved and recorded in identities.json; execute from exact Kani checkout):

```bash
A=array_value_as_used_by_merge_output
B=partial_copy_preserves_written_byte
FIXTURE=tests/expected/uninit/maybe-uninit-initialized/main.rs
export D0_REAL_CBMC="$(command -v cbmc)"
mkdir -p "$OUT/shim"
ln -s "$RESEARCH/capture_cbmc.py" "$OUT/shim/cbmc"
export PATH="$OUT/shim:$PATH"
```

Use the following argv template once per row. `CASE` selects A, B, AB, BA or D; `SELECTORS` is the exact array below.
AB/BA/D use identical selector ORDER A then B; changing CASE changes only the authorized diagnostic order control.
Do not use glob/substr selectors, `--tests`, automatic/public-function mode, playback or compact traces.

```bash
# A:  SELECTORS=(--harness "$A" --exact)
# B:  SELECTORS=(--harness "$B" --exact)
# AB, BA, D: SELECTORS=(--harness "$A" --harness "$B" --exact)
# Set CASE and SELECTORS explicitly for each invocation, fresh OUT/CASE.
if RUSTFLAGS='--emit=mir --edition=2021' \
  KANI_D0_CASE="$CASE" KANI_D0_DIR="$OUT/$CASE/compiler" \
  D0_CAPTURE_DIR="$OUT/$CASE/cbmc-private" \
  "$KANI" "$FIXTURE" -Z uninit-checks -Z unstable-options --no-slice-formula \
  -Z export-json --export-json "$OUT/$CASE/results.json" --output-format regular \
  --keep-temps --target-dir "$OUT/$CASE/model" --verbose \
  "${SELECTORS[@]}" --cbmc-args --trace
then KANI_EXIT=0; else KANI_EXIT=$?; fi
# Persist KANI_EXIT as original verification exit; propagate it after artifact collection.
# Keep setup/compiler/each solver/verification/curation exits SEPARATE. No `|| true`/generic green expected-fail wrapper.
```

`--no-slice-formula` is the same diagnostic solver option for every case and baseline comparison; no omitted checks.
The CLI supports the above flags at the pinned source. `--export-json` stores property summaries/trace_available, not full trace.
The shim preserves original solver stdout JSON, exits and signals for coordinator-only curation; stderr is not archived by it.
Observe the compiler process exit with the existing coordinator process supervisor (wait status of the actual compiler child);
`*-coverage.json` confirms codegen completion only, not compiler process/link completion. If no exact exit is available, mark UNKNOWN/STOP.
No internal timeout may leave a solver running: Linux capture shim sets parent-death SIGKILL and forwards catchable signals.
No retry under different options is authorized by this request.

Run matching baseline singletons/pair with the same command/options/fixture, unmodified `a0a2386001a15fecfe2facc2f6cd87f3dee13b60` compiler,
unset `KANI_D0_DIR`/`KANI_D0_CASE`; capture uses the same shim. Compare pair baseline to D, and singleton baseline to A/B.
Also a candidate invocation with observer env absent can separate source packaging from enabled observations if needed.
All baseline/diagnostic runs use exactly the same bounds/checks/sysroot/solver flags. Native order may vary because grouping
uses HashMap: record actual AB/BA prewarm sequence/root identities, workers and actual loop order and require a matched prewarm.
If prewarm differs, STOP matched causal/cache inference, report the mismatch; do not silently choose/reset cache or reorder roots.

## Required private artifacts and curated handoff

`identities.json`: full source baseline/candidate/tree/diff/fixture hashes, actual tools/sysroot/layout/binary pins, build recipe,
explicit argv, allowed diagnostic values, limits. For each case, `cases/CASE/manifest.json` must carry these identities plus
actual roots (pretty+mangled), unit=0/cache=0 qualified by source/case/compiler PID, actual prewarm+normal+actual codegen sequences,
per-stage original setup/compiler/solver/verification/curation exit or explicit NOT_RUN/timeout, and complete property inventory.
Missing/extra roots, stubs, non-Harnesses mode or multiple units are compiler diagnostic assertions and STOP.

Compiler sidecars are `compiler/PID-SEQUENCE-STAGE.json`, unique create_new files; coverage `PID-coverage.json`.
The schema/source anchors and per-operand NOT_RUN rows are in DIAGNOSTIC-MAP.json. Keep SHA256/bytes of each sidecar;
`payload_fingerprint` is FNV1a64 structural change detection, NOT an integrity hash. `cache_writer=[version,writer_root,body_fingerprint]`
attaches to consumer records for the exact body instance; hash local/write/read/consumed opaque MIR payloads consistently.
MIR snapshots serialize existing Ty/Span indices. They do not recursively format Ty::Debug before transformations.
`type-codegen` relates already-consumed type indices to normal backend types. Resolve source spans via normal emitted MIR/GOTO;
no extra body query or reconstruction for formatting. Preserve IDs as process-local, not runtime object IDs.

Required stages for BOTH roots and exact retained `SpecArrayEq::spec_eq<[u8;4]>` (determine actual Instance/name, do not assume spelling):
original MIR; every local before/after including UninitPass; delayed before/after or explicit no-seed status; cache writer/consumer;
actual codegen-consumed body; both raw-eq-operand indices/places/projections; each CheckAs/op/result/layout/call destination/normal edge;
per-root graph before join, joined graph/seeds/successors; every candidate get/set relevance and rejection predicate for needed places;
constant reference value separate from referent AllocId/offset/bytes/None mask/relocations/mutability; allocation symbol/reuse;
shadow Set/SetStorage/Copy/StoreArgument/LoadArgument operations, effective masks/ranges, insertion sequence and generated normal edge.
The field-insensitive graph is not an offset proof. The pre-backend `None` mask is not the zero-filled backend value.
`alloc_map` can coalesce equal allocations; retain requested AllocId and actual returned GOTO symbol.

For exact property IDs/source/GOTO PC binding on each actual solver input, CI ONLY:

```bash
"$D0_REAL_CBMC" --show-properties --json-ui "$GOTO_INPUT" > "$PROPERTY_JSON"
"$GOTO_INSTRUMENT" --show-goto-functions --json-ui "$GOTO_INPUT" > "$GOTO_FUNCTIONS_JSON"
```

Record their original exits/hash and confirm that read-only inventory shows the same IDs as solver JSON. These flags are audited
in CBMC 6.11.0 sources (API-SOURCES.json). Curate only relevant function/operand/assertion edges for handoff, preserving PC/labels.
Bind each check through actual boolean result/call operands/inserted MIR edge/GOTO assertion/PC, then actual property inventory.
Never infer operand from the .1/.2 suffix or from source/CLI order alone.

For each solver invocation, wrapper creates private `<uuid>.json` and `<uuid>.meta.json`. Require capture status COMPLETE,
child_exit recorded (0/10, others resource/error), child_signal=null, captured_complete=true, dropped_bytes=0; compare SHA256.
Do not give these full private JSON traces/full GOTO listings/full logs to the D0-A agent. Produce targeted curated artifacts in CI.
`curate_cbmc_trace.py CBMC_JSON manifest.json bindings.json -o curated.json` consumes only exact hash-bound JSON, independently
preserves original exits/status, exact property/source-stage-target bindings and original trace ordinals. `bindings.json` schema:
identity={source:full_diagnostic_SHA,stage:"solver-json",target:"CASE:harness:solver-input-SHA256"}, expected_trace_sha256,
properties[property_id]={property_id,source,stage,target,cbmc_source_location:{file,function,line[,column]},goto_binding:exact_PC_chain,
trace_lhs:{raw_eq_operand:[exact_LHS],shadow_state:[exact_LHS],pointer_witness_transition:[exact_LHS]},required_trace_lhs:[exact_LHS]}.
Bind every result property (successes need static binding only); extra failures/unknown properties STOP. The original manifest carries
identical identity/hash and original_exits={solver:actual_exit,verification:actual_exit,cbmc_status:actual_status}.
Curation exit2/partial/missing/null/wrong-type/mismatched identity/hash/required witness/cap is INCOMPLETE, never a negative setter fact.

For EACH failing raw_eq property return a targeted witness row:
`source operand -> source AllocId or stack origin -> GOTO symbol -> actual runtime pointer object+offset+extent -> selected tracked
object+offset+value -> last EXECUTED initialization/shadow transition`, with source/GOTO PC and original trace ordinal references.
Include object/offset/range/mask/value for all executed affecting Set/SetStorage/Copy/Store/Load operations and initial false state.
The curator selects actual records; it does not decode pointer identities from names or establish the last writer by itself.
Coordinator must bind actual values and transitions from complete trace/model data, or mark each unavailable field UNKNOWN and STOP causal claim.
No additional runtime probes/state writes are authorized to fill an optimized-out field. A trace of one witness is not all-path proof.
For each SUCCESS raw_eq property provide static operand/property binding, runtime fields N/A (no successful counterexample invented).

Every curated object/report includes emitted/dropped/filtered counts, coverage by phase/root/Instance/property, original indices,
source/file/index/request identity and SHA256. Caps: compiler 20,000 attempts, 4 MiB payload/event, 64 MiB serialized total;
CBMC retained prefix 64 MiB; curated report 1 MiB/2,048 selected records/16 KiB record/1,024 properties. Any required missing/capped
phase/symbol/result is UNKNOWN. Ask for a precise new targeted packet in D0-A; no automatic full dump or raw archive fallback.

## Stop/acceptance gates

- Setup/compile failure, timeout/OOM, unknown exit, wrong identity/root/unit/order/prewarm/coverage: STOP affected comparison.
- D vs baseline: compare full per-harness property sets and original/final/consumed normalized MIR/GOTO. Normalize only absolute
  output paths and proven alpha-renaming; changes to checks/masks/constants/signature pairing tokens/edges/semantics STOP/redesign hooks.
  Property/body/model equivalence is NOT_RUN before CI; no source-level review substitutes for this control.
- Expected raw_eq verification FAIL must remain visible with original nonzero exits and per-property verdicts. Do not label a
  workflow green/PASS merely because the known failure occurred. Reference .2 FAIL/.1 SUCCESS is not a new measured expectation proof.
- Return only curated report and exact identities/coverage to coordinator, then separately issue D0-A. No model fix/M0/future task now.
