# RESULT SAFETYNET — four existing opt-in u64 network safety roots N18..29 (GCB, jobs1): PASS 4/4

Reviewed PRE-BUILD 8c4ef5735f17 (coordinator GO). Branch experiment/kani-k1-safetynet-20261103, owner k1-network; base 2104e7a596fa,
task a64fecc570cf. library tree d4ec476a7a00 = Part1 v6; network.rs blob 1a85a483 (source/roots/covers/F/domain unchanged, no
library commit). Kani 9461e07af7ec / nightly-2026-10-12; check-tooling vs frozen 30f77e859903: pool ok, lane files equal, 6 bound
files ok. Profile gcb-e2-standard-4 → k1-standard4, 4 CPU/15.6 GiB, swap off, controls on, jobs 1, uninit off, 10 min/row, unwind 35.
Request safetynet-g1-measure-u64netsafety4-n18to29-20261103 (aa2e18fa…e7a6) → build 19a9e92a-5073-4de1-9f9a-d3097bd8d703 @8c4ef573.
T0 dispatch 09:37:45Z; start 09:39:10Z, finish 10:00:40Z, Cloud SUCCESS. Gate True, expectation met, measurement ok, Kani exit 0.

| Root (verify::network::) | Status | VT s | failed/total | unreach. | covers | CBMC row RSS |
|---|---|---:|---|---:|---|---:|
| network_safety_unstable_u64_n18_to21 | SUCCESS | 174.6 | 0/296 | 12 | 6/6 | 2.64 GiB |
| network_safety_unstable_u64_n22_to25 | SUCCESS | 220.2 | 0/296 | 12 | 6/6 | 3.26 GiB |
| network_safety_unstable_u64_n26_to27 | SUCCESS | 212.6 | 0/296 | 12 | 4/4 | 2.21 GiB |
| network_safety_unstable_u64_n28_to29 | SUCCESS | 211.4 | 0/296 | 12 | 4/4 | 2.36 GiB |

Row RSS: VmHWM of the single CBMC PID attributed `active=T0:<root>` (summary peaks; jobs 1). Unreachable counts are Kani data.
Packet peaks (per Build): time -v max 3419896 KiB (3.26 GiB, = cbmc), kani-compiler 1.65 GiB, kani-driver 1.85 GiB, sampled
process-sum 4.46 GiB at 628 s, wall 14:56; dmesg OOM none_seen. Covers equal the PRE-BUILD source forecast (per-length normal
return + family end + panic-stub cover); every per-length return cover satisfied, the stub cover is not counted as a return.
Gate: 4/4 accepted (identities/profile match, SUCCESS, 0 unintended failures, all original covers). Overall SAFETYNET PASS.
Cost: own spent $0.2970 of cap $1.00, own reserved $0. Project after: 185 builds, used $83.0895, reserved $1.0800 (foreign
unfinished build, not ours, untouched), cap $88.96.

Meaning/limits: bounded normal-return safety of exact any `[u64;N]`, N18..29, arbitrary volatile-reading bool comparator, actual
UnstableSmallSortTypeImpl → network merge route, panic_on_ord_violation cut by cover+assume(false), unwind 35. Not correctness,
not all T/F, not general/Stable, not unwind cleanup, uninit checks off. Source unchanged → measurement, not a speed-up.
Candidate-for-Mac: all four ≤300 s GCB shortlist (max 220.2 s, n22_to25 first, then n26_to27, n28_to29, n18_to21); macOS/jobs3
400–450 s margin stays OPEN (no conversion factor); n18_to21 116.9 s was earlier source afea78b3, not a matched baseline.
Opt-in result only; ordinary 202/v7 unchanged; no external PR/issue/CI. Next general packets — plan only, NOT run; each a separate future stage/cap/GO on the same v6 library + 30f77e85/9461e07a pins:
existing `merge::route_safety_all_routes_nN` (23 opt-in, cfg controls; N2..8,16 are ordinary) A[9,10,11,12] B[13,14,15,17]
C[18,19,20,21] D[22,23,24,25] E[26,27,28,29] F[30,31,32]: 5×4-row $0.945 + 1×3-row $0.810 = $5.535. Body
all_upper_routes_safety_body: any route → direct general u64 / non-Copy Unstable general / Stable u64 (scratch 48), stub
abort_on_order_violation (cover), unwind 34. Per-route covers/frames inventoried in each PREBUILD; not all types/impls; revisit after A/B.
