# KANI3300 C1-L — coordinator-only compile request / PREPARED_NOT_RUN

One future authorized coordinator job, six independent inputs from CASE-MANIFEST.json.
Cloud spend in this preparation session: $0; no dispatch, workflow publication or Kani push.
This request is not permission to start CI. Stop after preparing/publishing this research package.

## Exact sources and setup

Baseline: `a0a2386001a15fecfe2facc2f6cd87f3dee13b60`.
D0-PR diagnostic: `5eec235e3d0eeb99d7e432fcaef3a3135747b789`.
Compile-only adapter: `6d35d2f55052762ccc7555db1e8c12e32047091d`, tree
`1f74038dbedb683b2384b78bc36e020891f5e501`, local `/root/kani-fix-3300-c1l`,
branch `diagnostics/kani-3300-c1l`. The adapter is UNPUSHED; preserve this commit identity.
`diagnostic-adapter.patch` is the zero-context binary diff from exact D0-PR to adapter;
if applying require exact parent and `git apply --unidiff-zero`;
its SHA256 is in CASE-MANIFEST.json. Reapplication under another SHA requires rebinding.
Input research commit: `d8d3e6d4ca675c9734d6ce140890bc478daf0b43`; six original bytes/hashes
are pinned in individual `cases/CASE/manifest.json`, unchanged and not declared compile-ready.
No M0/B1/B3 model commits; this is baseline lowering evidence, not B1I-A/release acceptance.

Use the existing coordinator preflight/build lane with its phase/owner/ledger/budget controls.
Build the exact adapter by the existing `cargo build-dev -- --release` procedure, CI ONLY.
No original D0 A/B reruns, paired/order cases, flat whole-copy inputs, baseline reruns or retries.
The old D0 workflow/run.py cannot be used unchanged: it always installs solver capture, probes
solver versions and requests verification/trace/export-json. Do not copy it or its capture shim.
The existing compiler-child supervision capability must record actual wait status separately
from driver/linker status. D0's compiler_supervisor.py imports capture_cbmc and is not a
standalone compile-only launcher: do not copy that coupling. No new runner framework is supplied.

Before the first case, freeze `setup-identities.json`: exact source/tree, patch/input/config hashes;
full rustc -vV/commit, target-spec JSON SHA256 and exact data-layout; pointer width64/little endian;
SHA256/bytes/absolute path/build provenance for kani, actual kani-compiler, rustc, goto-cc,
kani_lib.c, Kani libraries and immutable Rust sysroot. CASE-MANIFEST pins nightly-2026-10-23,
compiler7189d39d9ce936881b8132c6addeaf3e295cd455, target x86_64-unknown-linux-gnu and the
D0-A immutable Rust/Kani sysroot manifest digests. Use their exact manifest serialization/artifacts;
missing/mismatched immutable pins STOP setup. Library sources are unchanged. No source SHA
substitutes for a binary SHA. New binary/layout fields are deliberately SETUP_FREEZE_REQUIRED,
not invented; no case may run with null/placeholder identities. Bind setup-file SHA to every case,
and compare executable/sysroot hashes before/after each. If the old immutable artifacts cannot
be reused, report the exact mismatch; do not silently weaken/re-pin these setup guards.
Record actual CPU affinity/export workers, address-space/CPU limits and wall timeout. Build timeout
2400s, each case600s; no retries or cap escalation. Timeout kills/reaps the whole process group
and preserves child exits/signals/partial files. Missing actual compiler-child exit is UNKNOWN/STOP.
No CBMC/Kissat/goto-instrument invocation, even version probes, is requested. goto-cc is a linker,
not the solver. Require a coordinator process-execution receipt with solver exec count zero;
accidental solver execution STOPs that case even if the driver exits0.

## Per-case recipe (not executed here)

`CONFIG.json` is authoritative for the exact argv/env templates and canonical config digest.
Resolve KANI, FIXTURE, OUT to absolute paths and record expanded argv without shell reinterpretation.
For each of the six explicitly enumerated cases, independently: verify original fixture SHA;
create a fresh `${OUT}/${CASE}`; compile the entire one-harness file in a fresh process/cache.
Do not concatenate inputs, mutate fixtures, rewrite harnesses or guess promoted AllocIds.

```bash
# CASE and FIXTURE come from its pinned manifest; KANI/OUT from frozen setup.
RUSTFLAGS='--emit=mir --edition=2021 --target=x86_64-unknown-linux-gnu' \
KANI_C1L_CASE="$CASE" KANI_C1L_DIR="$OUT/$CASE/compiler" \
"$KANI" "$FIXTURE" --crate-name c1l_input \
  -Z uninit-checks -Z unstable-options --only-codegen --output-format regular \
  --keep-temps --target-dir "$OUT/$CASE/model" \
  --harness "$CASE" --exact
# Supervisor persists the original driver, compiler and linker exits/signals separately.
```

Reject inherited extra Kani/driver/compiler flags, configs or tracing, including the env keys in
CONFIG.json. No export-json, cbmc-args/trace, no-slice-formula, --tests, automatic/public-function
mode, playback, compiler optimization/order override, fresh transformer intervention or model repair.
The pinned standalone driver builds `standalone_project`, links through `Project::try_new` /
`link_goto_binary` using goto-cc, then returns on `only_codegen` BEFORE `verify_project`.
This bypasses verification/property/solver reporting, not linking. The target triple passes through
RUSTFLAGS/base_rustc_flags (standalone Kani has no --target CLI). SOURCE-API.json pins this path.
Actual metadata and compiler unit must each contain exactly the requested singleton root,
Harnesses mode, one unit/cache, no stubs/test/automatic roots. Record pretty and actual mangled
name plus metadata/model file SHA256, case/PID/unit/cache and observed native ordering. Extra or
missing roots STOP. Two or more roots/prewarm/order controls are outside this request.

## Required compiler packet and coverage

`OUTPUT-CONTRACT.json` defines required fields, joins and admissible classifications. Per case:

1. Original and codegen-consumed MIR for the exact root and, for helper cases, local `compare`;
   root/helper Instance identity, symbol, original/consumed snapshot hashes and source coordinates.
   `--emit=mir` original output gets file SHA/bytes; curate only relevant function ranges and their
   byte offsets/hashes. Full sysroot MIR/whole GOTO bodies are excluded from the handoff.
2. Retained raw_eq call/site/specialization `[MaybeUninit<u8>;3]` and operand indices0/1. Bind
   caller local/constant → helper formal0/1 where applicable → raw_eq operand → injected CheckAs
   → actual full-byte layout/mask111 → consumed get::<3> and assertion CFG → GOTO local/call symbols.
   Keep both checks separate by operand expression and block/location, never by property suffix.
   No CBMC property ID/status/trace is required or fabricated. Unsupported or eliminated raw_eq
   must be explicitly located and classified, not counted as a successful legal/negative test.
3. For each operand, actual storage origin and referent: GlobalAlloc kind/AllocId, mutability,
   original Some(value)/None per byte, provenance relocation entries and derived spans using the
   pinned pointer width, allocation extent/alignment, pointer offset and selected extent. Bind
   referent-before → branch-kind → allocation-before → allocation-symbol/reuse → referent-symbol,
   source/consumed MIR operand and GOTO symbol. Record both sides even if they coalesce. Compiler
   opaque IDs stay in their own namespace; never identify them with runtime object numbers.
   Allocation mask must come from the actual Allocation before None→zero backend conversion.
4. Delayed-activation records bind case/PID/root/phase and existing target/start/instance counts.
   targets=0 yields EMPTY/NOT_ACTIVATED, with graph/instrumentation phase NOT_ACTIVATED for this
   invocation. Nonempty yields ACTIVATED, with graph details intentionally FILTERED_OUT_OF_SCOPE.
   No graph is synthesized. No conclusion about writes/setters follows from a skipped/filtered phase.
5. Include emitted/dropped/filtered/attempted/bytes counters, stage+instance expectations and
   field-level coverage with exact source record IDs/SHA/JSON pointers or byte/line coordinates.
   Reconcile each retained file with counts and scope, including all compiler PIDs and finish
   coverage files. A count alone does not establish a binding or completeness of an operand chain.

Adapter filters before payload evaluation: root/compare MIR and operations; selected operand/check/
allocation/local/terminator stages; relevant type names. No sysroot bodies/full points-to graphs,
repeated local-pass snapshots, solver infrastructure, runtime witness or new memory operations.
Allocation sidecars attach the existing current function where available; unscoped records need
an explicit operand join, and cannot alone establish completeness. Inspect coverage before claiming
an AllocId is absent. If the actual complete chain shows Stack/aggregate instead of immutable
promotion, report LOWERING_MISMATCH and N/A allocation fields with the positive stack binding.
Absence without complete coverage is UNKNOWN/INCOMPLETE. Observed fields remain separate from
EXPECTED-BINDINGS.json source expectations; do not rewrite the input to force promotion.

Per-case packet cap512KiB including sidecars, report, roots/manifest/exits/coverage; observer event
budget448KiB (including serialized envelopes), payload64KiB, records2048. The remaining64KiB is
reserved for per-case metadata. Shared curated metadata≤1MiB; complete curated packet≤5MiB.
SHA/byte references to private build/model artifacts do not authorize later raw downloads. Missing,
capped/dropped required data or a required type/operand filtered out => STOP affected case and
emit an incomplete coverage report. If required data cannot fit, STOP before that case's launch
with a precise filter/packet revision; no automatic cap growth, hidden truncation or another run.
A setup failure still receives a bounded case manifest/exits with later stages explicitly NOT_RUN.
No full compiler logs/raw archives/GOTO listings/solver traces go into research Git or handoff.

Keep setup, build, compiler, linker, driver and curation outcomes separate, original nonzero exits,
signals/timeouts and errors intact. Distinguish SETUP_FAIL, COMPILE_FAIL, UNSUPPORTED,
INCOMPLETE_REPORT and CODEGEN_SUCCESS; lowering suitability is a separate field.
Codegen success is not legal verification SUCCESS. Hole spelling is not measured uninitialized
failure. All runtime initializedness, reached properties, solver status and proof credit remain
NOT_RUN/false. No CI PASS claim is made. New compile facts require coordinator CI and a later
analysis session. No extractor is supplied or locally run against raw CI inputs.
