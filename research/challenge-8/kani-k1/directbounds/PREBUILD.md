# DIRECTBOUNDS PRE-BUILD REVIEW

Status: WAITING FOR COORDINATOR GO. No DIRECTBOUNDS Build submitted; compile/proof/covers NOT_RUN.
Review SHA is the published research/request commit carrying this packet. Runtime: Claude Code, one stage.
Task: TASK-DIRECTBOUNDS.md @928288d6b4. Branch experiment/kani-k1-directbounds-20261103.
Base f23d7f2354cff734880cd1b930e6ee8e56289815 = NETCOMP2 58d464ce1c (library tree 3b6d2a51dae0…) + cap e8e238db9d.
Library commit 3b856adf15267507dd5648ca8b7e3000d5c5d776; library tree 17dedd1eb7d64863b091c1a12d04385dadeef9ca.
Request directbounds-n10-n13-direct-u8-20261103, SHA256 02a91ccbedf23ce10228dc3cfbecbf8713d43cc0eb8e44863e30c0f5c6185009.
Full zero-context source diff: library.diff. No competitor code/branches/diffs read.

## Source scope

New opt-in child network::netcomp::directbounds, file verify/network/netcomp/directbounds.rs (blob bea01f03b9).
netcomp.rs: only `#[cfg(kani_smallsort_controls)] mod directbounds;` appended at EOF (all existing lines and
line numbers unchanged; A9/positive9/run9/helpers/runtime untouched). Child uses netcomp's private U8Cmp and
canonical and network's StrictU8/count_matching_values/is_sorted_by/prefix_unchanged through ordinary
descendant visibility; no `pub`, no visibility widened. Inherited `#![allow(dead_code)]` from network.rs.

positive9 is not reusable generically: it is fixed to [u8; 9]/run9 and carries composed-only branches;
a const-generic version would change A9 bytes. So direct_u8_n10/n13 are copies. static_check.py asserts
byte-equality of each to A9 positive9 under exactly these substitutions (a9_byte_diff in static-check.json):
- `fn positive9(composed: bool)` -> `#[kani::proof] #[kani::unwind(25)] fn direct_u8_nN()` (root inlined);
- `[u8; 9]` -> `[u8; N]`, `while i < 9` -> `while i < N`, literal prefix `netcomp N9:` -> `directbounds NN:`;
- `run9(&mut v, probe, &mut cmp, composed)` -> `runN(&mut v, &mut cmp)`.
runN = run9 with composed = false minus its composed-only locals: same actual call
`<u8 as UnstableSmallSortTypeImpl>::small_sort(v, cmp)`, then `kani::assert(canonical(*cmp), …unchanged)`.
Removed from run9: `base` and `initial_count = count_matching_values(v, &probe)` whose only uses are in
`if composed` branches (dead under A9's false); kept would be unused-variable warnings. probe arg dropped
for the same reason. This is the only semantic-neutral body difference to A9; VT comparison to A9 treats it so.

## Domain and actual route (same T/F/CMP/probe/solver as A9)

| | A9 netcomp_direct_u8_n9 (reference) | direct_u8_n10 | direct_u8_n13 |
|---|---|---|---|
| T / input | u8, full any [u8;9] | u8, full any [u8;10] | u8, full any [u8;13] |
| F category | fn pointer U8Cmp = fn(&u8,&u8)->bool | same | same |
| CMP value | `let mut cmp: U8Cmp = StrictU8::CMP` (reified strict_less::<u8>) | same | same |
| probe | independent any u8 | same | same |
| oracle | sortedness + full count(pre,probe)==count(v,probe) | same | same |
| entry | Unstable trait -> Freeze/Copy impl -> small_sort_network | same | same |
| route | len9<18 no merge; sort9_optimal (25 swap_if_less); insertion offset9=len: 0 inserts | sort9_optimal on v[0..9] (25); insertion_sort_shift_left(region,9): exactly one insert_tail(v[9]), <=9 cmps | sort13_optimal (45); insertion offset13=len: 0 inserts |
| stubs/summaries/adapters/solver attr | none / default solver | none / default | none / default |

Runtime anchors (smallsort.rs, unchanged): small_sort_network 311..353 (no_merge len<18, region=len,
>=13 sort13 / >=9 sort9), sort9_optimal 420, sort13_optimal 469, insert_tail 536, insertion_sort_shift_left 574.
N10 is the only one of the three that executes insert_tail; unwind(25) covers its <=9-step loop and all
10/13-step oracle loops (unwinding assertions on, as in A9).

## Rows, annotations, covers and literals

Prefix slice::sort::shared::smallsort::verify::network::netcomp::directbounds::; every root has exactly
`#[kani::proof]` + `#[kani::unwind(25)]` (static-check annotations), no other kani attribute in the file.

| Row | Expected | Covers (all required) |
|---|---|---|
| direct_u8_n10 | SUCCESS | sort moves elements; probe hits input; probe misses input; duplicates present (4/4) |
| direct_u8_n13 | SUCCESS | same four, N13 literals (4/4) |
| count_negative_u8_n10 | FAILED, only `directbounds negative: count n10` (:92) | sort returned before corruption; corrupted count check reached (2/2) |
| count_negative_u8_n13 | FAILED, only `directbounds negative: count n13` (:115) | same two, N13 literals (2/2) |

Positive covers are A9's four post-call covers, renamed. Controls: [0u8;N], probe0, real sort via runN
(canonical-cmp assert passes); then must-pass asserts `sorted before corruption`, `count before corruption`;
cover returned-before-corruption; v[N-1]=1 keeps order ([0..0,1]) -> must-pass `sorted after corruption`;
cover check-reached BEFORE the last assert; last assert fails: count(0) N -> N-1.
Each expect_check literal occurs once and is not a substring of any other literal (static-checked).
Any other FAILED check (sortedness, canonical, unwind, bounds, UB, unsupported), ERROR, OOM is not intended.
TIMEOUT on a positive is a resource outcome: no credit, no retry.

## Static delta and hashes

static_check.py PASS (static-check.json): library delta = exactly netcomp.rs (+appended registration) and new
directbounds.rs; ordinary exact 200 = integwrapfix/ordinary-expected.txt; cfg-on 395 (base, cfg-on-base.json from
f23d7f2354) -> 399 = +4 exact directbounds names; pfc_order.py: ordinary pfc sites 18 / bad 0 (unchanged).
Note: TASK says "ordinary 202 / PFC 36"; the base f23d7f2354 measures ordinary 200 and pfc_order 18 with the
recorded tools (also NETCOMP2 RESULT: 200 / PFC18). I report measured base values; both are unchanged here.
Rustfmt via assigned wrapper --check (2024, assigned fmtcfg) on directbounds.rs + netcomp.rs and
git diff --check: PASS (rustfmt-check.txt). Warnings: no compile run locally; statically every import, local
and helper is used and the module is cfg-gated (ordinary build unaffected). Compile confirmation is in Build.
Tooling: lane paths byte-equal to tooling base e8e238db9d87323fa4da011a1a8b37fb76ec91c0 (tooling-static.txt,
diff 0 bytes); post-build `k1g.sh check-tooling BUILD e8e238db9d…` will be recorded.
Hashes: directbounds.rs sha256 14c63e0bff7682d5c935c3f1e518b72821bc766de4c844418e2823bfc6d7845a;
netcomp.rs sha256 343244024809dc833249c8d651dc5fe69c6b16ebc2c1fb77e01c82018040162d; request as above;
g1.request.json byte-equals RUN-REQUEST.json; kani_k1.py validate accepted 4 rows (g1.args, g1.runner).

## Packet G1, budget and slots

measurement, gcb-e2-standard-4 (k1-standard4 4CPU/16GiB), controls:true, kani_jobs:1, uninit_checks:false,
harness_timeout_minutes:10, default solver, unwind25 with unwinding assertions; expect SUCCESS, SUCCESS,
FAILED(literal), FAILED(literal). Pin Kani 9461e07af7 / nightly-2026-10-12 unchanged (lane bytes equal).
One Build, no retry. Reserve (4*10+30)*$0.0135 = $0.945 <= own cap $1.00. One compile-error repair only if
own spent + $0.945 <= $1.00 (i.e. first Build compile-failed cheaply) and project <= cap.
Snapshot 12:46Z (budget-prebuild.txt): 195 builds, used $86.2350, unfinished $0 -> with reserve $87.1800 <= $93.96.
ROUTESEF (same owner) terminal/accounted (own reserved $0). Unfinished 0: <=2 project / <=1 k1-network holds.
runs.json: spent 0, reserved 0, no UUID. Refresh budget/slots and published SHA after GO, before dispatch.

## RESULT obligations

RESULT-DIRECTBOUNDS.md <=30 lines: table N9 (A9 from RESULT-NETCOMP2, reference only) / N10 / N13 with status,
VT, failed/total checks, covers, CBMC RSS, network route; controls' literal-only failures; one-line limitations
boundary on the single comparator U8Cmp and default solver; no interpolation to N11/N12, no N18/T/F transfer.
