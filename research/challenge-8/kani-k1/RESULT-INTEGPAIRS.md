# RESULT INTEGPAIRS — 4/4 PAIRS SAME-BUILD SUCCESS on integrated tree; matrix PARTIAL 16/55
Runtime Claude Code, no subagents; owner k1-merge. Library `2756f0e2a6` / tree `a45388ac593c809405558ea0c27599f487b17e4e` unchanged.
G1 Build `504cea68-dbfe-44f5-94b5-aa603f1a6b29` @`c20d0c0b86` (GO), request sha `b1c5ace0…e30fb2c`, Cloud 12:50:51–13:07:37 UTC.
G2 Build `52908448-39bb-43ac-b28e-c1c2931f7d75` @`5ba3c8b16b` (GO), request sha `216c2e26…1f9cc537`, Cloud 13:46:57–14:09:21 UTC.
Both: Cloud SUCCESS, lane COMPLETE, gate/expectation/measurement true, Kani exit 1 (expected controls only); check-tooling
vs e8e238db9d PASS; Kani 9461e07af7; measurement, k1-standard4 16 GiB swap off, controls, jobs1, uninit off, 600 s/row; dmesg OOM none.

## Positive rows (SUCCESS, 0 failed, covers = matrix)
| Build | Row (`verify::`) | Role | Failed/total; unr. | Covers | VT s | CBMC peak KiB |
|---|---|---|---|---|---|---|
| G1 | network::netcomp::netcomp_leaf_u8_n9 | leaf | 0/388; 5 | 7/7 | 58.638 | 315384 |
| G1 | network::netcomp::netcomp_composed_u8_n9 | consumer | 0/588; 18 | 6/6 | 98.408 | 989760 |
| G1 | network::u64nine::u64nine_leaf_u64_n9 | leaf | 0/388; 5 | 7/7 | 74.991 | 359272 |
| G1 | network::u64nine::u64nine_composed_u64_n9 | consumer | 0/588; 18 | 7/7 | 152.210 | 1347672 |
| G2 | merge::merge_scratch48_contract_u8_n9 | leaf | 0/571; 57 | 2/2 | 157.676 | 1324336 |
| G2 | bridge::bridgenine_caller_u8_n9 | consumer | 0/743; 59 | 3/3 | 24.172 | 349028 |
| G2 | bridge::bridgenine_direct_u8_n9 | baseline (no stubs) | 0/569; 53 | 2/2 | 207.768 | 425992 |
| G2 | network::netcomp::netcomp_leaf_u8_n13 | leaf | 0/388; 5 | 7/7 | 57.642 | 336380 |
| G2 | network::netcomp::netcomp_composed_u8_n13 | consumer | 0/588; 18 | 6/6 | 272.019 | 2154336 |

## Intended FAILED controls (sole located failed check = matrix literal/line; separate from positives)
| Build | Row | Failed/total; unr. | Sole failed check | Covers | VT s | CBMC peak KiB |
|---|---|---|---|---|---|---|
| G1 | netcomp_wrong_cmp_u8_n9 | 1/550; 29 | `netcomp canonical comparator required` netcomp.rs:122 | 2/2 | 0.534 | UNKNOWN (no sample) |
| G1 | netcomp_count_negative_u8_n9 | 1/569; 18 | `netcomp N9 negative: full-value count preserved` :242 | 3/3 | 65.403 | 945624 |
| G1 | u64nine_wrong_cmp_u64_n9 | 1/550; 29 | `u64nine canonical comparator required` u64nine.rs:123 | 2/2 | 0.517 | 35240 (model-path attribution) |
| G1 | u64nine_count_negative_u64_n9 | 1/570; 18 | `u64nine N9 negative: full-value count preserved` :235 | 3/3 | 79.970 | 1006568 |
| G2 | bridgenine_payload_flip_u8_n9 | 1/743; 58 | `bridgenine output preserves full-value probe count` bridge.rs:176 | 3/3 | 19.498 | 348788 |
| G2 | netcomp_wrong_cmp_u8_n13 | 1/550; 29 | `netcomp canonical comparator required` netcomp.rs:354 | 2/2 | 0.556 | UNKNOWN (no sample) |
| G2 | netcomp_count_negative_u8_n13 | 1/569; 18 | `netcomp N13 negative: full-value count preserved` :459 | 3/3 | 156.518 | 1909532 |

Pairs counted (leaf + consumer SUCCESS in one Build): netcomp u8 N9 (G1), u64nine u64 N9 (G1), bridgenine u8 N9 via merge
contract (G2), netcomp u8 N13 (G2).

## kani-driver (measured; 2 s sampler, kernel VmHWM; 30 s series = sampled RSS)
G1: driver VmHWM 4467072 KiB, first at sample 541 s; 2 s driver RSS 4401624 at 539 s. Window: u64nine_composed CBMC last
sample 537 s → u64nine_leaf start 543 s (±2 s); row attribution UNKNOWN. 30 s series: 6880 (90 s) → 314776 (120) → 1449088 (150)
→ 1987716 (210) → 2798900 (240) → 3025140 (361) → 3475128 (511) → 3282392 (541); compiler 1816332, sum peak 5105400 at 535 s.
G2: driver VmHWM 8252988 KiB = 2 s driver RSS at 916 s. Window: netcomp_composed_u8_n13 CBMC last 898 s → leaf13 start 924 s
(±2 s); attribution UNKNOWN. 30 s series: ~607912–731412 (120–571 s) → 1069876 (601) → 1864520 (631) → 2989128 (662–812)
→ 3791944 (842) → 4619340 (872) → 6060180 (902) → 5397912 (932); compiler 1871480, sum peak 8272164 at 916 s.
Run order (Kani, not request): G1 count9, wrong9, composed9, leaf9, u64 count, wrong, composed, leaf; G2 flip, caller, direct,
merge leaf, count13, wrong13, composed13, leaf13. Per-row driver growth beyond these windows: UNKNOWN (±30 s series only).

## Pair domains (leaf L / consumer C; details and source lines in integpairs/PREBUILD.md, PREBUILD-G2.md)
| Field | netcomp u8 N9 | u64nine u64 N9 | bridgenine u8 N9 | netcomp u8 N13 |
|---|---|---|---|---|
| T; F | u8; fn-ptr `U8Cmp` | u64; fn-ptr `U64Cmp` | u8; fn-ptr `fn(&u8,&u8)->bool` | u8; fn-ptr `U8Cmp` |
| CMP | `StrictU8::CMP`=strict_less | `StrictU64::CMP` | `LtU8::CMP`=lt_u8 (key x>>1) | `StrictU8::CMP` |
| Probe | any u8; L by value, C via CONTEXT9 → by value | any u64; same | static LtU8 probe, set before input (L, C) | any u8; L by value, C via CONTEXT13 |
| Backing/offset | exact [u8;9]+0 | exact [u64;9]+0 | src scratch48+0 (L: either form; C: [MaybeUninit;48]); dst [u8;9]+0 | exact [u8;13]+0 |
| Prefix/scratch/init/frame | full init, no scratch; L pair-only, C 25 hits | same | prefix9 init/tail39 uninit, split 4+5; dst9 frame | full init; L pair-only, C 45 hits |
| Binding | small_sort→network→sort9→stub adapter9→exchange→verified swap_net9 | …→adapter_u64nine→verified swap_u64_net9 | small_sort_general_with_scratch→stub adapter→MergeBridge→verified merge_profile | …sort13→adapter13→verified swap_net13 |

Matrix (parttwotree/proof-matrix.tsv): PARTIAL — 16 rows run here on tree a45388ac59, 39 rows NOT_RUN. Not ordinary credit.
Cost: own 2/2 Builds, $0.2295 + $0.3105 = $0.5400 ≤ cap $3.00, reserved $0. Project after: used $87.5310, cap $93.96.
Evidence: integpairs/g{1,2}.{summary.md,rows.txt,peaks-0.txt,log-grep.txt,tooling.txt,status.txt,cost.txt,assessment.json},
static-check, runs.json, budget-*.txt. Bounded K-1 outputs only; no raw logs/archives/Cloud Logging. No retry, no repair.
