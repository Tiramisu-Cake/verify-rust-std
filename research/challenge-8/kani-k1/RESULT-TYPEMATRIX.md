# TYPEMATRIX result — B4 dispatch safety on (u8, u32), u128, [u8; 9]: 10/10 SUCCESS
Build `5b4d8db6-bb4e-4d78-b344-a8a0e8389c81` after GO 6a14da38b8 (T0 dispatch 17:11:30Z; start 17:12:57Z, finish 17:59:29Z),
head `6a14da38b8a2772474c8b6d0bd59c33356284433`, request `typematrix-meas-dispatch-u8u32-u128-bytes9-20261103` (sha256 b122e59d…0b5d),
Kani 9461e07a, k1-standard4 (4 CPU, 15.6 GiB, swap off), controls on, jobs 1, uninit off, 600 s/row. check-tooling vs e8e238db9d: all ok.
Summary gate True, expectation met, Kani exit 0; no `[-]> .*smallsort` compile warning; dmesg OOM none. Cost $0.6345 (one Build, no repair).
| Root (`network::typematrix::`) | Status | VT s | failed/total | unreachable | covers | CBMC RSS GiB (PID) |
|---|---|---:|---|---:|---|---:|
| dispatch_safety_stable_unstable_u8u32_n0_1_2_7_8 | SUCCESS | 26.4 | 0/390 | 8 | 11/11 | 0.65 (9393) |
| dispatch_safety_stable_unstable_u8u32_n15_16_17 | SUCCESS | 202.7 | 0/380 | 7 | 7/7 | 3.34 (9335) |
| dispatch_safety_stable_unstable_u8u32_n31_32 | SUCCESS | 538.3 | 0/375 | 6 | 5/5 | 6.56 (9277) |
| dispatch_safety_stable_unstable_u128_n0_1_2_7_8 | SUCCESS | 32.6 | 0/390 | 9 | 11/11 | 0.73 (9480) |
| dispatch_safety_stable_unstable_u128_n15_16_17 | SUCCESS | 176.4 | 0/380 | 8 | 7/7 | 3.18 (9422) |
| dispatch_safety_stable_unstable_u128_n31_32 | SUCCESS | 452.5 | 0/375 | 8 | 5/5 | 6.46 (9509) |
| dispatch_safety_stable_unstable_bytes9_n0_1_2_7_8 | SUCCESS | 46.8 | 0/390 | 9 | 11/11 | 0.89 (9364) |
| dispatch_safety_stable_unstable_bytes9_n15_16_17 | SUCCESS | 187.2 | 0/380 | 8 | 7/7 | 3.39 (9451) |
| dispatch_safety_stable_unstable_bytes9_n31_32 | SUCCESS | 532.8 | 0/375 | 8 | 5/5 | 6.82 (9306) |
| dispatch_safety_unstable_u8u32_n9_12_13_18 | SUCCESS | 80.4 | 0/377 | 12 | 5/5 | 1.58 (9538) |
## Gate and closed cells
All 10 roots pass the root gate (SUCCESS, 0 failures, 74/74 covers). Row RSS = one CBMC PID per row (`k1g.sh peaks`, active root,
jobs 1). Packet: max RSS 6.82 GiB (cbmc), kani-driver 2.39, kani-compiler 1.77, sampled process sum 8.33 GiB; run wall 39:19.
Unreachable checks are Kani-reported data, not failures. Closed cells (type × route × lengths; default checks on normal-return paths):
- stable `small_sort_general_with_scratch` (scratch 48): (u8, u32), u128, [u8; 9] at 0,1,2,7,8,15,16,17,31,32;
- unstable `small_sort_network`: (u8, u32) at 0,1,2,7,8,9,12,13,15,16,17,18,31,32 (sort9, sort13, merge 18/31/32);
- unstable `small_sort_general` (stack scratch 48): u128 (align 16) and [u8; 9] at 0,1,2,7,8,15,16,17,31,32.
Routes by source and by the module's const assertions (x86_64/aarch64); layout of `(u8, u32)` is a toolchain fact, not a language
guarantee. Not shown: uninit/validity (uninit checks off), byte-level permutation, padding contents, u16 (deferred), sortedness.
## v7 candidates (GCB VT ≤ 300 s; next: full fork-CI)
7 rows: u8u32/u128/bytes9 `_n0_1_2_7_8` and `_n15_16_17`, and `dispatch_safety_unstable_u8u32_n9_12_13_18` (26–203 s, ≤ 3.4 GiB).
The three `_n31_32` rows SUCCESS at 452–538 s, 6.5–6.8 GiB: bounded fact, over the 300 s line, not candidates; no split here.
Evidence `typematrix/` (summary, peaks, tooling, cost, status, log-grep). Own $0.6345 of $1.80; project $89.9475, reserved $0, cap $93.96.
