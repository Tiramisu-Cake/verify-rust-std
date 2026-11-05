# PERMENSURES G2 — authorized exact packet

State: completed; all four expectations met. Observed outcome follows the historical packet.

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


## Observed G2 outcome and final handoff

The authorized exact four-row request was published without force at
`872c963fec2a18a8d217d7eb322dd1595ec9099e` and dispatched on k1-merge as
`4662b386-b6a8-471b-a1c8-833d26262f36`. k1g.sh watch was registered and the turn ended.
Dispatch maximum: $100.0455 of $118.96, comprising $99.1005 used and $0.9450 reserved.
The completion notification is Cloud SUCCESS. Bounded summary is COMPLETE, gate true and
expectations true; Kani exit1 is consistent with the one expected failing negative control.
The four-row page binds exact request/hash/source/build, total=4, offset=0, next_offset=done.
check-tooling passed the standard4 pool, source/build identities, all protected lane paths
and all six bound SHA-256 values against the full tooling base.

| Root | Status | Time s | Failed/total | Unreachable | Covers |
| --- | --- | --- | --- | --- | --- |
| swap_permutation_u8_backing24 | SUCCESS | 34.7287 | 0/289 | 4 | 7/7 |
| unstable_network_permutation_u8_n24 | SUCCESS | 498.13196 | 0/463 | 14 | 5/5 |
| swap_permutation_u8_backing9 | SUCCESS | 31.553417 | 0/289 | 4 | 7/7 |
| rejects_network_corruption_u8_n9 | FAILED (expected) | 25.809164 | 1/463 | 18 | 1/5 (4 unreachable) |

The negative's only failed check is exactly `permensures network tag mask`, reported at
`/workspace/src/library/core/src/slice/sort/shared/smallsort/verify/permensures.rs:92`.
Bounded log-grep locates its harness at kani.log:2710, cover summary at2717, exact failed
property at2719 and VERIFICATION FAILED at2722. N24 starts at2725, with 5/5 covers at2732
and SUCCESSFUL at2735. PFC backing24 starts at2738 with 7/7 covers at2743; backing9 starts
at2749 with 7/7 covers at2754. These bounded evidence coordinates support the exact expected
mask failure and all positive cover aggregates; no individual negative cover labels are
reported by the terse output. Its 1/5 covers do not invalidate the observed mask counterexample
or imply positive-coverage completion. Unreachable checks remain distinct from proof credit.

All G2 expectations are met. The full u8/backing24 arbitrary-position PFC supports the N24
consumer with exactly the same stateless arbitrary reading function item. N24 uses fixed
identity tags 0..23 and executes the real Unstable entry, insertion, merge and copies with
only swap_if_less summarized. Its normal-return permutation and both comparator outcomes
are nonvacuous by all five covers. Panic paths are cut only at the explicit order-violation
boundary, with no sortedness or unwinding proof. The backing9 PFC supports the same summary
used in the smaller corruption control. Duplicating one post-sort element now yields the
required mask counterexample in 25.809164 s. No checker or mutation semantics were changed.

Across G1/G2, established u8 swap domains are backings9,17,18,24,32. Positive tag consumers
are established at N17,N18,N24. The optional u64 model remains unproved by this packet;
other T have trivial ensures. Backing4/13 roots remain prepared but unrun. Existing safety
roots were preserved, not rerun. N32's matching PFC succeeds but its consumer remains the
G1 TIMEOUT, and the historical N17 negative remains TIMEOUT. The new N9 control validates
the checker at that matched domain; it does not turn either historical timeout into a pass.
N32 composition feasibility remains unresolved under the ten-minute limit. No universal
T/F, arbitrary-payload consumer, sortedness, panic-unwinding or disabled uninit/value-validity
claim is inferred. G1 N17 400.42688 s still exceeds the task-reported 335 s PERMTAGS reference;
this is not an independently reproduced, controlled causal performance comparison.

G2 whole verify run including compilation: 11:08.43, max RSS3573140 KiB; per-CBMC peak1.53 GiB
attributed to N24. OOM scan none_seen does not prove headroom. Combined bounded
`k1g.sh budget G1 G2` reports `2 0.7965 0.0000`: G2 $0.2430 plus G1 $0.5535, total $0.7965,
reserve zero, below own $3.00 cap. Both primary builds are now consumed; no compile error,
repair, unchanged retry or third build occurred. No further dispatch is authorized.

RESULT-PERMENSURES.md contains all eleven G1/G2 rows and the exact ensures in <=35 lines.
Only that result and this historical packet are changed at closeout; no library/tooling change.
Publish [skip ci], non-force push, REVIEW REQUEST / PERMENSURES ЗАВЕРШЁН, then stop.
