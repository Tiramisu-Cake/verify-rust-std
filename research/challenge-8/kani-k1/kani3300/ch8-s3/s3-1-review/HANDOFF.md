# Independent14 → original13: REQUEST_CHANGES

Exact reviewed g0 `e8a8e5328a941af8a07b778122604b0c9bf4579b`;
source `513341f41ce53833a279571401c924bdddddb6c8`;
control `1dfc267b66abd83d536eb41a17052a4f3d767d2b`;
stock tool `0aac16ef62da9e9d5645782d458593e5d78143ba` unchanged.
Full identities and hashes: INPUTS.json / inputs-audit.json.

Two blockers, independently reproduced without native tools:

1. **R14-02/P1**, `s3_campaign.py:186`: FAILED worker groups skip recorded
   protected-snapshot errors/drift. A recovered outer post snapshot permits all
   six later roots. Check available worker error evidence regardless of state;
   preserve the separate interrupted-worker missing-AFTER recovery case.
2. **R14-01/P2**, `runner.py:511,1091`, `s3_campaign.py:386`: compile/source-under-
   test receipts retain bd62 instead of513341; local/upload collector accepts
   them. Bind request-derived identities at writers and validate at readers,
   preserving legacy policy and historical evidence.

See REPORT.md and FINDINGS.json for exact triggers, repair boundaries and required
controls. `tests/test_review14.py` asserts the current buggy behavior; its PASS
means reproduction, not candidate approval. Existing36 S3 tests and real static
check-source pass. Original final172 PASS/601.497913089s remains correctly pinned
to1dfc;171/619 precursor is not final evidence.

Original13 owns a **new immutable repair** and refreshed affected identities/
validation; return **same14 delta**. Do not edit original s3-1 or this review.
No source edits are requested absent a repair dependency. Source/body/domain
review identified no additional blocker, but native compilation/proof/fit is
NOT_RUN and no provider is qualified.

**No APPROVE → no root GO-request.** User coordinator alone controls a separately
authorized future launch/accounting at12/17. Ledger remains reference11/17,
total41/48; no reservation. No CI/compiler/Kani/CBMC/full native runner/push/PR/
issues/ledger/subagents/model changes. Credit NONE; high/Fast OFF preserved.
