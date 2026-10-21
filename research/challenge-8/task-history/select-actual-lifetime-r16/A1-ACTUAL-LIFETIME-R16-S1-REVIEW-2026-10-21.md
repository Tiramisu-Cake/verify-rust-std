# R16 S1 independent semantic review

**Disposition: GO to the existing committed-source client preflight and S1 submit.** The review found and the owner corrected a stale c1 constructor pin and two bounded source-closure issues before this final review. GO covers the reviewed implementation and registration only; it grants no proof credit or profile acceptance.

Review baseline: HEAD `31596e61f516db80c53eb8d336c48d760bc1e97b` (including the R16 fixes in `2d2ae59f`, `435efd6d`, and `31596e61`). Reviewed only the R16 implementation/registration scope named in the task. Review key SHA-256: `776eb65b47b9a9b4a76891b46585b1e605e9f566255b5e078c1a21e874703e01`. The key is SHA-256 over the lexically sorted scoped paths, each encoded as `path + NUL + exact working-tree bytes + NUL`.

## Resolved finding and delta review

The initial R16 profile used a stale SHA for `a1-actual-body-c1.py`, which would have failed closed before body construction. Commit `2d2ae59f` updates the dependency pin to `8af19b63552b7ef6e4b6026b4f188fa00c4344a4bb1b75848008e7b46141441e`, matching the current constructor bytes. The full-body runner's actual-body, entry, runner, c1 constructor, copy/recovery/selector components, and `capture.py` hashes now match their profile pins.

The runner now imports only the pinned fixture and AST-gate helpers needed by this full-body path; the recipe drops the unused synthetic producers, legacy one-copy fixture, and (in final recipe-only delta `31596e61`) `a1-focus-backend.py`. The R16 call path uses the pinned `a1-runner.py` core only for `select_checked_cleanup_helper_lemma`; its full matrix collector that calls the focus backend is not invoked. The actual four-copy component and all callback, selector, recovery, c1, and required service-control routes remain. The R16 time budget accepts only 270–1200 second Builds and reserves exactly 240 seconds for packaging/reporting; registration controls reject smaller values and wrong types.

## Reviewed boundaries

The strict-entry diagnostic overlay only prints outer names/types under the trace flag before the existing strict freeze; it declares no proof semantics change. The c1 phase-binding patch changes the R15 authorization literal to R16 while retaining the other gates. `a1-tool.py` verifies the R15 overlay chain before applying the two manifest-pinned R16 overlays with exact before/after digests. The actual-body runner preserves the source body, includes unwind posts and four-source ownership, suppresses A1 summary environment inputs, requires source/tool identity checks, and keeps proof credit, admission, and evidence-complete flags false.

Static Python parsing succeeded for the R16 Python scope. The owner reports registration 8 PASS and service 27 PASS after the pin/closure/budget changes; I did not rerun those tests. No compiler, verifier, Cloud Build, or raw evidence was used. The required existing client source/transport preflight remains the next gate.
