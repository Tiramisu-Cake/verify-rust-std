# TYPEUXVI result — B4 u16 dispatch safety: 7/7 SUCCESS, all ≤ 148 s, ≤ 3.15 GiB
Build `79fa3fcd-d5ba-453b-ad9f-1585453f80b4` after GO edd7e20803 (T0 dispatch 08:15:00Z; start 08:15:40Z, finish 08:31:21Z),
head `edd7e20803f592b881f2300ab9a54e2ca2229b3f`, request `typeuxvi-meas-dispatch-u16-20261104` (sha256 8d2d6de9…9da9a),
Kani 9461e07a, k1-standard4 (4 CPU, 15.6 GiB, swap off), controls on, jobs 1, uninit off, 600 s/row. check-tooling vs e0fda080f5: all ok.
Summary gate True, expectation met, Kani exit 0; no `[-]> .*smallsort` compile warning; dmesg OOM none. Cost $0.2160 (one Build, no repair).
| Root (`network::typematrix::dispatch_safety_`) | Status | VT s | failed/total | unreachable | covers | CBMC RSS GiB (PID) |
|---|---|---:|---|---:|---|---:|
| stable_unstable_u16_n0_1_2_7_8 | SUCCESS | 19.7 | 0/390 | 8 | 11/11 | 0.58 (9286) |
| stable_unstable_u16_n15_16_17 | SUCCESS | 147.6 | 0/380 | 7 | 7/7 | 3.15 (9257) |
| unstable_u16_n9_12_13_18 | SUCCESS | 62.4 | 0/377 | 12 | 5/5 | 1.50 (9315) |
| stable_u16_n31 | SUCCESS | 57.5 | 0/368 | 9 | 2/2 | 1.20 (9373) |
| stable_u16_n32 | SUCCESS | 60.7 | 0/368 | 9 | 2/2 | 1.25 (9402) |
| unstable_u16_n31 | SUCCESS | 78.7 | 0/368 | 12 | 2/2 | 1.31 (9431) |
| unstable_u16_n32 | SUCCESS | 85.0 | 0/368 | 12 | 2/2 | 1.34 (9344) |
## Gate and closed u16 cells
All 7 roots pass the root gate (SUCCESS, 0 failures, 31/31 covers). Row RSS = the row's own CBMC PID (`k1g.sh peaks` JSON rows,
jobs 1). Packet: kani-compiler 1.74, kani-driver 1.57 GiB; run wall 9:40. Unreachable checks are Kani data, not failures.
Closed: u16 (size 2, align 2) × 24 cells — stable `small_sort_general_with_scratch` at {0, 1, 2, 7, 8, 15, 16, 17, 31, 32},
unstable `small_sort_network` at {0, 1, 2, 7, 8, 9, 12, 13, 15, 16, 17, 18, 31, 32}; the same cells as the (u8, u32) candidates.
Scope as TYPEMATRIX: safety and normal return only, full u16 domain, uninit off; no sortedness or permutation.
## v7 candidates (GCB VT ≤ 300 s; next: full fork-CI)
All 7 u16 roots (19.7–147.6 s, ≤ 3.15 GiB); with the 19 of TYPEMATRIX/TYPESPLIT the type matrix has 26 candidates.
Evidence `typeuxvi/` (summary, peaks, tooling, cost, status, log-grep). Own $0.2160 of $1.40; project $93.0120, reserved $0, cap $98.96.
