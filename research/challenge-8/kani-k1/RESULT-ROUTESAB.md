# RESULT ROUTESAB — existing opt-in general all-routes safety roots N9..15,17 (GCB, jobs1): PASS 8/8

Reviewed PRE-BUILD e9e702713f07 (coordinator GO; G2 pre-approved in that GO). Branch experiment/kani-k1-routesab-20261103, owner
k1-network; base 969c94f8591d, task afa9aefd5c5d. library tree d4ec476a7a00 = Part1 v6; merge.rs blob 12937938 (no library commit).
Kani 9461e07af7ec / nightly-2026-10-12; check-tooling vs frozen 30f77e859903 for both: pool ok, lane files equal, 6 bound files ok.
Profile gcb-e2-standard-4 → k1-standard4, 4 CPU/15.6 GiB, swap off, controls on, jobs 1, uninit off, 10 min/row, unwind 34.
G1 routesab-g1-measure-allroutes-n9to12-20261103 (cc730f7e…155e) → build c6bc3a65-7d5f-4276-89b4-e75da31f8158 @e9e70271;
  T0 dispatch 10:12:15Z, start 10:13:11Z, finish 10:23:02Z, Cloud SUCCESS, gate True, Kani exit 0. Receipt routesab/g1.result.md.
G2 routesab-g2-measure-allroutes-n13to15-n17-20261103 (b6068953…3e00) → build f7be2377-a9d1-40af-8fbe-959cfdc9da32 @cc472c9a;
  dispatch 10:26:48Z, start 10:27:38Z, finish 10:40:05Z, Cloud SUCCESS, gate True, Kani exit 0.

| Root (verify::merge::) | Pkt | Status | VT s | failed/total | unreach. | covers | CBMC row RSS |
|---|---|---|---:|---|---:|---|---:|
| route_safety_all_routes_n9 | G1 | SUCCESS | 29.2 | 0/613 | 11 | 4/4 | 0.63 GiB |
| route_safety_all_routes_n10 | G1 | SUCCESS | 38.9 | 0/613 | 11 | 4/4 | 0.71 GiB |
| route_safety_all_routes_n11 | G1 | SUCCESS | 38.8 | 0/613 | 11 | 4/4 | 0.77 GiB |
| route_safety_all_routes_n12 | G1 | SUCCESS | 43.2 | 0/613 | 11 | 4/4 | 0.86 GiB |
| route_safety_all_routes_n13 | G2 | SUCCESS | 54.5 | 0/613 | 11 | 4/4 | 1.07 GiB |
| route_safety_all_routes_n14 | G2 | SUCCESS | 56.1 | 0/613 | 11 | 4/4 | 1.17 GiB |
| route_safety_all_routes_n15 | G2 | SUCCESS | 62.8 | 0/613 | 11 | 4/4 | 1.24 GiB |
| route_safety_all_routes_n17 | G2 | SUCCESS | 121.7 | 0/613 | 9 | 4/4 | 1.60 GiB |

Row RSS: VmHWM of the single CBMC PID attributed `active=T0:<root>` (summary peaks; jobs 1). Unreachable counts are Kani data.
Packet peaks (per Build): G1 time -v max 2128244 KiB (2.03 GiB, kani-compiler), driver 0.64 GiB, process-sum 2.17 GiB, wall 3:49;
G2 time -v max 2128040 KiB (2.03 GiB, kani-compiler), cbmc 1.60, driver 1.07 GiB, process-sum 2.42 GiB, wall 6:16; OOM none_seen.
Covers 4/4 = PRE-BUILD forecast: normal return of each of the three routes (direct general u64, non-Copy Unstable general, Stable
u64 scratch 48) + abort_on_order_violation stub cover; the stub cover is not counted as a route return.
Gate: 8/8 accepted (identities/profile, SUCCESS, 0 unintended failures, all covers). No counterexample. Overall ROUTESAB PASS.
Cost: own spent $0.3105 (G1 $0.1350 + G2 $0.1755) of cap $1.95, own reserved $0.
Project after (10:42Z): 187 builds, used $83.9130, reserved by unfinished $0.0000 (PERMPROBE 87487311 now terminal; not ours), cap $88.96.

Meaning/limits: bounded normal-return safety of exact any `[u64;N]` on the three general/stable u64 routes, arbitrary volatile-reading
comparator, panic_on_ord_violation cut by cover+assume(false), unwind 34. Not correctness, not all T/F/impls, not unwind cleanup,
uninit checks off. Source unchanged → measurement, not a speed-up. Opt-in result only; ordinary 202/v7 unchanged; no PR/issue/CI.
Candidate-for-v7: all eight ≤300 s GCB shortlist (max n17 121.7 s); ≤600 s proof fit; macOS/jobs3 margin OPEN (no factor).
History (other trees/profiles, not matched): N9 34→29.2, N10 41→38.9, N12 43→43.2, N14 65→56.1 s; N11/N13/N15/N17 first records.
C–F advice (not run): VT grows ~4 s/N in the sort4 regime (N9..15), then ×1.9 at N17 when sort8_stable (two extra 8-merges)
starts. C[18..21] fits as 4 rows; split by route not needed upfront. D/E/F (N22..32, 3 more merge levels of insert_tail
work) are the likely >300 s risk: keep packet shape, but decide route-split for E[26..29]/F[30..32] after C/D VT, not now.
