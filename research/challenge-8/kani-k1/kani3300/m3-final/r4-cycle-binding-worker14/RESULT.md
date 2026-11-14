# Worker14 — r4 cycle binding

READY `1658f4cadfa83139e41180ce3865e23f79d889aa` in `/root/kani-fix-3300-worker14`; direct parent `3912b8e0319754f43bbcd7f2b363ad5cbf0a80c9`.

`cycle_root` is now REGRESSION_BOUND from reviewed run 43506774865 (r4).
The exact isolated inventory contains 384 checks: 337 SUCCESS, 46 UNREACHABLE,
and one FAILURE, `cycle_root.unsupported_construct.1`. FAILURE / OTHER is the
expected recursive mode boundary; full failure and Unsupported metadata match,
including the readable diagnostic, file/line and trace flag. All four mixed
selections match the cycle inventory exactly. The six r3 bindings are unchanged;
all seven roots are bound, with zero BINDING_PENDING entries in roots.json.
No diagnostic normalization or oracle allowance was added.

`AUDIT-R4.py` validates all 11 supplied invocations against hashes, receipts,
commands, selection/mode/configuration metadata, schemas, regular output and
exports. It reconstructs all saved observations and comparisons, checks all
seven exact isolated bindings, then replays the ordinary runner entirely offline
with verifier subprocess calls blocked: **PASS / REGRESSION_BOUND**, exit 0.
All 18 comparisons are accepted: **12 exact + 6 T1b**. The original capture is
unchanged (`UNBOUND_CAPTURE`, `BINDING_PENDING`, `MATCH_WITH_T1B`).

Exports and the job log identify CI wrapper `8b2bca3bed4c643d4a0126de5dedfb2a723b9214`.
Local Git comparison confirms its only differences from source `3912b8e0319754f43bbcd7f2b363ad5cbf0a80c9` are
`.github/workflows/` files. Both identities are recorded in the cycle evidence.

**91 synthetic tests pass**: binding 10, composition 41, mode-boundary 19,
strong oracle 21. Coverage includes exact cycle inventory/status/diagnostic
and failure metadata drift, missing Unsupported, fail-closed pending preflight,
process/schema errors, explicit capture remaining unqualified, and narrow T1b.
`git diff --check` passes; the source clone is clean after the new commit.

Research: `INPUTS.json`, `STATIC-CHECKS.json`, `AUDIT-R4.py`, `CAPTURE-AUDIT.json`,
`CHECKPOINT.json`. Quick run 43506779934 results are user-reported inputs only.
No cargo, Kani, CBMC, new CI, amend or push. Offline PASS does not replace fresh
C1 qualification. Producer order remains ORDER_UNCONTROLLED / NOT_ESTABLISHED;
no independent proof credit is claimed.
