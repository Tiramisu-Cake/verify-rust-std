# Coordinator handoff — R7 G1 then G2, all outcomes NOT_RUN

Worker15: Cloud $0, dispatch0, no local compiler/verifier/build, no Kani push or workflow/runner
change. This package is SOURCE_READY only after REVIEW.md; neither build nor solver admission.
Use the existing coordinator and preserve owner/phase/slots/T0/deadline/budget/ledger restrictions.
Exact source SHA/tree, patch/dependency hashes and composition are in SOURCE/TEST-MANIFEST.json.

## Matched inputs and source choices

B0 c614dba9ca7388e098f606231dde7af4b23a06b5 (current full chain + exact bootstrap skip).
B1 b4eb8294b74f3b6448ccccacbc87bdea71d67510 (B0 + separate snapshot / scalar private targets).
Neither is the old R1 control or CI-only filtered tree. Exact reviewed worker14 new-path delta
is now composed locally on both endpoints: B0 ce5d0a8d18e98d9acbc0f49d46488fdf9a5ab27c,
B1 8e01eb2aff5183c53403e1d1e73e573ce28d3095. Shared full tests tree
f7e3cff5b460b8024524a0bb6b1cfc1c31a592cb. Only four new test files; production subtrees unchanged.
Use these composed commits for matched G1; never replace production with the test base.
Record source commit/tree, full test tree, composed CI tree, wrapper/workflow commit and actual
tool/binary identities separately. Preserve all existing fixtures/goldens, including heavy pair.
Actual effective argv/env/host/target/sysroot/toolchain/object widths/CBMC/solver/inlining/slicing/
unwind/PFC settings remain UNKNOWN until captured by the coordinator's existing bounded receipts.

P1: tests/expected/uninit/private-transfer-frame/scalar-pfc-legal.rs, root
postcondition_reads_initialized_return; SHA256 fe05e646b2ccc9188d073b78b30abecd59eb877b6298abfcdfc8a27aeb3a260b.
P2: existing tests/expected/uninit/transfer-qualification/postcondition-hole.rs, root
postcondition_reads_returned_hole; SHA256 61fc369a6830c6ff185887b04db36139ca529e4de097c0025ce7b29c8323f759.
Both use edition2021/-Dwarnings and -Z uninit-checks -Z function-contracts --output-format=regular.
Keep the same actual flags/tools/checks for B0/B1. No changed expected verdict to fit prior failures.

## G1 — build before solver, one root/process

1. Build/fmt/clippy exact composed B0/B1. Compiler/lint/setup failure => solver NOT_RUN;
   rustfmt and Luna review are not compilation. No local substitute or speculative retry.
2. Run unchanged P1 on each, one root/compiler/solver at a time, existing timeout300s and
   RSS watchdog>6GiB, same measurement scope/sampling/overshoot and original exits/signals.
3. Bind actual reached reset -> completed partial reset -> immutable seed -> transfer -> ensures
   payload read path. Bind the source-following false/true snapshot before Move and live destination.
   Marker/property presence is insufficient; path loss or early Unsupported/frame failure is not
   a resource improvement. Full intended P1 checks must be SUCCESS with no extra private failure.
4. Bind both private exact distinct emitted symbols. B0 has the original main target containing
   all fields. B1 has the unchanged main target and the full twelve buffer scalar member targets:
   active, selected_argument, signature, count, written, remaining, last_stored, last_loaded,
   has_witness, value, relative_offset, layout_size. Verify identities/field expressions independently
   from lambda count; no whole-buffer or user-referent target. Require actual write scopes for
   Begin/store/load/reset. Aggregate/byte/padding write or missing coverage => STOP for design
   clarification, never blanket whole-buffer exemption. Verify no-uninit/no emitted targets is
   admitted and uninit/PFC missing/partial/duplicate targets cannot silently disappear.
5. Report properties/all Failed Checks, steps, VCC before/after simplification, conversion milestones,
   SAT vars/clauses, seconds, RSS/units/scope/peak and cutoff/exit. Steady completion inside existing
   cap is the resource goal; no promised2GB, solver PASS or operator/width causality from source.

If B0 closes all applicable P1/P2/frame/resource gates, choose minimal B0; B1 is optional.
If B1 remains heavy, STOP with actual DFCC size/use findings. No unsafe pointer fallback/new bisect.

On a P1-admitted source, run P2, new lawful-modifies positive, existing frame-negative,
requires-clause negative, and selected true/false/nested/repeated argument-return/move controls.
Use worker14 CONTROL-MAP for exact inputs/roots/source hashes and qualifications. P2: only the
intended ensures u8 payload-read uninit FAILURE; lawful input/frame/protocol PASS. Frame-negative:
FAIL at the actual user *outside assignment; private writes yield no extra assignableFAIL.
Clause negative: intended uninit read in requires, not private frame loss. An expected negative
does not authorize extra failures. Source-bound object/target/location takes priority over var_N;
existing hard-coded golden IDs may be changed only after coordinator-observed outside-write binding.

## G2 — only after accepted G1

Run full existing Uninit Quick on final source + identical reviewed test delta, unit immutable_allocations5,
kani Uninit, expected WITH BOTH transfer-qualification/legal-pair AND postcondition-hole, ui and
script-based-pre/mem-init-reinstrumentation. Preserve current guards, negative oracles, all checks,
normal/abort behavior and M1/S3/immutable/mixed coverage. Any separately composed historical
mixed16 test-only package must retain its own exact parent/delta/source/full-test-tree identities;
its absence from accepted base is not a local regression PASS. Do not silently import old production.
No selector removal/ignore/filtering. Restricted Quick43257528539 (135/0 excluding2 heavy selectors)
is historical, not full G2 or this head PASS. Counts are observed, never guessed.

Capture build/solver stages, root/property/target bindings, full failure inventory and receipts
through the existing reporting interface; no raw logs/archives or historical ledger rewrites.
Compile success != proof; archive integrity != verification. No B1/B2 independent credit yet.
Full platform/full-suite and actual SmallSort replay require a later separate handoff. M3 HELD.
Worker stops after source/composition package and does not dispatch or wait for CI.
