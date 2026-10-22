# Agent checkpoint: select-c3-callback-autonomous-2026-10-22-r19

- Owner: select-sort4 | phase: SORT4-ACTUAL-C3-2026-10-22-R19 | state: HANDOFF
- Updated: 2026-10-22T15:00:30Z
- Baseline: source `81226dafedd2e8d1dfb140ab0e4dd88556bfd7db`, tool `f76012fb518703b1d98e243ac4f487f16877cfcb`, profile `87a0bfe586b40a33bdf840164aec8748872c8fdd11b3faad421d3860d1f2a091`
- Session dates: T0 `2026-10-22T13:50:26Z`; main deadline `2026-10-22T15:50:26Z`; absolute deadline `2026-10-22T16:20:26Z`
- Budget: 3600s total; 652s spent; 0s retired; 2948s remaining including active reservations
- Active Build IDs: 8916761a-a0a7-428a-b853-187e45ef4dfa
- Unresolved IDs: none recorded

## Confirmed claims
- [SOURCE_REPORTED] R17 closed: S1-S4 terminal/accounted (S4 FAILURE: c2 unselected full_borrow leak), carry0, credit0. — [research/challenge-8/task-history/select-actual-c2-r17/S4-evidence.json](task-history/select-actual-c2-r17/S4-evidence.json) SHA `c6cfa91918fd3f75732510638ac2aa41c8a7c38c84f195a86cd907f9bc4765c9` Build `27e8bfac-eb5f-4cf4-ae89-18bacd16eb90`; [research/challenge-8/cloud-build/sort4-caller-entry-native/BUDGET-A1-ACTUAL-C2-2026-10-21-R17.json](cloud-build/sort4-caller-entry-native/BUDGET-A1-ACTUAL-C2-2026-10-21-R17.json) SHA `5c857f5ef31b2fa45910bb3f11ad505dd0506a78fdcd6412bec8c9aa7d74bb46`
- [SOURCE_REPORTED] R18 S5 (a6550c20; pins 1e92d32b) FAILURE 576s: actual body passes c2 without leak error; first failure c3 lib.rs:299 missing ref_precreated_token(v_base+2+1). c2 resource controls fail as designed (message/location). Causality UNKNOWN; credit0. — [research/challenge-8/task-history/select-s5-r18/S5-evidence.json](task-history/select-s5-r18/S5-evidence.json) SHA `724da794e6172fe2000fbeb81406fd83fe68df29ffdc00cde35933ac0c414cda` Build `0ee7f658-50fe-4928-a7c9-3da5e56c95f2`
- [SOURCE_REPORTED] R18 CLOSED early: one Build terminal/accounted 576s, 3024s retired, carry0; own active/request/reservation0. credit0. — [research/challenge-8/cloud-build/sort4-caller-entry-native/BUDGET-A1-ACTUAL-C2-2026-10-22-R18.json](cloud-build/sort4-caller-entry-native/BUDGET-A1-ACTUAL-C2-2026-10-22-R18.json) SHA `69a9ca981bba6e6dcdceaf7c17a24a161aa07e376635a2c29ef8d74567368075`
- [SOURCE_REPORTED] R19 c3 candidate de2a2c69+f1fbef3c: N in {2,3} overlay, c3 layer (all four shares; refs for c/a), 8 c3 + count-off controls, profile 36bed85d by SHA allowlist. Review GO_WITH_NITS (+delta). Unverified; credit0. — [research/challenge-8/task-history/select-c3-r19/C3-review.json](task-history/select-c3-r19/C3-review.json) SHA `37ae0f830af3fc6c672c804826d68a0342eee5cab1fc22fadfb40c87d0f1f14f`; [research/challenge-8/task-history/select-c3-r19/C3-IMPLEMENTATION.md](task-history/select-c3-r19/C3-IMPLEMENTATION.md) SHA `52d510ded9d4c5d03c9cded0eee690d6b05340b4b3899e71ff8dd8bbb29a9dec`
- [SOURCE_REPORTED] R19 S1 (pins 67d472cd) FAILURE 652s: overlay compiled; actual body passes c3 (first path) and fails only at c4 lib.rs:335 (token d=v_base+2+0). 4 c3 resource controls designed; credit0. — [research/challenge-8/task-history/select-c3-r19/S1-evidence.json](task-history/select-c3-r19/S1-evidence.json) SHA `e95e4c0d1cc9ea49414cb71048d3bc8122a0afd634749c2a08a94be8980ca8f2` Build `2b55f6a5-076a-4fd6-92e9-c42aae9ba500`

## Open
- c4/c5 setup (count 4/5; c5 operands from selectors; empty deferred set at N=5).
- Full actual sort4 normal/unwind on all paths; selector/copy composition; controls/mini7/fresh26, Freeze caller; credit0.

## Rejected approaches
- Assumed/address-only resource bridge or helper PASS as full-body proof — Does not establish actual ordered callback resources or full normal/unwind posts.

## Blocker
c4 has no callback setup: No matching heap chunks ref_precreated_token<T>(ptr_add_(v_base,2+0)); overlay count limited to 3. (aliasing.rsspec(88,9-29) via verified/lib.rs(335,26-29) c4 call) [Build `2b55f6a5-076a-4fd6-92e9-c42aae9ba500`]
- [research/challenge-8/task-history/select-c3-r19/S1-evidence.json](task-history/select-c3-r19/S1-evidence.json) SHA `e95e4c0d1cc9ea49414cb71048d3bc8122a0afd634749c2a08a94be8980ca8f2` Build `2b55f6a5-076a-4fd6-92e9-c42aae9ba500`

## Next
Wait S2 Build 8916761a (c4, pins 3af7d37d) via smallsort-session wait; ack; Brief: c4 and controls by name/message/location; c5 draft ready (scratch).

## Artifacts
- [research/challenge-8/task-history/select-s5-r18/S5-evidence.json](task-history/select-s5-r18/S5-evidence.json) — `724da794e6172fe2000fbeb81406fd83fe68df29ffdc00cde35933ac0c414cda`
- [research/challenge-8/task-history/select-s5-r18/C3-NEXT-DESIGN.md](task-history/select-s5-r18/C3-NEXT-DESIGN.md) — `783591a28b6a0e4ae2073223e55528a2aa33d31237c96d12bb0fa9b29d06276e`
- [research/challenge-8/task-history/select-c3-r19/C3-IMPLEMENTATION.md](task-history/select-c3-r19/C3-IMPLEMENTATION.md) — `52d510ded9d4c5d03c9cded0eee690d6b05340b4b3899e71ff8dd8bbb29a9dec`
