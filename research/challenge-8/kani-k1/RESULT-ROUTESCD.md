# RESULT ROUTESCD — existing opt-in general all-routes safety roots N18..25 (GCB, jobs1): PASS 8/8

Reviewed PRE-BUILD 60358cf50d7d (coordinator GO; G2 pre-approved in that GO). Branch experiment/kani-k1-routescd-20261103, owner
k1-network; base f02ba6c48b6a, task 98bbf31775e6. library tree d4ec476a7a00 = Part1 v6; merge.rs blob 12937938 (no library commit).
Kani 9461e07af7ec / nightly-2026-10-12; check-tooling vs frozen 30f77e859903 for both: pool ok, lane files equal, 6 bound files ok.
Profile gcb-e2-standard-4 → k1-standard4, 4 CPU/15.6 GiB, swap off, controls on, jobs 1, uninit off, 10 min/row, unwind 34.
G1 routescd-g1-measure-allroutes-n18to21-20261103 (e75c0506…55e2bc) → build 38eb81fa-89b8-49f7-b58b-d7745ba9c5fc @60358cf5;
  T0 dispatch 10:50:27Z, start 10:51:07Z, finish 11:06:24Z, Cloud SUCCESS, gate True, Kani exit 0. Receipt routescd/g1.result.md.
G2 routescd-g2-measure-allroutes-n22to25-20261103 (f52055e8…868c) → build b1a8ae94-6b0c-4a4c-b1d1-5239ccd7a2cf @c0c0acdf;
  dispatch 11:09:14Z, start 11:10:03Z, finish 11:29:20Z, Cloud SUCCESS, gate True, Kani exit 0.

| Root (verify::merge::) | Pkt | Status | VT s | failed/total | unreach. | covers | CBMC row RSS |
|---|---|---|---:|---|---:|---|---:|
| route_safety_all_routes_n18 | G1 | SUCCESS | 92.6 | 0/613 | 9 | 4/4 | 1.76 GiB |
| route_safety_all_routes_n19 | G1 | SUCCESS | 128.2 | 0/613 | 9 | 4/4 | 2.11 GiB |
| route_safety_all_routes_n20 | G1 | SUCCESS | 115.6 | 0/613 | 9 | 4/4 | 2.20 GiB |
| route_safety_all_routes_n21 | G1 | SUCCESS | 112.3 | 0/613 | 9 | 4/4 | 2.34 GiB |
| route_safety_all_routes_n22 | G2 | SUCCESS | 156.6 | 0/613 | 9 | 4/4 | 2.47 GiB |
| route_safety_all_routes_n23 | G2 | SUCCESS | 137.5 | 0/613 | 9 | 4/4 | 2.60 GiB |
| route_safety_all_routes_n24 | G2 | SUCCESS | 159.1 | 0/613 | 9 | 4/4 | 2.72 GiB |
| route_safety_all_routes_n25 | G2 | SUCCESS | 189.0 | 0/613 | 9 | 4/4 | 2.87 GiB |

Row RSS: VmHWM of the single CBMC PID attributed `active=T0:<root>` (summary peaks; jobs 1). Unreachable counts are Kani data.
Packet peaks (per Build): G1 time -v max 2457796 KiB (2.34 GiB, cbmc), kani-compiler 2.03, driver 1.20 GiB, process-sum 2.96 GiB,
wall 8:48; G2 time -v max 3005356 KiB (2.87 GiB, cbmc), kani-compiler 2.03, driver 1.41 GiB, process-sum 3.61 GiB, wall 12:17; OOM none_seen.
Covers 4/4 = PRE-BUILD forecast: normal return of each of the three routes (direct general u64, non-Copy Unstable general, Stable
u64 scratch 48) + abort_on_order_violation stub cover; the stub cover is not counted as a route return.
Gate: 8/8 accepted (identities/profile, SUCCESS, 0 unintended failures, all covers). No counterexample. Overall ROUTESCD PASS.
Cost: own spent $0.4860 (G1 $0.2160 + G2 $0.2700) of cap $1.95, own reserved $0. Window: T0 10:50:27Z, G2 terminal 11:29Z.
Project after (11:31Z): 191 builds, used $84.5745, reserved by unfinished $0.9450 (one foreign build, COVERCOST k1-merge), cap $88.96.

Meaning/limits: bounded normal-return safety of any `[u64;N]` on the three routes, arbitrary volatile-reading comparator, panic cut by
cover+assume(false), unwind 34; not correctness/all T/unwind cleanup, uninit off. Measurement only; ordinary 202/v7 unchanged; no PR/CI.
Candidate-for-v7: all eight ≤300 s GCB shortlist (max n25 189.0 s); ≤600 s proof fit; macOS/jobs3 margin OPEN (no factor).
History (other trees/profiles, not matched): N18 TIMEOUT@120 s screen → 92.6 s here; N23 TIMEOUT@120 s → 137.5 s (above that
screen); N21 180 → 112.3 s; N19/N20/N22/N24/N25 first records. N17 (ROUTESAB) 121.7 s → N18 92.6 s: no step at N18.
E/F advice (not run): same sort8_stable shape for all N≥16; VT is noisy but trends ~+14 s/N (92.6→189.0 over N18..25, N19>N20/21 and
N22>N23), CBMC RSS +0.16 GiB/N. Linear extrapolation: E[26..29] ~190–250 s, F[30..32] ~250–300 s, RSS ≤ ~4 GiB, well inside
10 min/row and 16 GiB. Run E (4 rows, reserve $0.945) and F (3 rows, $0.810) as is; no TIMEOUT here → no route split upfront.
If an E/F row TIMEOUTs: split routes 0/1 (small_sort_general own scratch) vs 2 (caller scratch) — needs new harnesses (new task).
