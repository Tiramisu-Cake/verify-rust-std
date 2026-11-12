# KANI3300 M2 — reviewed test-only handoff
- Base: 5abdcf982da6aff65662e198af27a9c776830a89; tree 960a71c70b3f890b4f5cd2b53a83f6a0f8e00951.
- Candidate: 5f7f2b7364135a0a8b7cfd86c43b4491a8911bac; tree b2bbb7366a9fbac33398fb01be7300f83a1d27bd.
- Production 254ae69662b3206cd4432dae0cd44c534b1b13fb unchanged; no new model repair or D0 setter.
- Six harnesses/four RS selectors, eight added files in transfer-qualification; 41 legacy obligations mapped by hash.
- Legal ordinary/PFC and true conditional arm, ensures hole, full/partial out-pointer, normal/panic=abort controls prepared.
- Existing first/middle/last, nested/repeated, Item true/false, typed/raw/padding/data, frame/requires, Move controls reused.
- Diff/format/hash checks PASS static only; one Luna High review found no concrete test/CFG defect.
- New compile/runtime/property outcomes NOT_RUN; concrete bindings UNKNOWN; semantic acceptance remains BLOCKED.
- Mixed u8 differential and early MU Unsupported kept as separate coordinator-reported facts; no raw_eq credit for MU.
- Scope update @6fa8fbf979 incorporated: nested MU-of-flat outside Part1; owner15 repairs flat controls; M2 candidate unchanged.
- True unwind NOT_COVERED; M3/full gate not started. Cloud $0, dispatches0, Kani not pushed, proof credit NONE.
- Research handoff is limited to kani3300/m2/; READY denotes local reviewed candidate availability only.
- STOP: coordinator owns subsequent targeted inspection and existing Quick acceptance.
READY 5f7f2b7364135a0a8b7cfd86c43b4491a8911bac
