# Agent checkpoint: merge-unwind-cleanup-autonomous-2026-10-22-r19

- Owner: merge | phase: MERGE-UNWIND-CLEANUP-R19-2026-10-22 | state: NOT_STARTED
- Updated: 2026-10-22T15:49:34Z
- Baseline: source `6fd50c699500cbac5c65912174d4aa49b49db19f`, tool `a66c1d30214e463a16a325cdef30b0ec8555e0af`, profile `947be6e0ed9aa0d2270a820dd72e5ff4c78e8d30af3e55d7228b477af700026d`
- Session dates: T0 `NOT_SET`; main deadline `NOT_SET`; absolute deadline `NOT_SET`
- Budget: 3600s total; 0s spent; 0s retired; 3600s remaining including active reservations
- Active Build IDs: none recorded
- Unresolved IDs: none recorded

## Confirmed claims
- [SOURCE_REPORTED] P1: RawPtr positive identical_local_rawmut refinement0 MATCHED; raw caller passed array_inv444/insert_tail call, new frontier free_locals array_ at 461 (unwind presumed). Bounded only; no credit. — [research/challenge-8/cloud-build/origin-layout/R18-PROOF1-RESULT-20261022.json](cloud-build/origin-layout/R18-PROOF1-RESULT-20261022.json) SHA `d0b75917c6865ce64ecad4da12beaa96a8ad293ff97c051af411e0a0d2141008` Build `e70d2723-f49d-4a8f-847e-f8da1106d36f`
- [SOURCE_REPORTED] P2: RawPtr controls 4/5 matched (positive, mutability, changed contents via aggregate refusal, raw/ref); index projection INCONCLUSIVE refiner limitation. No credit. — [research/challenge-8/cloud-build/origin-layout/R18-PROOF2-RESULT-20261022.json](cloud-build/origin-layout/R18-PROOF2-RESULT-20261022.json) SHA `18e233643f84376bc6103ee9df537bb917f3b9d2bdc454537fca86c404114ab3` Build `08bd6e03-a320-4e03-b5d3-21b051204b3e`
- [SOURCE_REPORTED] R18 CLOSED early: P1/P2 terminal/accounted, 1821s spent, 1779s retired, carry0; own active/unresolved 0. No credit. — [research/challenge-8/cloud-build/origin-layout/CURRENT-RECOVERY-R18-BUDGET-20261022.json](cloud-build/origin-layout/CURRENT-RECOVERY-R18-BUDGET-20261022.json) SHA `a0541f5bce32a9ea61cdfb025f90df1790707af014ae08436490c26db8d2c34d`

## Open
- Original as_mut_ptr/unsize, source-bound metadata, real borrow/reference lifecycle and caller normal/unwind remain OPEN; isolated lifecycle does not close them.
- Raw caller unwind free_locals needs checked source-bound cleanup (tool); RawPtr LocalAddressTaken negative and index projection control OPEN.
- CURRENT/backedge/false/true/panic/Drop/Resume compatible final matrix; B2/generic/arbitrary-n/sorting/tool qualification/independent proof credit remain OPEN.

## Rejected approaches
- Broad placeholder/cast inference exemption or address-only borrow bridge — Does not establish slice metadata, valid lifetime/full_borrow or memory authority; original gate must remain.; [research/challenge-8/cloud-build/origin-layout/R16-CALLER-DESIGN-20261021.md](cloud-build/origin-layout/R16-CALLER-DESIGN-20261021.md) SHA `c1e8f851b5c0b18edf3ed5ac2b758a32daa0eda2f4ea88551b8e37e03288b940`
- Short outer timeout990/execute570 chosen using prior whole-cycle timings — Missed nested compile reserve140; P4 timed out before proof. Keep full1200 plan unless effective inner budget reviewed.; [research/challenge-8/cloud-build/origin-layout/R16-REVIEW-20261021.md](cloud-build/origin-layout/R16-REVIEW-20261021.md) SHA `7ea120ef137323755ae4381de8915f8347d9a64bdd6b9e8b9753d561bdf70efa`
- Close early when the next tool commit/review cannot finish within main — R18 closed 29.5 min early with a ready, narrow design; CORE requires Cloud-free stages (implementation, tests, review, pins) instead.; [research/challenge-8/cloud-build/origin-layout/CURRENT-RECOVERY-R18-BUDGET-20261022.json](cloud-build/origin-layout/CURRENT-RECOVERY-R18-BUDGET-20261022.json) SHA `a0541f5bce32a9ea61cdfb025f90df1790707af014ae08436490c26db8d2c34d`

## Blocker
Raw caller unwind free_locals needs array_ at verified461; needs checked source-bound unwind cleanup (tool). R18 CLOSED early at real boundary. (raw caller verified461 free_locals) [Build `e70d2723-f49d-4a8f-847e-f8da1106d36f`]
- [research/challenge-8/cloud-build/origin-layout/R18-PROOF1-RESULT-20261022.json](cloud-build/origin-layout/R18-PROOF1-RESULT-20261022.json) SHA `d0b75917c6865ce64ecad4da12beaa96a8ad293ff97c051af411e0a0d2141008`

## Next
Implement the R18 unwind cleanup rule with its four controls and service tests; review; register R19; Cloud raw caller normal/unwind.

## Artifacts
- [research/challenge-8/cloud-build/origin-layout/R18-RELEASE-20261022.json](cloud-build/origin-layout/R18-RELEASE-20261022.json) — `1a9c18a08a0935226d6b7c4295dbe73d18c50e67464c6fe1554dea368561d076`
- [research/challenge-8/cloud-build/origin-layout/R16-RAW-CALLER-DESIGN-20261021.md](cloud-build/origin-layout/R16-RAW-CALLER-DESIGN-20261021.md) — `6acfb36fa52b2e05eea0551dfb40033156b23ef8165dfa67f6309d0550e721eb`
- [research/challenge-8/cloud-build/origin-layout/R18-REVIEW-20261022.md](cloud-build/origin-layout/R18-REVIEW-20261022.md) — `1558be1151365377aec81527760627eddd767e0e4b6344ed962d4c5a5d5e5617`
- [research/challenge-8/cloud-build/origin-layout/R18-RAW-CALLER-DESIGN-20261022.md](cloud-build/origin-layout/R18-RAW-CALLER-DESIGN-20261022.md) — `dfc93e3344b537e1168ae6b6a1645e4eb6d614c4e5b14effaf1185e6a641beac`
