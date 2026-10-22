# Agent checkpoint: merge-unwind-acceptance-autonomous-2026-10-23-r20

- Owner: merge | phase: MERGE-UNWIND-ACCEPTANCE-R20-2026-10-23 | state: ACTIVE
- Updated: 2026-10-22T21:51:28Z
- Baseline: source `6fd50c699500cbac5c65912174d4aa49b49db19f`, tool `39f6b0cacd00575c8ca2d39e9f15632723bf1227`, profile `1404842fc70c2fbc4d422d63ff3035edeacd22ac64cdf02382b2300e94fd57bb`
- Session dates: T0 `2026-10-22T20:08:00Z`; main deadline `2026-10-22T22:08:00Z`; absolute deadline `2026-10-22T22:38:00Z`
- Budget: 3600s total; 2107s spent; 0s retired; 1493s remaining including active reservations
- Active Build IDs: 0d3e7c6d-dfe4-4dbb-b5da-f0169d92ff53
- Unresolved IDs: none recorded

## Confirmed claims
- [INDEPENDENTLY_ESTABLISHED] R19 CLOSED: 0 Builds/spent, 3600s retired, carry0. Candidate/tool published; Cloud UNVERIFIED, credit0. — [research/challenge-8/cloud-build/origin-layout/R19-CLOSEOUT-20261022.json](cloud-build/origin-layout/R19-CLOSEOUT-20261022.json) SHA `64c5f76009562d166d0d057a6dab6e1198fd7431bb8a8dd867bac6656ceb055b`
- [SOURCE_REPORTED] R20 P1: compile5legs0; raw caller BOTH_TARGETS_EXIT0/stagesall0/sourceexact/posts preserved;5R19 controls MATCHED. Static shape != F5 resource negative. Bounded only, credit0. — [research/challenge-8/observations/28d241ff4bace6c455a0621a17de2bb59bc13cf90d79f14103b2dec836cb8557.json](observations/28d241ff4bace6c455a0621a17de2bb59bc13cf90d79f14103b2dec836cb8557.json) SHA `28d241ff4bace6c455a0621a17de2bb59bc13cf90d79f14103b2dec836cb8557` Build `196e1b52-23bf-47e8-bf0a-72caa5c1bbf2`; [research/challenge-8/observations/91dbaddf063900fe558593f5aeb413f306f4b691cd07575d77416e026cdb657a.json](observations/91dbaddf063900fe558593f5aeb413f306f4b691cd07575d77416e026cdb657a.json) SHA `91dbaddf063900fe558593f5aeb413f306f4b691cd07575d77416e026cdb657a` Build `196e1b52-23bf-47e8-bf0a-72caa5c1bbf2`
- [SOURCE_REPORTED] R20 P2: five R19 controls MATCHED; synthetic F5 failed callback/invariant setup gates, state fatal diagnostic lacks target context; both INCONCLUSIVE, credit0. — [research/challenge-8/cloud-build/origin-layout/R20-PROOF2-RESULT-20261023.json](cloud-build/origin-layout/R20-PROOF2-RESULT-20261023.json) SHA `2ae30e48c2f9114a3323966d64dee8333752446986b3a32c139bc74e33a03ca5` Build `17095248-45ee-433d-83d1-66679a8a1db5`; [research/challenge-8/observations/a848fcdc9a71e422dfc38da4c6e0454afe7d8eb5e6b6c7fd0c5d944c904909c6.json](observations/a848fcdc9a71e422dfc38da4c6e0454afe7d8eb5e6b6c7fd0c5d944c904909c6.json) SHA `a848fcdc9a71e422dfc38da4c6e0454afe7d8eb5e6b6c7fd0c5d944c904909c6` Build `17095248-45ee-433d-83d1-66679a8a1db5`; [research/challenge-8/observations/3c8c597476cc7dffd9fa35d51249e8805b4e2301ff7e9209df1c20b7dfb1a323.json](observations/3c8c597476cc7dffd9fa35d51249e8805b4e2301ff7e9209df1c20b7dfb1a323.json) SHA `3c8c597476cc7dffd9fa35d51249e8805b4e2301ff7e9209df1c20b7dfb1a323` Build `17095248-45ee-433d-83d1-66679a8a1db5`

## Open
- Original as_mut_ptr/unsize and real borrow/reference lifecycle plus full caller normal/unwind OPEN.
- Raw caller bounded source-reported exit0 only; state context and index-projection intended controls OPEN.
- F5 separate synthetic resource negative INCONCLUSIVE; actual missing-owner control is static shape refusal.
- Metadata tool191/profile0428 compile, checked content lemmas and final CURRENT/backedge/false/true/panic/Drop/Resume matrix OPEN.
- No B2/generic/arbitrary-n/sorting/tool qualification/independent credit.

## Rejected approaches
- Broad placeholder/cast inference exemption or address-only borrow bridge — Does not establish slice metadata, valid lifetime/full_borrow or memory authority; original gate must remain.; [research/challenge-8/cloud-build/origin-layout/R16-CALLER-DESIGN-20261021.md](cloud-build/origin-layout/R16-CALLER-DESIGN-20261021.md) SHA `c1e8f851b5c0b18edf3ed5ac2b758a32daa0eda2f4ea88551b8e37e03288b940`
- Short outer timeout990/execute570 chosen using prior whole-cycle timings — Missed nested compile reserve140; P4 timed out before proof. Keep full1200 plan unless effective inner budget reviewed.; [research/challenge-8/cloud-build/origin-layout/R16-REVIEW-20261021.md](cloud-build/origin-layout/R16-REVIEW-20261021.md) SHA `7ea120ef137323755ae4381de8915f8347d9a64bdd6b9e8b9753d561bdf70efa`

## Blocker
P4 WORKING; metadata/helper/controls unverified. Original caller OPEN.
- [research/challenge-8/cloud-build/origin-layout/R20-PROOF4-START-20261023.json](cloud-build/origin-layout/R20-PROOF4-START-20261023.json) SHA `f362938c350671793a786de90b899ba5a93bc786c91a0af2eec168671ce6dbe9` Build `0d3e7c6d-dfe4-4dbb-b5da-f0169d92ff53`

## Next
Prepare decoder record compatibility; terminal Brief when ready.

## Artifacts
- [research/challenge-8/cloud-build/origin-layout/R19-UNWIND-CLEANUP-DESIGN-20261022.md](cloud-build/origin-layout/R19-UNWIND-CLEANUP-DESIGN-20261022.md) — `571f1acd4a0ad8f86c7fe2bfa95e9a5a80450cbe0a5dc84c81fe5f8309ad857e`
- [research/challenge-8/cloud-build/origin-layout/R19-REVIEW-20261022.md](cloud-build/origin-layout/R19-REVIEW-20261022.md) — `6b9a227165ed4cc3ba6e71d77ee2083ca14c4505fe64205b2233068c444fc1a8`
- [research/challenge-8/cloud-build/origin-layout/R20-CALLER-AND-CONTROL-FRONTIER-20261023.md](cloud-build/origin-layout/R20-CALLER-AND-CONTROL-FRONTIER-20261023.md) — `d08d28d9859bfa6b319ceb99c22aade95e0f54efa02c27db93d44af4aca2f0f8`
- [research/challenge-8/cloud-build/origin-layout/R20-STATE-CONTROL-REVIEW-20261023.json](cloud-build/origin-layout/R20-STATE-CONTROL-REVIEW-20261023.json) — `c2050c3cde4909c2c2c631dc2ead4659753c6bbb00629b76726765fc5df9ba50`
- [research/challenge-8/cloud-build/origin-layout/R20-FINAL-ADOPTION-REVIEW-20261023.json](cloud-build/origin-layout/R20-FINAL-ADOPTION-REVIEW-20261023.json) — `d842a8f96a7d752686e4505b42fc20df79d08186018ba5a616e1e967376f9fd1`
