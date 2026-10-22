# Agent checkpoint: select-s5-unselected-borrow-autonomous-2026-10-22-r18

- Owner: select-sort4 | phase: SORT4-ACTUAL-C2-2026-10-22-R18 | state: CLOSED
- Updated: 2026-10-22T13:07:56Z
- Baseline: source `81226dafedd2e8d1dfb140ab0e4dd88556bfd7db`, tool `f76012fb518703b1d98e243ac4f487f16877cfcb`, profile `87a0bfe586b40a33bdf840164aec8748872c8fdd11b3faad421d3860d1f2a091`
- Session dates: T0 `2026-10-22T12:12:06Z`; main deadline `2026-10-22T14:12:06Z`; absolute deadline `2026-10-22T14:42:06Z`
- Budget: 3600s total; 576s spent; 3024s retired; 0s remaining including active reservations
- Active Build IDs: none recorded
- Unresolved IDs: none recorded

## Confirmed claims
- [SOURCE_REPORTED] R17 S1-S3 terminal/accounted: S1 phase-allowlist run_error; S2 tool compile failure; S3 actual body c1 non-pure ghost read. Actual obligations closed0; credit0. — [research/challenge-8/task-history/select-actual-c2-r17/S1-evidence.json](task-history/select-actual-c2-r17/S1-evidence.json) SHA `9e02ff66640dfb90532a457a05e83bdc2426b2a68e3e252449b080f74d3e9148`; [research/challenge-8/task-history/select-actual-c2-r17/S2-evidence.json](task-history/select-actual-c2-r17/S2-evidence.json) SHA `7a1b4f8c2d939ca352117afccfa6aafc6d55f132798678346143aab1591b0024`; [research/challenge-8/task-history/select-actual-c2-r17/S3-evidence.json](task-history/select-actual-c2-r17/S3-evidence.json) SHA `f00873db2149b0156ab4e20fce138f8364bccdede88e0c2db73b101a8572edbf`
- [SOURCE_REPORTED] R17 S4 (candidate 51c4368b) terminal/accounted FAILURE 525s; actual body passes S3 c1 ghost-read and fails function-end leak check: unselected c2 full_borrow(cmp2_k) at v_base+0/+1, matching S5-UNSELECTED-BORROW-FIX.md. Causality UNKNOWN; actual obligations closed0; no control qualification; credit0. — [research/challenge-8/task-history/select-actual-c2-r17/S4-evidence.json](task-history/select-actual-c2-r17/S4-evidence.json) SHA `c6cfa91918fd3f75732510638ac2aa41c8a7c38c84f195a86cd907f9bc4765c9` Build `27e8bfac-eb5f-4cf4-ae89-18bacd16eb90`; [research/challenge-8/task-history/select-actual-c2-r17/observations/1568767949f9cb2325075a4b28c38d740e4c1d8755e9114723d84287ebbe5081.json](task-history/select-actual-c2-r17/observations/1568767949f9cb2325075a4b28c38d740e4c1d8755e9114723d84287ebbe5081.json) SHA `1568767949f9cb2325075a4b28c38d740e4c1d8755e9114723d84287ebbe5081`
- [SOURCE_REPORTED] R17 CLOSED (interrupted, absolute expired): four terminal/accounted Builds, 1995s used, 1605s retired, carry0; own active/unresolved/request/reservation0 after own status. No complete actual obligation or independent credit. — [research/challenge-8/cloud-build/sort4-caller-entry-native/BUDGET-A1-ACTUAL-C2-2026-10-21-R17.json](cloud-build/sort4-caller-entry-native/BUDGET-A1-ACTUAL-C2-2026-10-21-R17.json) SHA `5c857f5ef31b2fa45910bb3f11ad505dd0506a78fdcd6412bec8c9aa7d74bb46`
- [SOURCE_REPORTED] R18 S5 (a6550c20; pins 1e92d32b) FAILURE 576s: actual body passes c2 without leak error; first failure c3 lib.rs:299 missing ref_precreated_token(v_base+2+1). c2 resource controls fail as designed (message/location). Causality UNKNOWN; credit0. — [research/challenge-8/task-history/select-s5-r18/S5-evidence.json](task-history/select-s5-r18/S5-evidence.json) SHA `724da794e6172fe2000fbeb81406fd83fe68df29ffdc00cde35933ac0c414cda` Build `0ee7f658-50fe-4928-a7c9-3da5e56c95f2`
- [SOURCE_REPORTED] R18 CLOSED early: one Build terminal/accounted 576s, 3024s retired, carry0; own active/request/reservation0. credit0. — [research/challenge-8/cloud-build/sort4-caller-entry-native/BUDGET-A1-ACTUAL-C2-2026-10-22-R18.json](cloud-build/sort4-caller-entry-native/BUDGET-A1-ACTUAL-C2-2026-10-22-R18.json) SHA `69a9ca981bba6e6dcdceaf7c17a24a161aa07e376635a2c29ef8d74567368075`

## Open
- c3-c5 setup + translator index generalisation (C3-NEXT-DESIGN.md); new profile/review required.
- Full actual sort4 normal/unwind; selector/permutation/copy composition; controls/mini7/fresh26, Freeze caller; credit0.

## Rejected approaches
- Assumed/address-only resource bridge or helper PASS as full-body proof — Does not establish actual ordered callback resources or full normal/unwind posts.

## Blocker
c3 has no callback setup: No matching heap chunks ref_precreated_token<T>(ptr_add_(v_base,2+1)); translator overlay supports indices 1/2 only. (aliasing.rsspec(88,9-29) via verified/lib.rs(299,26-29) c3 call) [Build `0ee7f658-50fe-4928-a7c9-3da5e56c95f2`]
- [research/challenge-8/task-history/select-s5-r18/S5-evidence.json](task-history/select-s5-r18/S5-evidence.json) SHA `724da794e6172fe2000fbeb81406fd83fe68df29ffdc00cde35933ac0c414cda` Build `0ee7f658-50fe-4928-a7c9-3da5e56c95f2`

## Next
Implement C3-NEXT-DESIGN: generalise indexed overlay to N calls, c3 constructor sharing all four borrows; review; Cloud.

## Artifacts
- [research/challenge-8/task-history/select-s5-r18/S5-review.json](task-history/select-s5-r18/S5-review.json) — `26099067fcc01c07ba31d5e0e016dd3c5685fab65fb009a2ae91f6ef201e4085`
- [research/challenge-8/task-history/select-s5-r18/REGISTRATION.md](task-history/select-s5-r18/REGISTRATION.md) — `a193bbc5fc74a219970759fc8d4600355a1cc2960db142cd67157960cb7ec523`
- [research/challenge-8/task-history/select-s5-r18/R18-client-review.json](task-history/select-s5-r18/R18-client-review.json) — `6530c5b6b221a352c43aaa0144d99d0154294b32f378c78360da1b1d8b97b9fd`
- [research/challenge-8/task-history/select-s5-r18/S5-evidence.json](task-history/select-s5-r18/S5-evidence.json) — `724da794e6172fe2000fbeb81406fd83fe68df29ffdc00cde35933ac0c414cda`
- [research/challenge-8/task-history/select-s5-r18/C3-NEXT-DESIGN.md](task-history/select-s5-r18/C3-NEXT-DESIGN.md) — `783591a28b6a0e4ae2073223e55528a2aa33d31237c96d12bb0fa9b29d06276e`
