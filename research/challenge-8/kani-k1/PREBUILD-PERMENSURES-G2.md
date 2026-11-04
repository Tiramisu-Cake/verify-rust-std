# PERMENSURES G2 — authorized exact packet

Coordinator GO after G1 report `00bff2533bab3dca2bea096e73495dd502afbfc8` authorizes dispatch
without another PRE-BUILD round if the request is exactly: backing24 PFC + N24 consumer,
and a smaller N9/N13 post-sort corruption control with its matching backing PFC, <=4 roots,
10-minute limit. Both owners were explicitly declared free; this packet selects k1-merge.
No additional G1 retry or N32 row is authorized or included.

Branch `experiment/kani-k1-permensures-20261105`;
library commit `7263edfaef952a79e1931c3373a8428d14ede868`.
Tooling base `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`;
Kani pin `cd355b0bccd32300713bc2ce4f765dafa1510607`.
Request `permensures-g2-20261105`, SHA-256
`f0ba910d99f318185aff5dc023c1dc954f7ad2a838af6301b1678155c401bc40`.
Kind diagnostic, standard4, controls true, jobs1, 10 min per harness, unwind40.
Existing organizer flags, no-assert-contracts, uninit/value-validity options remain unchanged.
Names below have prefix `slice::sort::shared::smallsort::verify::permensures::`.

| Root | Expected | Domain |
| --- | --- | --- |
| swap_permutation_u8_backing24 | SUCCESS | full u8 backing24, any in-bounds a/b including equal |
| unstable_network_permutation_u8_n24 | SUCCESS | fixed identity tags 0..23, verified swap, real insertion/merge |
| swap_permutation_u8_backing9 | SUCCESS | full u8 backing9, same arbitrary positions |
| rejects_network_corruption_u8_n9 | FAILED, `permensures network tag mask` | same network consumer on tags0..8, then v[0]=v[1] |

Both PFCs and the N24 consumer were already prepared before G1. The only library addition is
an eight-line N9 root calling exactly the existing `exercise_network::<9>(true)` with the
same verified swap/panic-stub/unwind attributes as the N17 negative. The runtime functions,
conditional u8/u64 model, all existing harness bodies and frame/ensures remain unchanged.
N9 is chosen over N13 to reduce the control's formula after N17 timed out. No runtime,
checker or mutation change is used to manufacture a different expected failure.

Every root uses the same function item `arbitrary_less(&u8,&u8)->bool`, volatile reads of
both operands and an independent arbitrary answer per call. PFC arrays are arbitrary full
u8 values; consumer identity tags are a subset. Matching backing24/N24 and backing9/N9
provide exact T/F/allocation-size matches, without transfer from other sizes. No claim for
u64 is established by these rows, and other T still have trivial ensures.
Only swap_if_less uses stub_verified. The actual Unstable trait entry, insertion, merge and
copies run; explicit order-violation panic is cut by cover/assume(false)/unreachable as in G1.
N24 evidence concerns normal return, not sortedness, panic unwinding or arbitrary payloads.
N9 has no merge; its declared order-panic cover is not expected on that source route.
The negative duplicates one output element after sort and must fail exactly the mask property;
an unrelated failed check or TIMEOUT does not validate it. Covers must be inspected separately.

Validation: existing request validator accepted exactly four rows; static checks confirmed
all requested roots, matches of T/F/backing, and the exact expected negative property.
Only the N9 root was added to the library. Contract/runtime source and existing safety-PFC
source match the completed G1 source; all protected lane paths match the tooling base.
git diff --check passes. No local cargo/rustc/Kani/CBMC, raw logs, credentials, competitor
code, workflow/tooling modifications or subagents are used.

G2 reserve: (4*10+30) min * $0.0135/min = $0.9450. Own G1 spent $0.5535;
combined spent plus G2 reserve $1.4985 < $3.00. Dispatcher refreshes project used/reserved
and enforces the $118.96 cap before submission. This is the second primary build; no further
primary build is authorized. At most one compile-error repair must stay within the task's
remaining cap and explicit authorization; no ordinary failure/timeout retry is included.

Publish separate library/research [skip ci] commits and push without force. Dispatch this
exact request under the existing coordinator GO, then k1g.sh watch BUILD and end the turn.
After completion use bounded summary/rows, check-tooling and necessary bounded diagnostics;
update RESULT-PERMENSURES.md in <=35 lines preserving all G1 outcomes and proof limits,
publish final REVIEW REQUEST / PERMENSURES ЗАВЕРШЁН and stop.
