# Correction after CI43636027466 — targeted request (no dispatch)

Prior6d2e9ae621: fmt/build/clippy PASS; units6/2/9, kani24/0, expected226ok/2compile failures,
ui17/0, script2/0, remaining JSON17/0. The two Replace callers lost the required local PFC.
Current source restores it and explicitly selects the original caller only. First rerun
both affected expected selectors and confirm their intended N2/N0, useful blocks and1total.
Goldens remain unchanged. New source has not been built/verified by this worker.

Sensitivity CI attempt was INVALID: selectors were ignored/skipped; it was not a detection
result. Manifest already specifies --force-rerun; use it for every mutation selector.
All four patch files and their mutated-input hashes remain unchanged/applicable. Reuse
the built Kani/compiletest; require normal cases PASS before mutation mismatch evidence.
The original regression/Quick and final three-host acceptance requirements below remain.

# S5 coordinator CI request — NOT_RUN

The owner supplied missing exact-base report43630584079 at g0 d9a2a40c93.
Strong p2 and postcondition-hole each have exactly3 failures: both intended reads plus
outer ensures17. Replace has exactly2 intended reads, no Unsupported; support remains
UNCLAIMED. Original Replace covers are SATISFIED; portable negative removes pure
cover hooks and retains both input alternatives and the useful reached assertion.
Positive same-source ordinary/SimpleCheck companions retain both return-path covers.

On final source candidate (SHA in RESULT/INPUTS), build once and run fmt/build/clippy.
Run native compiletest discovery and all22 new/reworked expected normal fixtures (21 old case/root obligations) first,
with regular output, per-fixture object-bits12 and existing flags/checks/solver.
Use exact selectors in DISCOVERY-INVENTORY.json. Any unexpected failure, missing
selector, UNREACHABLE useful assertion or unsatisfied required cover stops acceptance.
No blessing or --fix-expected, skip, solver/no-check workaround, or stale composition waiver.

Then use SENSITIVITY-MANIFEST.json: four independent CI-only/test-only overlays,
same built Kani and native compiletest, original goldens unchanged except sanity overlay.
Force rerun and separate build/output dirs; record actual native verdict/N, compiletest
exit and precise expected mismatch. Intentional mutant-selector compiletest FAIL is
successful sensitivity detection, not a normal test PASS. Setup/compile errors, timeout
and unrelated Unsupported are invalid experiments. Reuse builds; no rebuild per mutant.

Run existing Uninit kani/expected/ui/script, S2 immutable allocation9 units, S3 reset
controls, S4 delayed_cache6/delayed_scope2 units, and all remaining upstream JSON-handler
schema/export tests, then existing Linux Quick. Known bound-composition FAIL is not a
waiver: that suite is removed after map, and replacements must pass. No new JSON runner.

Mixed-inventory relation is deliberately not asserted by expected; assess the reduced
end-to-end coverage in MIXED-ISOLATION-DISPOSITION/REVIEW. Three-platform full Gate A
remains after S6/freeze; one Linux result cannot establish three-host portability.
No build/push/CI dispatch was performed by this worker.
