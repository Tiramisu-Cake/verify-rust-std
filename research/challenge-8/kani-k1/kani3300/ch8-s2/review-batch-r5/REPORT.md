# Independent14 R5 review — CHANGES_REQUIRED

Reviewed exact package `53008fd4de6bb5719fd232b1ddb7e875b5112012`, control
`4e97d370aba4adc480fcc3701b111d02658aa94d`, tree
`d4e0b1f74b609c67f984fe157b940330ac8d323a`, sole parent
`9e14e033f9ee31522b571c127609dcdff76d230b`. Task `cd5da9a56e145dfef0e14a78a5379659d1c77cd6`
and mandatory margin addendum `e333995f0089a629e0ccbaf1a477248ff5fc31e2` both applied.
Source `bd62e54df1b4749154790aa3db3cc7978f547f75` and stock
`0aac16ef62da9e9d5645782d458593e5d78143ba` remain unchanged.

Two blockers require an immutable original13 repair and same14 delta review.
An 11-minute cap-only repair addresses R14-R5-01 but leaves R14-R5-02 open.
This review does not authorize GO or dispatch.

1. **R14-R5-01 — HIGH: Validate lacks the mandatory 1.5x margin.**
   `.github/workflows/ch8-s2.yml:33` grants 600s. The exact recorded final-object
   execution is 130 tests, exit0, 403.420022367s, on control4e97. Required cap is
   at least 605.1300335505s; 600s gives about 1.487x. Original530 cannot APPROVE.
   Original13 should implement the already routed R5-only 11-minute cap and
   its exact assertions/derived bindings. 660s gives about 1.636x against the
   inherited host measurement. Keep legacy10min strict and preserve all modules,
   step order, setup1800/job180/campaign and resource ceilings. Do not claim that
   the old130-test execution ran on a repaired object or predicts GitHub timing.
   Evidence: `VALIDATE-MARGIN.json`, rechecked timing/transcript provenance in
   `REEXECUTED-VALIDATION.json`.

2. **R14-R5-02 — HIGH: the uploaded artifact cannot replay a completed seal.**
   `r5_campaign.py:197` seals every group file, including the stdout/stderr logs
   that `runner.py:1086` creates before execution. `pack_evidence.py:100` packs
   only `*.json`; the workflow uploads only `group-evidence.json.gz` at line109.
   `r5_campaign.py:46,268` subsequently verifies every sealed file through
   `collect.read_bytes`, which indexes the missing log in the archive.

   The reviewer reproduction runs the real `_run_group` control pipeline with
   only external execution/source/binary sampling replaced by bounded fixtures.
   The local root is `RECORDED`, expected-match true, and its seal verifies.
   After a later synthetic global failure, packing reports `PACKAGED`, and the
   row receipt is retained byte-for-byte. Copying only the uploaded artifact to
   a fresh directory makes both `sealed(..., collect.read_bytes)` and R5
   `collect()` fail with `KeyError: groups/r5-checker_order_corrupt/stderr.log`.
   Thus a normal published completed prefix is not replayable even below all
   caps. No native compilation or real evidence archive was used.

   Original13 should align the portable completion seal with the bounded
   structured evidence actually published. Keep raw logs local; retain any
   local-only digest metadata explicitly without requiring unavailable raw
   payload during portable replay. Preserve request/source/binary/compile/export/
   rich-property/diagnostic checks and protected decoders. Add a meaningful
   archive-only regression: complete a root, introduce a later failure, run
   fallback/packing, copy only the upload to a fresh directory, and verify exact
   prefix plus collection. Artifact existence alone does not test this boundary.
   Compact-cap omissions must remain explicit and unqualified. Evidence:
   `reproduce_uploaded_prefix.py`, `UPLOADED-PREFIX-REPRO.json`, `CODE-EVIDENCE.json`.

The remainder of the full R5 contract was reviewed as follows.

| Area | Review result |
|---|---|
| Singleton/order/selection | Serial owner loop follows the exact issued order; one qualified `--harness`, `--exact`, jobs1; observed stock-start guards reject wrong/duplicate roots. Native execution NOT_RUN. |
| Inventories | Selected9/16/5 and deferred general32 pair remain distinct from full11/20/6. Source rows, tagged oracles, covers and both general32 contexts remain. |
| Fresh bindings | Fresh invocation UUID/CARGO_TARGET_DIR, per-root export, cfg/stub/PFC/metadata/request/argv/source/binary snapshots preserved. Namespace IDs do not establish compiler-instance/origin proof. |
| Lifecycle | Local limit/compile/missing/partial/unexpected results continue after verified owned cleanup. Source/tool/request/binary drift, containment/storage/global boundaries abort with explicit unstarted/unknown states. Cutoffs cannot become late success. |
| Durability | Local completed seals survive later failure/fallback. Portable replay is blocked by R14-R5-02. |
| Time/resource caps | Compile180 inside child600, supervised worker710 plus publication10 inside slot720;9x720+180+240=6900 within7500/8100/7560. Setup1800 and job10800 unchanged. Maxima sums do not grant elapsed time. |
| RSS | Effective min(6GiB,available−2GiB,12GiB); non-atomic polled PGID VmRSS, overshoot possible. Outer observed-owned PID sampling and subreaper/pidfd cleanup are distinct from strict kernel/tree memory accounting. |
| Global limits | Shared monotonic campaign clock, reserved cleanup, aggregate stdout/stderr/export/artifact census and remaining grants; no retries, resumed partial roots or compilation reuse. |
| Gates/controls | Legacy request/functions and protected lexical/cfg/PFC/contract/ordinary/parser/oracle/diagnostic/B01B02 behavior preserved. New explicit profile dispatch remains separate. |
| Packaging/ancestry | Exact stock-relative changed paths/payload hashes, request/workflow copies, six patch replays, sole parent9e14, shallow7/5/2 verified. |

Validation: the reviewer independently ran **23 R5 Python/mock service tests,
all PASS**, 25.83181921s; no full Validate repetition. The author-recorded final
Validate130PASS/403.420022367s and check-source13.074775086s were inspected with
exact command, identities and transcript hashes. All75 committed package files
and74 manifest hashes match530. The reviewed author static validator was
reexecuted with its sole persistent output redirected here; it rechecked hashes,
protected bytes/maps, six Git-index patch replays and actual shallow metadata.
Four legacy function AST comparisons were checked independently.

Only reviewer-owned output files were written. Candidate/source/tool edits,
compiler/verifier/full runner/CI/push/PR/issue/ledger/budget/reservation/subagents:
zero. Fast OFF, settings preserved. Future GitHub duration and native R5 outcomes
remain UNKNOWN/NOT_RUN. Assumed/caller-copy/source-reported limitations remain;
general32 is deferred, no proof obligations closed, independent B1/B2 credit NONE.

No final repair pins have been issued to this review at sealing. Uncommitted or
unissued repair directories are excluded. Next: root routes these localized
findings to original13, supplies exact committed repair pins, then requests
same14 integration/delta review. GO requires exact-final APPROVE and no blockers.
