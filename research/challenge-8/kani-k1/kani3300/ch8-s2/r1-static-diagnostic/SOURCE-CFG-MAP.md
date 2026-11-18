# Source/cfg dependency map

Source 9fd558c9dab5ec26abdb1226eb5f2b9cd9ffbff6; stock 0aac16ef62da9e9d5645782d458593e5d78143ba; control 2ecf5e839f898f6bb1cd96edd6cc6bf677acb4c8.

All paths/lines bind to full commit/blob/SHA256 and exact excerpts in SOURCE-CFG-MAP.json. Reused input identities are in PROVENANCE.json. Static availability only; no compiler ran.

K=kani; S=kani_smallsort_sorting; C=kani_smallsort_controls; A=kani_smallsort_s2_assumed. All11 roots use K,S,C,A.

| Dependency | Gate | Source location | At K,S,C,A |
|---|---|---|---|
| core→slice→sort→shared→smallsort | No additional relevant gate | lib.rs:330; slice/mod.rs:40; sort/mod.rs:8; shared/mod.rs:6 | Active |
| verify | K | smallsort.rs:998–1000 | Active |
| sorting_model; KeyLess/Snapshot | K && S via module | verify.rs:83–84; sorting_model.rs:22,45–70,150–158 | Active |
| sort8 requires/modifies/ensures | K && S && A | smallsort.rs:770–772 | All active |
| sort8 declaration/body | Unconditional | smallsort.rs:773–790 | Active with contracts |
| disjoint helper | K | smallsort.rs:858–866 | Active, same module, no import |
| sorting_s2_span facade, both impls | K && S && A via module | verify.rs:95–96; sorting_s2_span.rs:5–53 | Active declarations; u8/KeyLess selects active impl |
| insert_tail/merge S2 predicates | K && S && A | smallsort.rs:627–628,886–887 | Active |
| batch and sort8 registration | K && S && A via module | verify.rs:97–98; sorting_s2_batch.rs:168–176 | Active; registration not selected for execution |
| sorting_s2_swap | K && S && A via module | verify.rs:93–94 | Active |
| S1 control modules | K && S && C | verify.rs:87–90 | Active additional compiled items |
| helper_contracts providers | K via verify; comparator-frame control also C | verify.rs:70; helper_contracts.rs:270 | Active |
| stock parsing/old lifter | Contract macros | initialize.rs:60–69,93–110; shared.rs:138–254 | Implementation inspected; expansion NOT_RUN |
| stock post application | Fn(&R)->bool | kani_core/src/lib.rs:693 | R=(); bool post |
| stock registration validation | All crate free items | kani_middle/mod.rs:83–128 | Algorithm inspected; execution NOT_RUN |

Source paths are under library/core/src/slice/sort/shared/ unless specified. Macro files are under library/kani_macros/src/sysroot/contracts/. Complete exact paths are in JSON.

| Root (all active under K,S,C,A) | batch function line | Mode | Verified stub → PFC providers | Ordinary stub |
|---|---:|---|---|---|
| swap_pfc | 73 | PFC | none | none |
| summary_witness | 101 | Original | none | none |
| merge32_real | 28 | Original | none | none |
| sort13_assumed | 41 | Original | swap_if_less → swap_safety_u8_backing4@49, swap_safety_u64_backing4@55, swap_safety_bytes17_backing4@61, swap_safety_u8_backing9@121, swap_safety_u8_backing13@127, rejects_swap_comparator_writing_outside_frame_u8@271, swap_pfc@71 | none |
| general32_assumed | 58 | Original | sort8_stable → sort8_registration_only@168<br>insert_tail → insert_tail_safety_u64_tail1_to4_backing5@157<br>bidirectional_merge → merge_safety_u64_len2@240, merge_safety_u64_len4@247 | none |
| merge_order_corrupt | 117 | Original | none | none |
| merge_count_corrupt | 124 | Original | none | none |
| checker_count_corrupt | 131 | Original | none | none |
| checker_order_corrupt | 137 | Original | none | none |
| sort13_weak | 145 | Original | none | swap_if_less → weak_swap |
| general32_weak | 159 | Original | sort8_stable → sort8_registration_only@168<br>insert_tail → insert_tail_safety_u64_tail1_to4_backing5@157 | bidirectional_merge → weak_merge |

Providers are in helper_contracts.rs except swap_pfc@71 and sort8_registration_only@168 in sorting_s2_batch.rs. Existing u64 safety PFC presence does not qualify u8 semantic summaries. Root source hashes and full provider paths are in JSON.

| K | S | C | A | sort8 attrs / span / batch registration | disjoint helper |
|---|---|---|---|---|---|
| 1 | 1 | 1 | 1 | active | active |
| 1 | 1 | 0 | 1 | active | active |
| 1 | 1 | 1 | 0 | inactive | active |
| 1 | 0 | 1 | 1 | inactive | active |
| 0 | 1 | 1 | 1 | inactive | inactive |

With K=0 sort8 remains an ordinary declaration while its contracts/helper/verify modules are absent. With S=0 or A=0 S2 attrs/modules disappear together. C is not a gate on the S2 negative roots. Counterfactual rows are not runs.

O→r1: only13 appended registration lines in sorting_s2_batch.rs; old file is an exact byte prefix. Sort8 contracts/body, span and disjoint helper are unchanged.
