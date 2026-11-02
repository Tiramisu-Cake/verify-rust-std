# WONEDIAG PRE-BUILD REVIEW

WAITING FOR COORDINATOR GO. No Build submitted; own UUIDs none, spent/reserved $0/$0.
The published packet commit is the review SHA. Task: `../TASK-WONEDIAG.md`, including Уточнения.
Branch `experiment/kani-k1-wonediag-20261102`; task base `82848e3bc9`, W1 `1c107cb12a`.
Library-only commit `af8b0db75a78f737772c8fe86ed7d5cdff109e11`, tree
`af3da15225005c0eba22ef42626c8562485c8e7e`.
Kani `9461e07af7ec929f050aa4192f29363c9be07779`, nightly-2026-10-12 unchanged.

## Complete change and invariant domain

`library.patch` is the full library diff: 55 appended lines in `verify/wrap/wone.rs` only.
All original bytes in that file remain an unchanged prefix. Every other library file is unchanged.
No target, requires/ensures/modifies clause, model, type, comparator, old harness or negative
control changes. Existing private Rust T/F/CMP are reused inside the existing opt-in module,
after targets; no visibility expansion, copied targets, stubs or callback substitution.

Three new PFCs call the existing W1 `*_len` contract targets. Each explicitly constructs
initialized backing5, active offset1, literal len3, with unrestricted A/B/C/probe/left/right.
There is no length choice, match or `with_backing!` in the additions. All use original unwind16.
The original contracts still require len<=3 and initialized writable aligned/nonnull regions;
this pilot checks only N3 in these fixtures, not every allowed backing, N0..3 or N16.
Ensures retain sorted keys `x>>1` and scalar-old full-byte count at an independent u8 probe.
Generated checks, pointer/memory checks and target write-set enforcement remain enabled.

| New PFC in wrap::wone | Unchanged target / T / canonical F | Scratch | Frame after return |
|---|---|---|---|
| unstable_byte_n3 | unstable_byte_len / u8 / byte_less | real network route | input_frame on both sentinels |
| freeze_noncopy_n3 | freeze_noncopy_len / private NonCopyU8 / noncopy_less | real general internal scratch48 | same input_frame |
| stable_byte_n3 | stable_byte_len / u8 / byte_less | separate uninitialized scratch48, entire mutable slice | same input_frame; scratch may change |

Stable u8 retains whole borrowed scratch in modifies; no scratch prefix borrow or initialization.
The len>=2 scratch requirement remains scratch.len()>=len+16; this fixture supplies all 48 slots.
Separate uncontracted `input_covers_n3` runs after frame/return, seven reachable goals per row:
return; descending three-key chain; ascending chain; all equal keys with A!=B; A==B==C;
probe==A; probe distinct from A/B/C. These reproduce W1 N3 predicates without N0/N1/N2 covers.
No input constraint is introduced by covers. SUCCESS requires intended checks and all seven covers.
Stable Cell and negative controls are not requested; their old evidence does not prove new PFCs.

## Static checks and full exact request

`check_static.py` / `static-check.json`: source forecast only, ordinary exact200 unchanged,
cfg-on exact391 = prior388 plus exactly the three new names. Target ordering and opt-in
inheritance checked separately. Old source prefix and other library files checked against base.
`pfc-order.txt`: `ordinary pfc sites 23 bad 0`. This script labels gated child PFCs ordinary;
it is not the ordinary200 count. `rustfmt-check.txt` and `git diff --check` PASS, lines<=100.
No local cargo/rustc/Kani/CBMC run; native compilation and proofs remain NOT_RUN.

`g1.request.json` equals active `RUN-REQUEST.json`; request ID `wonediag-g1-20261102`.
Request SHA256 `605ba88774653998448d96773cb31f8e88074df58c732840fc063f37d097c95a`.
Measurement / controls:true / kani_jobs:1 / uninit_checks:false / timeout10 / standard4.
Exactly three SUCCESS rows, with full exact names:

- `slice::sort::shared::smallsort::verify::wrap::wone::unstable_byte_n3`
- `slice::sort::shared::smallsort::verify::wrap::wone::freeze_noncopy_n3`
- `slice::sort::shared::smallsort::verify::wrap::wone::stable_byte_n3`

Validator PASS with max-total-minutes60; generated argv includes `--exact`. Controls cfg enables
availability, not execution of all controls. No old TIMEOUT/OOM or expected-failure row is selected.
One Build only: full reserve (3*10+30)*$0.0135=$0.8100. No automatic retry; no G2.
`budget-prebuild.txt`: global used $76.7175/reserved $0; projected $77.5275 <= cap $88.96.
Own builds0/1, spent/reserved $0/$0. Refresh global budget before dispatch after exact-packet GO.
Tooling/workflows/pin/flags/cap unchanged; library commit is separate from research/request commit.
Both commits use [skip ci], push without force.

## After coordinator GO only

Dispatch this published branch using tools/k1g.sh, record UUID and request/source/library identity,
then `k1g.sh watch UUID` with CODEX_THREAD_ID and end the turn. No model polling.
At terminal outcome use K-1 bounded status/summary/peaks and needed log-grep/log-lines; check-tooling
against `30f77e859903df14b442ff9294d4fbbd44827f20`. K-1 is outside Evidence Brief/Select-Merge.
Record VT=UNKNOWN when Kani omits Verification Time; TIMEOUT/OOM are resource outcomes.
RESULT-WONEDIAG.md <=35 lines: each row status/VT/RSS/covers/failed checks and W1 comparison
(unstable TIMEOUT 2101724 KiB, NonCopy TIMEOUT 15585836 KiB, Stable u8 OOM 15679436 KiB; VT UNKNOWN).
If N3 is cheaper, this supports a joint effect of union/match/backings, without separating them;
if still expensive, their influence is not excluded. Proof scope remains only these N3 fixtures.
Evaluate, without running, a single next comparison (contract N3 vs plain real-entry N3;
whole scratch write-set vs prefix3 while retaining allocation48/frame enforcement; or N2/N4+).
Publish final result with REVIEW REQUEST <sha> / WONEDIAG ЗАВЕРШЁН and stop this one stage.
