# RESULT ROUTESEF — existing opt-in general all-routes safety roots N26..32 (GCB, jobs1): PASS 7/7

Reviewed PRE-BUILD 604e01b4e35e (coordinator GO; G2 pre-approved in that GO). Branch experiment/kani-k1-routesef-20261103, owner
k1-network; base 7ef2f27a81af, task c5dbc40f2d10. library tree d4ec476a7a00 = Part1 v6; merge.rs blob 12937938 (no library commit).
Kani 9461e07af7ec / nightly-2026-10-12; check-tooling vs tooling base e8e238db9d87 (= 30f77e85 + CAP_USD) for both: pool ok, lane
files equal, 6 bound files ok. Profile gcb-e2-standard-4 → k1-standard4, 4 CPU/15.6 GiB, swap off, controls on, jobs 1, uninit off,
10 min/row, unwind 34, stub panic_on_ord_violation → abort_on_order_violation.
G1 routesef-g1-measure-allroutes-n26to29-20261103 (7cba0f02…f49b) → build 6515c8ee-8f2c-49fb-b76c-f1cc70834fb2 @604e01b4;
  T0 dispatch 11:38:06Z, start 11:39:28Z, finish 12:03:50Z, Cloud SUCCESS, gate True, Kani exit 0. Receipt routesef/g1.result.md.
G2 routesef-g2-measure-allroutes-n30to32-20261103 (76ca39b8…1c14) → build a7795d09-1bb4-466a-b503-b6dc9204616d @b73a44f4;
  dispatch 12:07:30Z, start 12:09:05Z, finish 12:35:37Z, Cloud SUCCESS, gate True, Kani exit 0.

| Root (verify::merge::) | Pkt | Status | VT s | failed/total | unreach. | covers | CBMC row RSS |
|---|---|---|---:|---|---:|---|---:|
| route_safety_all_routes_n26 | G1 | SUCCESS | 243.8 | 0/613 | 9 | 4/4 | 3.03 GiB |
| route_safety_all_routes_n27 | G1 | SUCCESS | 218.6 | 0/613 | 9 | 4/4 | 3.19 GiB |
| route_safety_all_routes_n28 | G1 | SUCCESS | 234.2 | 0/613 | 9 | 4/4 | 3.35 GiB |
| route_safety_all_routes_n29 | G1 | SUCCESS | 253.7 | 0/613 | 9 | 4/4 | 3.35 GiB |
| route_safety_all_routes_n30 | G2 | SUCCESS | 307.7 | 0/613 | 9 | 4/4 | 3.72 GiB |
| route_safety_all_routes_n31 | G2 | SUCCESS | 329.2 | 0/613 | 9 | 4/4 | 3.93 GiB |
| route_safety_all_routes_n32 | G2 | SUCCESS | 358.9 | 0/613 | 9 | 4/4 | 4.12 GiB |
Row RSS = VmHWM of the one CBMC PID attributed `active=T0:<root>` (jobs 1); unreachable counts are Kani data. Packet peaks (per
Build): G1 time -v max 3513332 KiB (3.35 GiB, cbmc), kani-compiler 2.01, driver 1.60, process-sum 4.31 GiB, wall 17:14; G2 time -v
max 4320440 KiB (4.12 GiB, cbmc), kani-compiler 1.89, driver 1.73, process-sum 5.14 GiB, wall 18:17; OOM none_seen.
Covers 4/4 = PRE-BUILD forecast: 3 route normal returns (direct general, non-Copy Unstable, Stable scratch 48) + stub cover (no return).
Gate: 7/7 accepted (identities/profile, SUCCESS, 0 unintended failures, all covers). No counterexample. Overall ROUTESEF PASS.
Cost: own spent $0.7020 (G1 $0.3375 + G2 $0.3645) of cap $1.80, own reserved $0; no repair used. T0 11:38:06Z, G2 terminal
12:35:37Z. Project after (12:37Z): 195 builds, used $86.2350, reserved by unfinished $0.0000, cap $93.96.
Meaning/limits: bounded normal-return safety of any `[u64;N]` on the three routes, arbitrary volatile-reading comparator, panic cut by
cover+assume(false), unwind 34; not correctness/all T/unwind cleanup, uninit off. Measurement only; ordinary 202/v7 unchanged; no PR/CI.
Candidate-for-v7: N26..29 ≤300 s GCB shortlist (max n29 253.7 s). N30..32 >300 s: proof fit ≤600 s only, not shortlist;
macOS/jobs3 margin OPEN (no factor). N32 is the scratch boundary 48 = 32+16 (abort_immediate not taken), still SUCCESS.
History (other trees/profiles, not matched): N29/N31/N32 TIMEOUT@120 s screen → 253.7/329.2/358.9 s here (all above that screen,
consistent); N26/N27/N28/N30 first records. Task forecast E 190–250 s held (n29 +3.7 s); F 250–300 s exceeded by 8–59 s.
B1 N9..32, tree d4ec476a, same profile (VT s / CBMC GiB; N16, N2..8 ordinary; ROUTESAB ≤17, ROUTESCD 18..25, here 26..32):

| N | VT | RSS | N | VT | RSS | N | VT | RSS | N | VT | RSS | N | VT | RSS | N | VT | RSS |
|---|---:|---:|---|---:|---:|---|---:|---:|---|---:|---:|---|---:|---:|---|---:|---:|
| 9 | 29.2 | 0.63 | 13 | 54.5 | 1.07 | 18 | 92.6 | 1.76 | 22 | 156.6 | 2.47 | 26 | 243.8 | 3.03 | 30 | 307.7 | 3.72 |
| 10 | 38.9 | 0.71 | 14 | 56.1 | 1.17 | 19 | 128.2 | 2.11 | 23 | 137.5 | 2.60 | 27 | 218.6 | 3.19 | 31 | 329.2 | 3.93 |
| 11 | 38.8 | 0.77 | 15 | 62.8 | 1.24 | 20 | 115.6 | 2.20 | 24 | 159.1 | 2.72 | 28 | 234.2 | 3.35 | 32 | 358.9 | 4.12 |
| 12 | 43.2 | 0.86 | 17 | 121.7 | 1.60 | 21 | 112.3 | 2.34 | 25 | 189.0 | 2.87 | 29 | 253.7 | 3.35 | | | |
B1 = 23/23 SUCCESS, 4/4 covers each, no TIMEOUT/OOM. v7: ≤300 s shortlist N9..15, N17..29 (20 roots); proof fit only N30..32
(3 roots, 307–359 s); none >600 s. Split (not run; no TIMEOUT, so none required): if v7 needs N30..32 under 300 s, split routes
0/1 (small_sort_general, own 48 stack scratch) vs 2 (Stable, caller scratch 48): new harnesses → new task; per-route VT unmeasured.
