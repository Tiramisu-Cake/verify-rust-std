# PARTTWO-TREE future proof matrix (NOT RUN in this stage)

Row data: `proof-matrix.tsv` (55 rows = 54 transferred opt-in roots + ordinary leaf `merge::merge_scratch48_contract_u8_n9`).
Historical column cites other trees/Builds for orientation only; none of it is credit for library tree
`a45388ac593c809405558ea0c27599f487b17e4e`. Running this matrix needs its own task, request(s) and GO.

Profile to reproduce the historical setup: measurement, controls:true, jobs1, uninit off, unwinding assertions on,
standard4 4CPU/16GiB swap off, 600 s/row; unwind per root as in `roots-manifest.tsv` (bridge/mergestep/N18 34,
network 25, wone 16). Part 2 profile decisions (uninit on, ordinary vs opt-in) remain open.

## A — SUCCESS gate (28 rows; all must be SUCCESS with full declared covers, 0 failed checks)

Leaf/consumer pairs must run in the same Build on the same tree (no cross-Build leaf reuse):

| Consumer | Matching leaf(s) | Exact shared domain |
|---|---|---|
| `bridge::bridge_caller_positive_u8_n3` | `bridge::bridge_leaf_u8_n3` | merge_profile<LtU8> N3 1+2, src[u8;3]+0, uninit dst[3]+0 |
| `bridge::bridgenine_caller_u8_n9` | `merge::merge_scratch48_contract_u8_n9` (ordinary) | Stable u8 N9, fnptr LtU8::CMP, scratch48 prefix9/tail39, dst[9]+0 |
| `network::netcomp::netcomp_composed_u8_n9` | `netcomp_leaf_u8_n9` | Unstable u8 N9, U8Cmp StrictU8::CMP, any [u8;9]+0 |
| `network::netcomp::netcomp_composed_u8_n13` | `netcomp_leaf_u8_n13` | Unstable u8 N13, any [u8;13]+0 |
| `network::u64nine::u64nine_composed_u64_n9` | `u64nine_leaf_u64_n9` | Unstable u64 N9, U64Cmp StrictU64::CMP, any [u64;9]+0 |
| `netcomp::netten::caller::nettencall_positive_u8_n10` | `netten_swap_prefix9_backing10`, `netten_insert_strict_u8_begin0_tail9` | Unstable u8 N10, any [u8;10]+0, shared probe |

Standalone theorems/baselines (16): `bridgenine_direct_u8_n9`, `netcomp_direct_u8_n9`, `directfour_merge4_u8`
(direct baselines); leaves without accepted consumer: `net18_swap_{left,right}_backing18`, `mergestep_{up,down}_leaf_u8`,
`u64thirteen_leaf_u64_n13`; wrappers `stable_cell_n0_to3`, `{unstable_byte,freeze_noncopy,stable_byte}_{n3,n2}`.

## B — expected FAILED (17 rows; separate gate)

Each must FAIL with exactly the one named literal/requires check of `proof-matrix.tsv` and the listed covers:
bridge wrong-F/unsorted (specfix.rs:317/:318), bridgenine payload flip (bridge.rs:176); wone always-true (:58),
payload corruption (:321); netcomp wrong-cmp 9/13 (:122/:354), count 9/13 (:242/:459); u64nine wrong-cmp/count
(:123/:235); u64thirteen wrong-cmp/count (:127/:240); nettencall swap/insert/count (:101/:162/:320);
mergestep count (:576). Expected failures are never part of an "all rows SUCCESS" gate.

## C — OPEN / timeout / diagnostic (10 rows; excluded from both gates)

OPEN (historical TIMEOUT/OOM, need reformulation, not scheduled): `wone::{unstable_byte,freeze_noncopy,stable_byte}_n0_to3`,
`u64thirteen_composed_u64_n13` (U64-N13 PARTIAL), `net18_merge_strict_scratch32`, `mergestep_composed_merge4_u8`.
Diagnostic: `mergestep_{up,down}_binding_negative_u8` (literal only, covers 2/4 and 3/4: MERGESTEP gate FAIL),
`bridge_frame_{positive,negative}_u8_n3` (frame calibration; positive covers 2/5 limitation).

Resource note from history: several A rows need 1–2.4 GiB CBMC and 200–330 s; nettencall drove kani-driver to
~14.1 GiB VmHWM in a 4-row Build, so a full matrix must be split into Builds that fit 16 GiB.
