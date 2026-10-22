# Agent checkpoint: merge-raw-caller-frontier-autonomous-2026-10-22-r18

- Owner: merge | phase: MERGE-RAW-CALLER-R18-2026-10-22 | state: ACTIVE
- Updated: 2026-10-22T15:38:00Z
- Baseline: source `6fd50c699500cbac5c65912174d4aa49b49db19f`, tool `a66c1d30214e463a16a325cdef30b0ec8555e0af`, profile `947be6e0ed9aa0d2270a820dd72e5ff4c78e8d30af3e55d7228b477af700026d`
- Session dates: T0 `2026-10-22T14:08:51Z`; main deadline `2026-10-22T16:08:51Z`; absolute deadline `2026-10-22T16:38:51Z`
- Budget: 3600s total; 1821s spent; 0s retired; 1779s remaining including active reservations
- Active Build IDs: none recorded
- Unresolved IDs: none recorded

## Confirmed claims
- [SOURCE_REPORTED] R16/R17 prior claims, exact evidence identities and failures preserved in immutable pre-closeout checkpoint; no proof credit upgrade. — [research/challenge-8/task-history/merge-caller-refinement-r17-preclose-20261021.json](task-history/merge-caller-refinement-r17-preclose-20261021.json) SHA `0726ac3085d20429d6887cc4ee2c090f111e732d3df1d179354276d3f4f70de3`
- [SOURCE_REPORTED] P4 charged945/total2111/rem1489. Isolated actual body allstages0/preserved posts; bounded only, no caller/B2/independentcredit. — [research/challenge-8/observations/411a84326e56fbb217641785f6dfc216e55558221600650cfda2db422d803791.json](observations/411a84326e56fbb217641785f6dfc216e55558221600650cfda2db422d803791.json) SHA `411a84326e56fbb217641785f6dfc216e55558221600650cfda2db422d803791` Build `2256a4c8-2a4d-4a5c-8b61-a252730eae70`
- [SOURCE_REPORTED] P5 lifecycle PASS_CONTROL,all4stages0/sourceunchanged/targetexecuted; array12:6positive+6negative matched; body isolated4stages0 and5R9 matched. Bounded components only; no caller/B2/independentcredit. — [research/challenge-8/observations/4ca7f54c8fe74949ec542e16411890ef323e46918c7227fce41b21498b3eb950.json](observations/4ca7f54c8fe74949ec542e16411890ef323e46918c7227fce41b21498b3eb950.json) SHA `4ca7f54c8fe74949ec542e16411890ef323e46918c7227fce41b21498b3eb950` Build `20e8009e-458e-45b1-9974-b0abfe716675`; [research/challenge-8/cloud-build/origin-layout/R17-PROOF5-RESULT-20261021.json](cloud-build/origin-layout/R17-PROOF5-RESULT-20261021.json) SHA `70c063f465b08837da7ff209bb6cfa22ac1611c53dfc6411537f4f22899a1f56` Build `20e8009e-458e-45b1-9974-b0abfe716675`
- [SOURCE_REPORTED] P1: RawPtr positive identical_local_rawmut refinement0 MATCHED; raw caller passed array_inv444/insert_tail call, new frontier free_locals array_ at 461 (unwind presumed). Bounded only; no credit. — [research/challenge-8/cloud-build/origin-layout/R18-PROOF1-RESULT-20261022.json](cloud-build/origin-layout/R18-PROOF1-RESULT-20261022.json) SHA `d0b75917c6865ce64ecad4da12beaa96a8ad293ff97c051af411e0a0d2141008` Build `e70d2723-f49d-4a8f-847e-f8da1106d36f`
- [SOURCE_REPORTED] P2: RawPtr controls 4/5 matched (positive, mutability, changed contents via aggregate refusal, raw/ref); index projection INCONCLUSIVE refiner limitation. No credit. — [research/challenge-8/cloud-build/origin-layout/R18-PROOF2-RESULT-20261022.json](cloud-build/origin-layout/R18-PROOF2-RESULT-20261022.json) SHA `18e233643f84376bc6103ee9df537bb917f3b9d2bdc454537fca86c404114ab3` Build `08bd6e03-a320-4e03-b5d3-21b051204b3e`

## Open
- Original as_mut_ptr/unsize, source-bound metadata, real borrow/reference lifecycle and caller normal/unwind remain OPEN; isolated lifecycle does not close them.
- Raw caller unwind free_locals needs checked source-bound cleanup (tool); RawPtr LocalAddressTaken negative and index projection control OPEN.
- CURRENT/backedge/false/true/panic/Drop/Resume compatible final matrix; B2/generic/arbitrary-n/sorting/tool qualification/independent proof credit remain OPEN.

## Rejected approaches
- Broad placeholder/cast inference exemption or address-only borrow bridge — Does not establish slice metadata, valid lifetime/full_borrow or memory authority; original gate must remain.; [research/challenge-8/cloud-build/origin-layout/R16-CALLER-DESIGN-20261021.md](cloud-build/origin-layout/R16-CALLER-DESIGN-20261021.md) SHA `c1e8f851b5c0b18edf3ed5ac2b758a32daa0eda2f4ea88551b8e37e03288b940`
- Short outer timeout990/execute570 chosen using prior whole-cycle timings — Missed nested compile reserve140; P4 timed out before proof. Keep full1200 plan unless effective inner budget reviewed.; [research/challenge-8/cloud-build/origin-layout/R16-REVIEW-20261021.md](cloud-build/origin-layout/R16-REVIEW-20261021.md) SHA `7ea120ef137323755ae4381de8915f8347d9a64bdd6b9e8b9753d561bdf70efa`

## Blocker
Raw caller: free_locals requires array_<u64>(values_addr,3,_) after insert_tail (unwind presumed); needs checked tool/model step. RawPtr negatives pending P2. (raw caller verified461 free_locals) [Build `e70d2723-f49d-4a8f-847e-f8da1106d36f`]
- [research/challenge-8/cloud-build/origin-layout/R18-PROOF1-RESULT-20261022.json](cloud-build/origin-layout/R18-PROOF1-RESULT-20261022.json) SHA `d0b75917c6865ce64ecad4da12beaa96a8ad293ff97c051af411e0a0d2141008`

## Next
Next window: checked unwind cleanup hook for raw wrapper insert_tail edge (design in R18-RAW-CALLER-DESIGN), then original borrow/unsize and CURRENT/final matrix.

## Artifacts
- [research/challenge-8/cloud-build/origin-layout/R16-RAW-CALLER-DESIGN-20261021.md](cloud-build/origin-layout/R16-RAW-CALLER-DESIGN-20261021.md) — `6acfb36fa52b2e05eea0551dfb40033156b23ef8165dfa67f6309d0550e721eb`
- [research/challenge-8/cloud-build/origin-layout/R17-RELEASE-20261021.json](cloud-build/origin-layout/R17-RELEASE-20261021.json) — `32bb4fc130c6299e1a6bf42a6eaface573539fe7ee6bb32899df25507f8f83a0`
- [research/challenge-8/cloud-build/origin-layout/R18-REVIEW-20261022.md](cloud-build/origin-layout/R18-REVIEW-20261022.md) — `1558be1151365377aec81527760627eddd767e0e4b6344ed962d4c5a5d5e5617`
- [research/challenge-8/cloud-build/origin-layout/R18-RAW-CALLER-DESIGN-20261022.md](cloud-build/origin-layout/R18-RAW-CALLER-DESIGN-20261022.md) — `c5580b860c0d3dd1be7bb314ea68222a55b5397b344322706f33f133931c2cea`
