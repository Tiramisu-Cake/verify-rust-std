# S4 exact coordinator CI request — NOT_RUN

Preparation only: no dispatch/phase/budget/publication authority. Use existing
coordinator/preflight and accepted pins; no local build request. Candidate source
SHA/tree is in INPUTS.json and RESULT.md. Baseline is ad324418cdc66b18e9b71f76a412be6ccea20c7e
plus baseline-tests.patch, expected tree in expected-baseline-tree.txt. Validate
base/tree/patch and each BASELINE-PACKAGE.json blob before building. Only the
five observer/test/document files may differ on baseline. Do not use bf8170b28.
If CI-only overlay is required, record source SHA/tree and overlay SHA/tree
separately, with workflow-only diff. Never import SEL1.

1. Existing preflight, fmt, candidate build/type/borrow check and clippy.
   Preserve nightly-2026-10-23, CBMC 6.11.0, Kissat 4.0.1 (validate actual pins,
   do not silently substitute). Local formatter used only the requested wrapper;
   coordinator may run its established CI fmt check. Run default cprover checks
   and compile the touched optional LLBC path via the existing cprover+llbc
   build lane. Do not start unrelated LLBC proof work.
2. Candidate native lifecycle controls in its normal compiler test environment:
   `cargo test -p kani-compiler delayed_cache::tests -- --nocapture` (6 tests),
   `cargo test -p kani-compiler delayed_scope_tests -- --nocapture` (2 tests).
   Require exact first original/non-Clone value/modified flag restoration,
   current replacement visibility, untouched/warm/new regular retention,
   absent-root removal, repeated/empty scope, rejection of invalid lifecycle,
   and normal/early-return/unwind guard reuse. Preserve
   `cargo test -p kani-compiler immutable_allocations::tests` (S2 unit9).
   Add unchanged existing no-uninit/PubFns and contract/loop smoke controls via
   their current suite profiles; empty journal must not alter those outcomes.
3. On EACH baseline and candidate binary, separately invoke from its checkout:
   `python3 tests/json-handler/uninit-part1-composition/run.py --kani <absolute-matching-kani> --collect-unbound --keep-output`.
   Retain original observer exit **2**, UNBOUND_CAPTURE, NOT_CHECKED_CAPTURE;
   it is not a green regression job. Fresh observer must finish all 11 Kani
   invocations below (each fresh process, --jobs 1, unique target/export,
   timeout 180s unchanged). A different exit or incomplete capture is not an
   isolation comparison. Do not reuse outputs or old C1b inventories.

| Invocation | Exact --harness selectors in CLI order | Expected Kani exit |
| --- | --- | --- |
| isolated-immutable_legal | immutable_legal | 0 |
| isolated-immutable_hole_negative | immutable_hole_negative | 1 |
| isolated-ordinary_ensures_legal | ordinary_ensures_legal | 0 |
| isolated-pfc_legal | pfc_legal | 0 |
| isolated-pfc_negative | pfc_negative | 1 |
| isolated-cycle_root | cycle_root | 1 |
| isolated-unrelated_legal_after_cycle | unrelated_legal_after_cycle | 0 |
| all_A_then_B | immutable_legal, immutable_hole_negative, ordinary_ensures_legal, pfc_legal, pfc_negative, cycle_root, unrelated_legal_after_cycle | 1 |
| all_B_then_A | unrelated_legal_after_cycle, cycle_root, pfc_negative, pfc_legal, ordinary_ensures_legal, immutable_hole_negative, immutable_legal | 1 |
| cycle_then_legal | cycle_root, unrelated_legal_after_cycle | 1 |
| legal_then_cycle | unrelated_legal_after_cycle, cycle_root | 1 |

For each selector pass --harness separately, then --exact. Exact full argv
construction, flags and expected root lines/modes/verdicts are in
CONTROL-MANIFEST.json. Both lanes use RUSTFLAGS="--edition 2021 -D warnings",
NO_COLOR=1, four unstable features (uninit-checks, function-contracts,
export-json, unstable-options), output-format=regular, object-bits12, default
solver and all normal safety/overflow/unwind/undefined/reach/contract checks.
No alternative check suppression or global object-bits override. Preserve
actual effective argv/environment and source hash before/after per invocation;
record exact source/tree and binaries (kani driver, compiler, CBMC, solver),
toolchain and hashes in a lane receipt. Existing runner records argv/source/
exports/output hashes and original exits; coordinator must supply tool and
environment identity alongside it, including export-worker availability/CPU
configuration when known. Both lanes must have identical inputs and flags.

4. Before attributing accumulation, validate actual unit membership and shared
   std::ptr::read::<u8> Instance/model identity for the ordinary roots. Existing
   CodegenUnits::new debug event can supply bounded unit membership, e.g. same
   narrow KANI_LOG=kani_compiler::kani_middle::codegen_units=debug on BOTH lanes;
   retain that bounded event and its identity mapping, without a whole-log
   download. Actual producer order, when a bounded receipt is available, must
   be reported separately from selector/JSON/verifier-output order. With no
   actual receipt report NOT_ESTABLISHED; never relabel CLI AB/BA as observed.
   Do not modify compiler ordering, unit configurations or model semantics.
5. Baseline: examine all 18 comparisons of each mixed root against its OWN fresh
   isolated root. Require at least one actual addition of delayed operations/
   checks on a shared root, with retained exact rows and source mapping back to
   the real u8 read. Check description/class/location/status and reachability;
   use model/operation binding where available. Legal SUCCESS is compatible
   with the required accumulation. Historical 3/6/9 additions are not evidence
   for this baseline. If exact, different-unit, unreached, unrelated early guard,
   timeout, or incomplete output: NONDISCRIMINATING/UNREPRODUCED, return a bounded
   revised source/callee/unit request rather than crediting S4.
6. Candidate: require all 18 comparisons accepted=true, exact_match=true,
   differences={}, mixed_root_oracle=EXACT_MATCH, with the same per-root full
   check multiset (including SUCCESS and UNREACHABLE), failures with every
   metadata field, Unsupported, useful checks/covers, verdict, failure_kind,
   n_failed and complete counters. Check N print ordinal is not identity.
   Existing checkout/toolchain-prefix normalization only; no description,
   class, status, location meaning, or failure normalization/allowance.
   Also compare every candidate isolated root with the corresponding baseline
   isolated root: retain the full multiset and payload. Candidate mixed may
   remove only the baseline's mapped accumulated duplicates, never an isolated
   required check. No verdict-only or failures-only acceptance.
7. Preserve S2 immutable19/unit9 and S3 nested-aggregate-reset two intended
   single-failure negatives and reinit SUCCESS. Run their unchanged expected
   selectors and top-level move/pairing/argument/typed-return, ordinary-slots,
   unresolved-calls, closure-upvars, transfer-qualification, cycle/PFC/contract
   controls with original per-fixture flags. Any unexpected lost check, new
   status/payload/failure/Unsupported or mode regression blocks acceptance.
8. After lifecycle/target controls, accepted Quick: kani Uninit/Quantifiers/
   TailCall; expected uninit/quantifier-capture/arbitrary; ui quantifier-safety-checks/
   explicit-tail-calls*; script-based-pre mem-init-reinstrumentation/
   autoharness_explicit_tail_call; JSON uninit-contract-oracles and
   uninit-contract-mode-boundaries; existing required trailing stages.
   Run ordinary bound composition separately, retain original exit/status.
   Its known stale-binding FAIL can remain S5 debt; exact fresh isolation may
   pass separately. ordinary_ensures_legal's two real #5093 SUCCESS overflow
   assertions stay present. Do not bless roots.json, serialize new goldens,
   add allowances, remove suites, or report all-PASS Quick after diagnostic FAIL.

After authorized execution use the established evidence interface, preserving
B1/B2/source-reported vs independent credit. Record structural status, observed
order status, exact fresh-isolation status and legacy JSON debt separately.
Full three-platform Gate A waits for S5/S6/freeze. S4 is not accepted until its
new distinguishing baseline, candidate/native checks and required CI pass.
