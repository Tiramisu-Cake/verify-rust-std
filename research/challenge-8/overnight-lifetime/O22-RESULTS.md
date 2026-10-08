# O22 strict lifetime-cut diagnostic checkpoint

The O22 isolated CUT console built from VeriFast source
`f76012fb518703b1d98e243ac4f487f16877cfcb` plus the production
overlay identified by proof SHA `02945280d4f335948c6edd60feb7ac62092a0256`,
then the separate CUT patch SHA-256
`d557082b0c17771acd7386ad6caca7bc139877cf1ca513d9570da210b1b542d8`.
The CUT verifier binary is
`8b1ab517e81690ef390b61a2f136f8b41fe373c95cece1a753ebafe0d09cb652`;
the real exporter and refinement checker retain production hashes
`b00c75f43ab4d89bf85f5e62a5114a238b89b720d4598d90423347b9d97ac796`
and `b049c8d1b0bb350f77664e1c75c5a95966c5839984abc25c7cb629c0cba04d28`.
The effective spec and decoder hashes are in the hosted
`strict-cut-isolated/cut-console-manifest.json`. This is a diagnostic
console and **not an accepted production profile**. The exact hosted
artifact is `/tmp/overnight-o22-evidence/overnight-s6/strict-cut-isolated/`.

Four source fixtures completed before a runner setup error stopped the
17-case matrix. `positive_basic`, `ordinary_unmarked`,
`positive_early_return`, and `positive_direct_unwind` each had complete
NORMAL and readonly export/decode, original-source refinement exit 0,
source-strip identity, exact selected-body inventory, and full VeriFast exit
0 with no proof error or leak. The direct-unwind fixture verified its
same-unit `cut_maybe_unwind` callee before its caller. Both decoded graphs
include the call's `unwindAction = continue`; the caller log reaches two
return leak checks (normal and unwind) and reports 0 errors / 57 statements.
These are local scope-mechanics positives, not a proof of actual sort4.

The separate absent-opt-in run of `positive_basic` also exported, decoded,
and refined; full verification rejected the exact source marker at
`verified/lib.rs(13,9-14,1)` with `Strict lifetime binding requires explicit
overnight opt-in`, before target body proof. On the same CUT console, all
eight full S6 matrix stages have status 0 and `accepted: true`; the nine
existing no-cut callback controls and their classifier have status 0.
Those regressions establish only the named unmarked behavior on this
experimental console.

The matrix process exited 1 before exporting `positive_f_bound` because
its source-shape guard expected `callback_positive(`, whereas its reviewed
generic declaration starts `callback_positive<T, F: ...>`. The remaining
13 fixtures are **NOT_RUN**. The runner-only fix in `capture.py` recognizes
`<` for that one generic target while retaining its function count and
template/source checks; no fixture, CUT patch, target postcondition, or
classifier was changed. A new hosted run is required to observe it.

The source-file, CFG ingress/reentry, unresolved-inference, live nested-bound
heap, and outer-variable escape controls remain unimplemented or unverified.
No CUT acceptance or actual sort4 lifetime claim follows from O22.

Exact run: [37754201983](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37754201983),
proof02945280d4f335948c6edd60feb7ac62092a0256.
