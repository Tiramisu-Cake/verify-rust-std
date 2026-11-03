# TYPESPLIT result — B4 `_n31_32` pair roots split by route × length: 12/12 SUCCESS, all ≤ 190 s
Build `de53e600-f485-4f43-bb2b-5b51ef686368` after GO b595df116a (T0 dispatch 18:54:20Z; start 18:55:15Z, finish 19:30:51Z),
head `b595df116a8b9ea63df8f8d4cca5f1685fcf6d95`, request `typesplit-meas-dispatch-n31-n32-route-split-20261103` (sha256 2f5b88dc…4390),
Kani 9461e07a, k1-standard4 (4 CPU, 15.6 GiB, swap off), controls on, jobs 1, uninit off, 600 s/row. check-tooling vs e8e238db9d: all ok.
Summary gate True, expectation met, Kani exit 0; no `[-]> .*smallsort` compile warning; dmesg OOM none. Cost $0.4860 (one Build, no repair).
| Root (`network::typematrix::dispatch_safety_`) | Status | VT s | failed/total | unreachable | covers | CBMC RSS GiB (PID) |
|---|---|---:|---|---:|---|---:|
| stable_u8u32_n31 | SUCCESS | 88.2 | 0/368 | 9 | 2/2 | 1.32 (9292) |
| stable_u8u32_n32 | SUCCESS | 95.8 | 0/368 | 9 | 2/2 | 1.37 (9437) |
| unstable_u8u32_n31 | SUCCESS | 110.3 | 0/368 | 12 | 2/2 | 1.36 (9582) |
| unstable_u8u32_n32 | SUCCESS | 119.0 | 0/368 | 12 | 2/2 | 1.42 (9495) |
| stable_u128_n31 | SUCCESS | 151.4 | 0/368 | 9 | 2/2 | 1.25 (9408) |
| stable_u128_n32 | SUCCESS | 120.0 | 0/368 | 9 | 2/2 | 1.31 (9611) |
| unstable_u128_n31 | SUCCESS | 77.5 | 0/368 | 8 | 2/2 | 1.28 (9466) |
| unstable_u128_n32 | SUCCESS | 90.5 | 0/368 | 8 | 2/2 | 1.34 (9350) |
| stable_bytes9_n31 | SUCCESS | 98.5 | 0/368 | 9 | 2/2 | 1.38 (9553) |
| stable_bytes9_n32 | SUCCESS | 107.8 | 0/368 | 9 | 2/2 | 1.43 (9524) |
| unstable_bytes9_n31 | SUCCESS | 145.7 | 0/368 | 8 | 2/2 | 1.72 (9321) |
| unstable_bytes9_n32 | SUCCESS | 190.0 | 0/368 | 8 | 2/2 | 1.79 (9379) |
## Gate and cells
All 12 roots pass the root gate (SUCCESS, 0 failures, 24/24 covers). Row RSS = the row's own CBMC PID (`k1g.sh peaks`, attribution
direct, jobs 1). Packet: max RSS 1.79 GiB (cbmc), kani-driver 1.74, kani-compiler 1.72, sampled process sum 2.91 GiB; run wall 25:07.
Sum of VT 1394.6 s vs 1523.6 s of the three pair roots. Unreachable checks are Kani-reported data, not failures.
Every N31/32 cell got its own root ≤ 300 s: (u8, u32), u128, [u8; 9] × stable `small_sort_general_with_scratch` × 31, 32
(88–151 s) and × unstable (`small_sort_network` for (u8, u32): 110–119 s; `small_sort_general` for u128, [u8; 9]: 77–190 s).
Same scope as TYPEMATRIX: safety and normal return only, uninit off; no sortedness, permutation or padding contents.
## v7 candidates of the type matrix (GCB VT ≤ 300 s; next: full fork-CI)
19 roots: TYPEMATRIX 7 — u8u32/u128/bytes9 `_n0_1_2_7_8` and `_n15_16_17`, `dispatch_safety_unstable_u8u32_n9_12_13_18`
(26–203 s, ≤ 3.4 GiB) — plus these 12 (77–190 s, ≤ 1.8 GiB). The three pair `_n31_32` roots stay in source, not candidates.
Evidence `typesplit/` (summary, peaks, tooling, cost, status, log-grep). Own $0.4860 of $2.05; project $91.3380, reserved $0, cap $93.96.
