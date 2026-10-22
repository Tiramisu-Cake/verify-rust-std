# Agent checkpoint: merge-unwind-acceptance-autonomous-2026-10-23-r20

- Owner: merge | phase: MERGE-UNWIND-ACCEPTANCE-R20-2026-10-23 | state: NOT_STARTED
- Updated: 2026-10-22T20:00:20Z
- Baseline: source `6fd50c699500cbac5c65912174d4aa49b49db19f`, tool `39f6b0cacd00575c8ca2d39e9f15632723bf1227`, profile `1404842fc70c2fbc4d422d63ff3035edeacd22ac64cdf02382b2300e94fd57bb`
- Session dates: T0 `NOT_SET`; main deadline `NOT_SET`; absolute deadline `NOT_SET`
- Budget: 3600s total; 0s spent; 0s retired; 3600s remaining including active reservations
- Active Build IDs: none recorded
- Unresolved IDs: none recorded

## Confirmed claims
- [SOURCE_REPORTED] P1: RawPtr positive identical_local_rawmut refinement0 MATCHED; raw caller passed array_inv444/insert_tail call, new frontier free_locals array_ at 461 (unwind presumed). Bounded only; no credit. — [research/challenge-8/cloud-build/origin-layout/R18-PROOF1-RESULT-20261022.json](cloud-build/origin-layout/R18-PROOF1-RESULT-20261022.json) SHA `d0b75917c6865ce64ecad4da12beaa96a8ad293ff97c051af411e0a0d2141008` Build `e70d2723-f49d-4a8f-847e-f8da1106d36f`
- [SOURCE_REPORTED] P2: RawPtr controls 4/5 matched (positive, mutability, changed contents via aggregate refusal, raw/ref); index projection INCONCLUSIVE refiner limitation. No credit. — [research/challenge-8/cloud-build/origin-layout/R18-PROOF2-RESULT-20261022.json](cloud-build/origin-layout/R18-PROOF2-RESULT-20261022.json) SHA `18e233643f84376bc6103ee9df537bb917f3b9d2bdc454537fca86c404114ab3` Build `08bd6e03-a320-4e03-b5d3-21b051204b3e`
- [SOURCE_REPORTED] R19 cleanup tool 39f6b0ca / proof candidate 3a587cb7 reviewed GO_WITH_NITS x2; Cloud compile/proof/controls NOT_RUN, credit0. Publication confirmed in closeout. — [research/challenge-8/cloud-build/origin-layout/R19-REVIEW-20261022.md](cloud-build/origin-layout/R19-REVIEW-20261022.md) SHA `6b9a227165ed4cc3ba6e71d77ee2083ca14c4505fe64205b2233068c444fc1a8`
- [INDEPENDENTLY_ESTABLISHED] R19 CLOSED: 0 Builds/spent, 3600s retired, carry0. Candidate/tool published; Cloud UNVERIFIED, credit0. — [research/challenge-8/cloud-build/origin-layout/R19-CLOSEOUT-20261022.json](cloud-build/origin-layout/R19-CLOSEOUT-20261022.json) SHA `64c5f76009562d166d0d057a6dab6e1198fd7431bb8a8dd867bac6656ceb055b`

## Open
- Original as_mut_ptr/unsize, source-bound metadata, real borrow/reference lifecycle and caller normal/unwind remain OPEN; isolated lifecycle does not close them.
- R19 raw caller unwind cleanup implemented/reviewed but UNVERIFIED; RawPtr LocalAddressTaken negative and index projection OPEN.
- CURRENT/backedge/false/true/panic/Drop/Resume compatible final matrix; B2/generic/arbitrary-n/sorting/tool qualification/independent proof credit remain OPEN.
- R19 F5: missing_owner_drop is a static shape refusal, not a separate verifier proof of the unwind copy. Phase/recipe R20 registration remains to be prepared at actual T0.

## Rejected approaches
- Broad placeholder/cast inference exemption or address-only borrow bridge — Does not establish slice metadata, valid lifetime/full_borrow or memory authority; original gate must remain.; [research/challenge-8/cloud-build/origin-layout/R16-CALLER-DESIGN-20261021.md](cloud-build/origin-layout/R16-CALLER-DESIGN-20261021.md) SHA `c1e8f851b5c0b18edf3ed5ac2b758a32daa0eda2f4ea88551b8e37e03288b940`
- Short outer timeout990/execute570 chosen using prior whole-cycle timings — Missed nested compile reserve140; P4 timed out before proof. Keep full1200 plan unless effective inner budget reviewed.; [research/challenge-8/cloud-build/origin-layout/R16-REVIEW-20261021.md](cloud-build/origin-layout/R16-REVIEW-20261021.md) SHA `7ea120ef137323755ae4381de8915f8347d9a64bdd6b9e8b9753d561bdf70efa`

## Blocker
Published R19 cleanup candidate remains Cloud-UNVERIFIED; original caller borrow/unsize and full normal/unwind remain OPEN.

## Next
At actual T0 prepare/register R20; Cloud preflight, then the published raw caller normal/unwind and five R19 controls.

## Artifacts
- [research/challenge-8/cloud-build/origin-layout/R19-UNWIND-CLEANUP-DESIGN-20261022.md](cloud-build/origin-layout/R19-UNWIND-CLEANUP-DESIGN-20261022.md) — `571f1acd4a0ad8f86c7fe2bfa95e9a5a80450cbe0a5dc84c81fe5f8309ad857e`
- [research/challenge-8/cloud-build/origin-layout/R19-REVIEW-20261022.md](cloud-build/origin-layout/R19-REVIEW-20261022.md) — `6b9a227165ed4cc3ba6e71d77ee2083ca14c4505fe64205b2233068c444fc1a8`
