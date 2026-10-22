# Agent checkpoint: select-s5-unselected-borrow-autonomous-2026-10-22-r18

- Owner: select-sort4 | phase: SORT4-ACTUAL-C2-2026-10-22-R18 | state: HANDOFF
- Updated: 2026-10-22T12:50:00Z
- Baseline: source `81226dafedd2e8d1dfb140ab0e4dd88556bfd7db`, tool `f76012fb518703b1d98e243ac4f487f16877cfcb`, profile `87a0bfe586b40a33bdf840164aec8748872c8fdd11b3faad421d3860d1f2a091`
- Session dates: T0 `2026-10-22T12:12:06Z`; main deadline `2026-10-22T14:12:06Z`; absolute deadline `2026-10-22T14:42:06Z`
- Budget: 3600s total; 0s spent; 0s retired; 3600s remaining including active reservations
- Active Build IDs: 0ee7f658-50fe-4928-a7c9-3da5e56c95f2
- Unresolved IDs: none recorded

## Confirmed claims
- [SOURCE_REPORTED] R16 S5 reached actual c2; source-reported missing ref_precreated_token(v_base+3). credit0. — [research/challenge-8/task-history/select-actual-lifetime-r16/S5-evidence.json](task-history/select-actual-lifetime-r16/S5-evidence.json) SHA `209199ccfeef37d698b97216466b3f726d383358fa274e8e887f1ca5ead6ca51` Build `acd8e010-16b8-4b58-9501-083cb10b595f`
- [SOURCE_REPORTED] R16 CLOSED: five Builds terminal/accounted, 2170s spent, 1430s retired, carry0. credit0. — [research/challenge-8/cloud-build/sort4-caller-entry-native/BUDGET-A1-ACTUAL-LIFETIME-2026-10-21-R16.json](cloud-build/sort4-caller-entry-native/BUDGET-A1-ACTUAL-LIFETIME-2026-10-21-R16.json) SHA `64819aa0be35fd1f84e6c90109c33cf944cbac9afcb26ca4598d066f18c4aa45`
- [SOURCE_REPORTED] R17 S1-S3 terminal/accounted: S1 phase-allowlist run_error; S2 tool compile failure; S3 actual body c1 non-pure ghost read. Actual obligations closed0; credit0. — [research/challenge-8/task-history/select-actual-c2-r17/S1-evidence.json](task-history/select-actual-c2-r17/S1-evidence.json) SHA `9e02ff66640dfb90532a457a05e83bdc2426b2a68e3e252449b080f74d3e9148`; [research/challenge-8/task-history/select-actual-c2-r17/S2-evidence.json](task-history/select-actual-c2-r17/S2-evidence.json) SHA `7a1b4f8c2d939ca352117afccfa6aafc6d55f132798678346143aab1591b0024`; [research/challenge-8/task-history/select-actual-c2-r17/S3-evidence.json](task-history/select-actual-c2-r17/S3-evidence.json) SHA `f00873db2149b0156ab4e20fce138f8364bccdede88e0c2db73b101a8572edbf`
- [SOURCE_REPORTED] R17 S4 (candidate 51c4368b) terminal/accounted FAILURE 525s; actual body passes S3 c1 ghost-read and fails function-end leak check: unselected c2 full_borrow(cmp2_k) at v_base+0/+1, matching S5-UNSELECTED-BORROW-FIX.md. Causality UNKNOWN; actual obligations closed0; no control qualification; credit0. — [research/challenge-8/task-history/select-actual-c2-r17/S4-evidence.json](task-history/select-actual-c2-r17/S4-evidence.json) SHA `c6cfa91918fd3f75732510638ac2aa41c8a7c38c84f195a86cd907f9bc4765c9` Build `27e8bfac-eb5f-4cf4-ae89-18bacd16eb90`; [research/challenge-8/task-history/select-actual-c2-r17/observations/1568767949f9cb2325075a4b28c38d740e4c1d8755e9114723d84287ebbe5081.json](task-history/select-actual-c2-r17/observations/1568767949f9cb2325075a4b28c38d740e4c1d8755e9114723d84287ebbe5081.json) SHA `1568767949f9cb2325075a4b28c38d740e4c1d8755e9114723d84287ebbe5081`
- [SOURCE_REPORTED] R17 CLOSED (interrupted, absolute expired): four terminal/accounted Builds, 1995s used, 1605s retired, carry0; own active/unresolved/request/reservation0 after own status. No complete actual obligation or independent credit. — [research/challenge-8/cloud-build/sort4-caller-entry-native/BUDGET-A1-ACTUAL-C2-2026-10-21-R17.json](cloud-build/sort4-caller-entry-native/BUDGET-A1-ACTUAL-C2-2026-10-21-R17.json) SHA `5c857f5ef31b2fa45910bb3f11ad505dd0506a78fdcd6412bec8c9aa7d74bb46`

## Open
- S5 a6550c20: reviewer GO_WITH_NITS; Cloud Build 0ee7f658 (pins 1e92d32b) pending; credit0.
- Read each S5 control diagnostic/location in Brief (qualification checks only exit).
- Full actual sort4 normal/unwind; ordered c1–c5 attribution/current-owner recovery, selector-pointer/permutation/copy composition.
- Required HRTB-off/controls completion, final mini7/fresh26, qualification and stable Freeze caller; independent B1/B2 credit0.

## Rejected approaches
- Assumed/address-only resource bridge or helper PASS as full-body proof — Does not establish actual ordered callback resources or full normal/unwind posts.

## Blocker
Function leaks heap chunks: unselected c2 full_borrow(cmp2_k, full_borrow_content(T,t)) at v_base+1 and v_base; full actual normal/unwind OPEN. (verified/lib.rs(314,1-2), actual body leak check) [Build `27e8bfac-eb5f-4cf4-ae89-18bacd16eb90`]
- [research/challenge-8/task-history/select-actual-c2-r17/S4-evidence.json](task-history/select-actual-c2-r17/S4-evidence.json) SHA `c6cfa91918fd3f75732510638ac2aa41c8a7c38c84f195a86cd907f9bc4765c9` Build `27e8bfac-eb5f-4cf4-ae89-18bacd16eb90`

## Next
WAITING S5 Build 0ee7f658 via wait; ack, then Brief: c2 leak check and controls by message/location.

## Artifacts
- [research/challenge-8/task-history/select-actual-c2-r17/S4-evidence.json](task-history/select-actual-c2-r17/S4-evidence.json) — `c6cfa91918fd3f75732510638ac2aa41c8a7c38c84f195a86cd907f9bc4765c9`
- [research/challenge-8/task-history/select-actual-c2-r17/S5-UNSELECTED-BORROW-FIX.md](task-history/select-actual-c2-r17/S5-UNSELECTED-BORROW-FIX.md) — `f7b9e8522fc7cf08a15011682c7368bc0cc8673df3f54f6dbbc438274ef3dca4`
- [research/challenge-8/task-history/select-s5-r18/S5-review.json](task-history/select-s5-r18/S5-review.json) — `26099067fcc01c07ba31d5e0e016dd3c5685fab65fb009a2ae91f6ef201e4085`
- [research/challenge-8/task-history/select-s5-r18/REGISTRATION.md](task-history/select-s5-r18/REGISTRATION.md) — `a193bbc5fc74a219970759fc8d4600355a1cc2960db142cd67157960cb7ec523`
- [research/challenge-8/task-history/select-s5-r18/R18-client-review.json](task-history/select-s5-r18/R18-client-review.json) — `6530c5b6b221a352c43aaa0144d99d0154294b32f378c78360da1b1d8b97b9fd`
