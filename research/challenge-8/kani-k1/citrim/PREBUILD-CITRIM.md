# CITRIM — exact G1 pre-build packet

PRE_BUILD_REVIEW_PENDING. No CITRIM build dispatched; no runtime/proof result claimed.
Task: TASK-CITRIM.md at b0f0f90d1f; one stage, G1/G2 only, no retry.
Worktree `/root/verify-rust-std-kani-citrim`, branch `experiment/kani-k1-citrim-20261105`.
Owner k1-merge; stage citrim-g1; ledger citrim-budget-20261105.
Library base `4fa6151b6a`; library commit `d866f287bb844b788ea853d0bb2fe829ddbf7292`.
Tooling base `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`; all lane files unchanged.
Kani pin `cd355b0bccd32300713bc2ce4f765dafa1510607`; nightly 2026-10-22.

## Exact domain replacements

Short names below are relative to verify::. Complete names/selector sets: check-report.json.
All value domains, probes, comparator functions, profile requirements, assertions and stubs
are retained. No runtime, contract definition, control or other ordinary body changes.

| Original | Replacement suffixes | Domain equality |
| --- | --- | --- |
| merge::general_direct_u64_n9 | _lt_lt, _lt_ge, _ge_lt, _ge_ge | full [u64;9] × probe = disjoint four truth pairs |
| merge::stable_direct_u64_n9 | _lt_lt, _lt_ge, _ge_lt, _ge_ge | same four truth pairs, same scratch48 |
| network::dispatch_safety_stable_unstable_bytes16_n15_16_17 | _n15, _n16, _n17 | {15,16,17} × {stable,unstable} |
| network::dispatch_safety_stable_unstable_bytes16_n32 | stable_bytes16_n32, unstable_bytes16_n32 | N32 × {stable,unstable} |
| network::dispatch_safety_stable_unstable_bytes17_n15_16_17 | _n15, _n16, _n17 | {15,16,17} × {stable,unstable} |
| network::insert_tail_contract_u64_start1_tail2_to8 | tail2_to5, tail6_to8 | [2,8] = [2,5] ∪ [6,8] |
| network::insert_tail_contract_u64_start1_tail9_to12 | tail9_to10, tail11_to12 | [9,12] = [9,10] ∪ [11,12] |
| network::insert_tail_contract_u64_start1_tail13_to14 | tail13, tail14 | {13,14} = {13} ∪ {14} |
| network::network_safety_unstable_u64_n30_to32 | _n30, _n31, _n32 | {30,31,32} = {30} ∪ {31} ∪ {32} |

Merge truth pair is `(v[0] < v[1], v[2] < v[3])`, before sorting. Every pair of bools
is included once; >= includes equality. Probe remains independent and fully arbitrary.
The new helpers are token-identical to the old helpers after removing the two partition
assumptions and renaming generic parameters. Original helpers serving N6..8 remain unchanged.
All eight merge parts use `#[kani::solver(cadical)]`: solver selection changes the SAT backend,
not the program or specification. Existing source already uses this solver at the same pin.
Unwind bounds are unchanged (34 merge, 65 dispatch, 25 insertion, 35 network).

Length/tail parts instantiate exactly the original macros, including each selected length/tail
cover. Shared completion/movement/panic covers are duplicated, never removed. For bytes16 N32,
the selected route's original cover label is retained in its part, and the other route's cover
lives in the complementary part. Stable/unstable entry points, comparator and panic stub match.
New parts require **64/64 covers**, zero unreachable covers (expected-covers.json).
Other unreachable non-cover checks must not be misreported as unreachable covers.

## Static validation

`python3 -B research/challenge-8/kani-k1/citrim/check_citrim.py`: PASS_SOURCE_ONLY.
TRIMPART lexer/macro expander reused without modification. The checker enumerates selectors,
checks exact disjoint unions, compares new expanded roots against original macro expansions,
checks the merge helper projection, and requires old shared items/macros to survive verbatim.
210 retained ordinary roots and all 34 opt-in roots are token-identical; other module files
are byte-identical. Runtime and all tooling are unchanged; only merge.rs/network.rs differ.
Ordinary **235 = 219 - 9 + 25**; cfg-on **269 = 235 + 34**. Exact lists are saved alongside.
Source inventory is not compiler inventory; G2 must request and compare all 235 ordinary names.
Rustfmt check (existing edition/style 2024 wrapper), diff check and request validation: PASS.
No local cargo/rustc/Kani/CBMC; no subagents; no competing PR/branch/diff inspection.

## G1 and budget

Request `citrim-g1-20261105-01`: diagnostic, standard4, jobs=1, controls=false,
inventory=false, all 25 new SUCCESS parts, 5 minutes each. Request SHA256 is in check-report.json
and RUN-LEDGER.json; exact harnesses are RUN-REQUEST.json and new-ordinary.txt.
SHA256: `879ae1c1994099eb19ca2c9d63c7e911efd6b13d781ae020acd0e8f9eb2d2b00`.
Maximum harness budget 125 min + 30 min overhead = **155 min**, reserve **$2.0925**.
Own cap **$3.00**; project cap **$118.96**; G1/G2 at most, no retries, one compile-error repair
per build only when own spent + new reserve <= cap. No repair is pre-authorized for dispatch.
G2 requires separate exact-packet review/GO after G1 analysis and inventory=true; its reserve
must fit remaining own/project budgets and the task window. No G2 request is dispatched now.
Budget snapshot: 240 builds, used $102.1920, reserved $0; with G1 maximum $104.2845.
The 300+30 minute window/deadlines and live budget observation are recorded in RUN-LEDGER.json.
Recheck project used/reserved, own spent/reserve, owner slot and remaining time before dispatch.

Actions baselines are source-reported in TASK-CITRIM.md: Ubuntu sum 1804.5 s, macOS sum 2126.0 s
for the nine original roots (per-root values retained in RESULT-CITRIM.md draft).
New times and before/after totals are unmeasured. No paired GCB timing for these exact old roots
is present in the inherited CITRIM/VEIGHTINTEG/CODEFIX reports. No measured scaling factor is claimed;
120 s GCB would be ~240 s at the task's conservative 2× heuristic, so it is not an Actions guarantee.

## After coordinator GO

Confirm exact approved pushed SHA and free k1-merge slot; use only this worktree's k1g.sh.
Dispatch once, record UUID/source/request/cost/window in the ledger, then `k1g.sh watch BUILD`
and immediately end the turn. Do not poll status in a loop. On wake, read bounded summary/rows,
check-tooling BUILD 59893bff1fbb2af1a0c08862afd7e3bb87c19cdd, covers and warnings via log-grep,
peaks and budget. Require every part SUCCESS, <=120 s and all expected covers reachable.
If needed, prepare G2 refinements and final inventory packet for separate coordinator GO.
Final RESULT-CITRIM.md <=45 lines must distinguish measured GCB times from supplied Actions
baselines and unchanged-root time, give every union and exact inventory delta, and state failures.
Stop on an uncovered decision with `Координатор, вопрос: ...`.
