# M3-R3 capture runner repair — worker14

Source: `3a29b3323561c5765505ef617607cadfc91f0ce8`, new commit directly on
`6c29e38c57fdf646bf07725c5c09008518d04255` in `/root/kani-fix-3300-m3r3`.
Scope: issued tasks (1)–(2); no binding preparation or manifest changes.

Capture run `43501001052` stopped during observation validation of
`isolated-pfc_legal`, after Kani itself returned 0 / SUCCESS. No combined
invocation started. The receipt explicitly records
`Rejected('wrong PFC target: pfc_legal')`. `export.json` has
`attributes.kind.ProofForContract.target_fn = "pfc_contract"`, matching the
manifest. The old predicate required `.endswith("::pfc_contract")`, rejecting
this valid bare target. Harness metadata preserves the PFC attribute's path
spelling (`kani-compiler/src/kani_middle/attributes.rs`, `harness_attributes`),
so a leading module separator is not guaranteed.

The error was not absent: local job log line 2179 contains the FAIL JSON and
receipt error. The handler printed that large line before all regular logs;
the tail therefore showed only pfc_legal's successful verifier output and
`Retained mixed-root outputs`. It returned 1 because runner validation failed,
not because the verifier reported a failure or a combined step ran.

The repair accepts the exact bare target as well as the previously accepted
module-qualified suffix, retains rejection of wrong target names, and includes
expected/actual target metadata in rejection messages. Every caught stop now
prints its invocation/order and phase, exception type and reason to stderr
before and after regular logs. Preflight uses the same handler. A FAIL
`capture.json` is retained when a temporary directory exists; malformed receipts,
report-write failures and unreadable logs cannot replace the original printed
reason. KeyboardInterrupt identifies the active step and exits 130. Successful
process receipts now persist expected_exit too. UNBOUND_CAPTURE still exits 2;
no binding/order/proof credit was added.

`AUDIT-CAPTURE.py` reads only the supplied local files and uses the repaired
schema/observation/comparison paths without launching Kani. `CAPTURE-AUDIT.json`
pins the job-log, receipt, export and regular-output hashes and records the
four complete validated inventories: immutable_legal (39 properties),
immutable_hole_negative (37), ordinary_ensures_legal (227), pfc_legal (231).
Original receipts and artifacts remain unchanged, including the original PFC
rejection. This establishes offline runner validation, not a new proof run.

Capture cannot be completed from these files: isolated pfc_negative, cycle_root
and unrelated_legal_after_cycle plus all_A_then_B, all_B_then_A,
cycle_then_legal and legal_then_cycle are missing. The coordinator needs a fresh
full `tests/json-handler/uninit-part1-composition/test.sh --collect-unbound --keep-output`
capture on the repaired commit. No resumable capture mode or synthetic replacement
for missing verifier outputs was introduced. Binding remains BINDING_PENDING.

Validation: `python3 tests/json-handler/uninit-part1-composition/test_compare.py`
passes 32 tests, including bare/qualified/wrong PFC targets, isolated/combined
stops, comparison failure, malformed receipt, failure-report write error,
preflight rejection, interrupt, and full synthetic 11-invocation capture exiting
2. Existing timeout/process/output/hash error-path tests also pass.
`git diff --check` passes. The offline artifact audit passes for all four runs.
No cargo, Kani, CBMC, push or new CI dispatch was performed. Quick run
`43498489470` PASS (expected 202/0) is user-reported prior evidence, not rerun here.
