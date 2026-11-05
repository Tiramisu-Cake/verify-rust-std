# TAILDIAG G1 — exact packet for coordinator review

Branch `experiment/kani-k1-taildiag-20261105`, stable owner `k1-network`.
Task `7a68931f595b173c69624cecb88436c449912c91`, integrated base `4fa6151b6a`.
Library-only commit `c8eec9f537b2845fc2032b3458c8eeacfd9eb9b1` adds the opt-in module
and its cfg-gated declaration. Runtime, prior verify sources, workflow and lane tooling unchanged.
Tooling base `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`.
Kani pin `cd355b0bccd32300713bc2ce4f765dafa1510607`, nightly `2026-10-22`.
No compiler, cargo, rustc, Kani or CBMC ran locally; no build is dispatched.

## Exact experiment

All rows are `proof_for_contract(insert_tail)`, real body, start 0, arbitrary initialized
array contents, unwind 32, no sorted-prefix assumptions and no functional stubs.
The arbitrary comparator reads both arguments volatile and returns a fresh symbolic bool,
as in v8b. The deterministic comparator makes identical volatile reads, then compares the
whole u64 values with `<`. This is a strict value order without the profile's probe, shifted
key, sortedness requires or ensures. Only the answer policy changes between these two rows.
Baseline is u64/backing17/tail1..7/arbitrary comparator/default solver/explicit suffix frame.
Backing rows use the same tail1..7 range so allocation size and tail domain are not confounded.
The two upper-tail rows vary only the interval relative to their corresponding lower rows.
All new root names below have prefix `slice::sort::shared::smallsort::verify::taildiag::`.

| Root | Factor vs baseline | Allocation | Tail inclusive | F | Solver | Explicit suffix frame |
| --- | --- | --- | --- | --- | --- | --- |
| u64_backing8_tail1_to7 | backing | u64[8] | 1..7 | arbitrary_less::<u64> | default | yes |
| u64_backing12_tail1_to7 | backing | u64[12] | 1..7 | arbitrary_less::<u64> | default | yes |
| u64_backing17_tail1_to7 | baseline | u64[17] | 1..7 | arbitrary_less::<u64> | default | yes |
| u64_backing17_tail1_to7_value_order | comparator | u64[17] | 1..7 | value_less_u64 | default | yes |
| u64_backing17_tail1_to7_cadical | solver | u64[17] | 1..7 | arbitrary_less::<u64> | cadical | yes |
| u64_backing17_tail1_to7_kissat | solver | u64[17] | 1..7 | arbitrary_less::<u64> | kissat | yes |
| u8_backing17_tail1_to7 | element type | u8[17] | 1..7 | arbitrary_less::<u8> | default | yes |
| u64_backing17_tail1_to7_no_explicit_frame | frame | u64[17] | 1..7 | arbitrary_less::<u64> | default | no |
| u64_backing17_tail8_to15 | upper interval | u64[17] | 8..15 | arbitrary_less::<u64> | default | yes |
| u64_backing17_tail8_to15_value_order | upper interval + comparator | u64[17] | 8..15 | value_less_u64 | default | yes |

No-frame removes only the explicit post-call frame assertion; the real modifies contract remains.
Each root has five required reachable covers: comparator true/false, lowest/highest tail on
return, normal return. Deterministic rows also retain both comparison covers. Expected total
50/50, with no unreachable covers for a passing row; timeout rows have unknown cover results.
A green runner alone is insufficient. The frame loop covers the entire suffix after tail.

Solver attribute reference: [official Kani documentation](https://model-checking.github.io/kani/reference/attributes.html#kanisolversolver).
It lists cadical and kissat and warns that the default depends on version. Explicit cadical
may be a repeat of the default, not a distinct algorithm; do not assume solver causality
without bounded invocation evidence for the pinned version. No other source/PR was consulted.

## Validation and budget

`python3 -B research/challenge-8/kani-k1/taildiag/check_taildiag.py`: PASS.
It reuses the existing source lexer/expander, checks unchanged prior roots/sources/runtime,
whole-module opt-in gating, exact request names, and unchanged lane paths against tooling base.
Static ordinary inventory stays 219; cfg-on 253 -> 263, 34 old opt-in plus 10 new roots.
Exact lists and expected covers are adjacent. This is source validation, not compiler inventory.
Rustfmt --check (existing 2024 config/wrapper), 100-column check and git diff --check: PASS.
Existing request validator: ten exact SUCCESS rows accepted, controls=true, inventory=false,
diagnostic standard4, jobs=1, 4 minutes per root. Gate failure is expected if any row times out.
Request `taildiag-g1-20261105-01`, SHA256
`ccc22fb30ac75edd682dee2aca2b175fcdc977c23c017a85802d8f0ff3037296`.
40 harness-minutes + 30 setup/closeout overhead = 70-minute build timeout; reserve **$0.9450**.
Own cap **$2.00**, project cap **$118.96**. Snapshot: 240 builds, used **$102.1920**,
reserved **$0**, with G1 max **$103.1370**. Recheck at dispatch; preparation starts no build window.
Two equally sized worst-case builds reserve $1.89 total; repairs require actual remaining cap.
At most G1/G2, no retries, at most one compile-error repair per build within own spent+reserve.
Main window 240 minutes + closeout 30; start/deadlines recorded at authorized G1 dispatch.

## After coordinator GO

1. Confirm exact pushed SHA, slot owner and budget; record window/deadlines in the local ledger.
2. Dispatch once via k1g.sh, record build identity; run `k1g.sh watch BUILD` and end the turn.
3. On wakeup use bounded summary/rows/peaks/log-grep, check-tooling and budget only.
   Bind build/source/request/pool/Kani identities and the ten exact requested row names.
   Full std lane inventory is disabled per coordinator: its roughly 49-minute cost risks the
   70-minute build timeout. The 263-name cfg-on list remains source-only validation.
   Record per-row checks, covers, verification seconds and attributed CBMC/solver RSS peaks.
   Missing verification seconds on timeout do not equal the 240-second watchdog budget.
4. Separate SUCCESS from <=200-second candidates; treat factor explanations as hypotheses
   unless controlled pairs establish the effect. No extrapolation of bounded domains.
5. G2 requires coordinator GO after G1 analysis. Choose the cheapest measured combination;
   partition domains <=200 seconds. Only a successful union covering tail1..15 permits
   an insertion consumer <=16, with identical T, function-item F, allocation and start.
   Backing17 PFCs cannot justify a backing16 consumer; use an initialized backing17 allocation
   and a slice of len<=16 if that is the selected matched domain. Callback covers cut by a
   verified stub must not be treated as reachable consumer covers.
6. Write RESULT-TAILDIAG.md <=40 lines, commit/push research [skip ci], then
   REVIEW REQUEST <sha> / TAILDIAG ЗАВЕРШЁН. Do not claim completion before evidence exists.
