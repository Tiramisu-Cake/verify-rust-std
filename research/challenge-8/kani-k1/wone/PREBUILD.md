# WONE PRE-BUILD REVIEW

WAITING FOR COORDINATOR GO. No Build dispatched. The published packet commit is the review SHA.
Task: `../TASK-WONE.md`, branch `experiment/kani-k1-wone-20261102`.
Base task commit `4ffdf6e267` (source baseline `e382287728`, library v5 `cbe69760c8`).
Library commit `e4f1df6a348fe67277250f84e5a6aa83638a7892`, tree
`1731596d7c6df1e7fc745fa9e8d6a9ae4df7a432`.
Kani pin `9461e07af7ec929f050aa4192f29363c9be07779`, nightly-2026-10-12 unchanged.

## Full patch and contract domain

`library.patch` contains the complete library diff (325 added lines, two files).
`verify/wrap.rs` only appends gated `mod wone;`; old N2 functions, PFCs and controls are byte-identical.
`verify/wrap/wone.rs` is an opt-in child under `kani_smallsort_controls`, using the private parent
types/model/comparators without changing visibility. Runtime smallsort.rs and all other library
files, tooling, workflows, flags, cap and pin are unchanged.

Four raw wrappers have `(v: *mut T, len: usize, [scratch], cmp: fn(&T,&T)->bool, probe: u8)`:
`stable_cell_len`, `unstable_byte_len`, `freeze_noncopy_len`, `stable_byte_len`.
Each requires `len <= 3`, nonnull/aligned initialized writable `v[..len]`, canonical comparator;
each body guards canonical identity and forwards that actual pointer to the real trait entry.
Full-byte Model; order is `x >> 1`; probe is independent/unrestricted by value. Generalized sorted
and full-value count inspect all len elements, with scalar pre-count in `old`, no callback in specs.
Only Stable u8 permits scratch writes: its modifies includes the entire passed mutable scratch
slice plus v[..len]. Cell scratch is excluded from modifies. Scratch allocations are separate
from input; this is a conservative requires, not a check of every nonoverlapping same allocation.
Stable u8 requires `len < 2 || scratch.len() >= len + 16`: N2/N3 need 18/19 or the real body aborts;
N0/N1 return before the size check. No domain is claimed for short scratch at N2/N3.

## Exact PFC fixtures and controls

Each of four PFC harnesses chooses len 0..3 and uses `with_backing!` match: initialized arrays
of exactly N+2 elements, active offset 1/len N, unrestricted A/B/C/probe and both sentinels.
This is not an exact N allocation, and does not establish all requires-allowed backings/offsets.

| PFC (wrap::wone::) | T / actual route | Scratch fixture | Explicit frame |
|---|---|---|---|
| stable_cell_n0_to3 | Cell<u8>, Stable fallback | backing2, borrowed len 0..2; slot0 initialized, slot1 uninit | input sentinels + initialized scratch slot0 |
| unstable_byte_n0_to3 | u8, Unstable network/insertion | internal network scratch | input sentinels |
| freeze_noncopy_n0_to3 | private Freeze !Copy !Drop NonCopyU8, general | internal scratch48 | input sentinels |
| stable_byte_n0_to3 | u8, Stable Freeze/general | separate uninit scratch48, full borrowed slice | input sentinels only; scratch may change |

F is a concrete fn pointer, not generic FnMut; canonical values are cell_less/byte_less/noncopy_less.
No stubs or comparator replacement. All targets precede their PFCs. All use unwind16.
Uncontracted post-match input_covers has 16 reachable goals per row: returns N0/1/2/3;
N2 and N3 reversed/increasing/tied-distinct/duplicate; independent probe hit and misses at N1/2/3.
N3 reverse/increasing covers constrain the full three-key chain; ties cover all three keys.
Cell adds two scratch-length covers. Expected positive covers: 18/16/16/16.
N0 order/count are vacuous; its input frame/no-op is checked. N1 order is trivial but preserving
the singleton through count is substantive. These results cannot establish N0..16/32 or stability.

Two plain negative controls use the new Stable u8 N3 wrapper and scratch48:
`rejects_always_true`: only `wone canonical comparator required` (wone.rs:58) should fail;
`rejects_payload_corruption`: after sorted/count real-body assertions, flip `v[0] ^= 1`, confirm
key order, then only `wone full-value checker rejects payload corruption` (wone.rs:321) should fail.
Both have one reachable cover. Unrelated failures, timeout or compile error do not pass a control.

## Static checks (not native compilation/proof)

`python3 -B research/challenge-8/kani-k1/wone/check_static.py`:
PASS 20 checks; exact ordinary 200 unchanged against integwrapfix/ordinary-expected.txt;
cfg-on exact 388 = cleanup382 plus exactly six WONE names. Gate inheritance is checked separately.
No historical inventory/report is rewritten. `static-check.json` binds source/request hashes.
`python3 -B research/challenge-8/kani-k1/integwrapfix/pfc_order.py
library/core/src/slice/sort/shared/smallsort`: `ordinary pfc sites 20 bad 0`, saved in pfc-order.txt. Four of those
sites are gated child PFCs that this script mislabels ordinary; ordinary200 is the separate check.
TASK-SPECFIX rustfmt-wrapper --check passes for both changed Rust files; width <=100;
git diff --check passes. No local cargo/rustc/Kani/CBMC, Actions or CircleCI run.

## Request, budget and continuation

RUN-REQUEST.json exactly equals `g1.request.json`: `wone-g1-20261102`, measurement,
controls true, jobs1, uninit false, timeout10, standard4. Six exact names, four SUCCESS and
two FAILED with distinct literal expect_check. Validator passes with max-total-minutes150.
Request SHA256 `e0e7ac117a4bb93f65750202f5a7a155cede41c7c6f56cd98b58de82e1ec4a51`.
Own builds 0/2, spent/reserved $0/$0; G1 reserve (6*10+30)*0.0135 = $1.215 <= $1.5 task cap.
Project snapshot: used $74.8140, reserved $0, projected including G1 $76.0290 <= cap $88.96.
Refresh budget before dispatch. G2 only on compile error, with separate review/GO and
fact_spent plus a new complete reserve <=$1.5; no promise that a retry will fit.

After GO for the published review SHA: dispatch this branch via tools/k1g.sh, record own UUID,
register `k1g.sh watch UUID` with CODEX_THREAD_ID and end the turn. No model polling.
At completion use bounded K-1 summary/status/peaks/log-grep/log-lines only as needed; bind source,
library/request hashes, pin/flags, requested target names, covers and exact failed check locations.
Check tooling vs `30f77e859903df14b442ff9294d4fbbd44827f20`, cost own UUIDs only.
Evidence Brief and Select-Merge procedures do not apply to this K-1 task.
Then RESULT-WONE.md <=40 lines including rows/status/VT/RSS/covers/failures, domain limits,
readiness and cost estimate for N4..N8; publish `[skip ci]` without force and stop this stage.
