# PERMENSURES G3 — coordinator-authorized exact packet

State: completed; backing28 PFC passed, N28 default and N32 kissat timed out. Details below.

After accepting G2 report `51000f2508c0566348df32fe6ade506368a95ba2`, the coordinator explicitly
authorized a third build and raised this stage's own cap from $3.00 to $4.00. This overrides
the original two-primary-build limit only for G3. Project cap stays $118.96. GO permits
exactly N32 consumer with kissat and backing28 PFC + N28 consumer with default solver,
<=3 rows, ten minutes per row, any free owner, self-dispatch after fixing the packet.

Branch `experiment/kani-k1-permensures-20261105`, owner k1-merge (released after own G2).
Library commit `329583ee0404068f804ceb9b514ce9841bffd25e`.
Tooling base `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`;
Kani pin `cd355b0bccd32300713bc2ce4f765dafa1510607`.
Request `permensures-g3-20261105`, SHA-256
`bd3f8db57ef3c46f8d826571d25f6bd4f69200db90729eb09915fa4dcba52601`.
Kind diagnostic, standard4, controls true, jobs1, ten-minute harness timeout, unwind40.
No global solver override or changes to existing verification flags are made.
Names have prefix `slice::sort::shared::smallsort::verify::permensures::`.

| Root | Expected | Domain / solver |
| --- | --- | --- |
| unstable_network_permutation_u8_n32_kissat | SUCCESS | identity tags0..31, backing32, same verified swap; explicit kissat |
| swap_permutation_u8_backing28 | SUCCESS | full u8 backing28, any in-bounds a/b including equal; default solver |
| unstable_network_permutation_u8_n28 | SUCCESS | identity tags0..27, backing28, same verified swap; default solver |

N32 uses a separate proof root with exactly the previous consumer's attributes and body,
plus `#[kani::solver(kissat)]`. The original default-solver N32 root remains untouched, so
G1's TIMEOUT and input identity stay historical. Its backing32 PFC already passed in G1
at source `d86897746f1b3d6c0bbfed3ca3c03e96a46dbe96` with full u8 values, arbitrary positions
and the same function item. G3 does not rerun or extrapolate that PFC to other backings.
The unchanged swap contract/model/comparator/harness helpers preserve its domain for N32.

Backing28 gets a separate proof_for_contract root and matching consumer through the existing
macros. Every root uses the same stateless arbitrary reading comparator, whole u8 values
and exact backing N; tag inputs are subsets of the corresponding full-value PFC domains.
Only swap_if_less is summarized. Real Unstable dispatch, insertion, merge and copies run.
The explicit order-violation panic is cut by the existing cover/assume(false)/unreachable.
Claims are normal-return fixed-tag permutation, not sortedness, panic unwinding or arbitrary
payloads. The optional u64 model has no evidence from these u8 rows; other T have trivial
ensures. Both consumer routes use merge; all positive covers must be inspected independently
of SUCCESS. The validated N9 negative remains G2 evidence and is not resubmitted.

Static validation: the existing request validator accepted exactly these three rows.
The only library changes are backing28 PFC invocation, N28 consumer invocation, and the
new N32 kissat root. Removing those additions restores the G2 harness file byte for byte.
All existing root bodies, runtime functions and safety-PFC source are unchanged. Protected
lane paths match the tooling base. git diff --check passes. No local cargo/rustc/Kani/CBMC,
credentials, raw logs, competitor code, tooling/workflow changes or subagents are used.
Packet validation does not establish compilation or proof success.

G3 reserve: (3*10+30) min * $0.0135/min = $0.8100. Actual G1/G2 spent $0.7965, reserve zero;
combined spent plus G3 reserve $1.6065 < newly authorized own cap $4.00. Dispatcher refreshes
project accounting and enforces $118.96 before submission. No fourth primary build is
authorized by this GO; no ordinary timeout retry is included.

Publish separate library/research [skip ci] commits, push without force, dispatch this exact
request under the existing GO, then k1g.sh watch BUILD and end the turn. On completion use
bounded summary/rows, source/tooling binding and needed bounded diagnostics; preserve all
G1/G2 outcomes and limits in the final report. RESULT-PERMENSURES.md stays <=35 lines, with
historical detail in the prebuild packets. Publish REVIEW REQUEST / PERMENSURES ЗАВЕРШЁН,
then stop without further dispatch.


## Observed G3 outcome and final handoff

The exact three-row request was published without force at
`049d7f8464dbcb95c9a0b3db15ec1e65c61254e0`, owner k1-merge, request SHA-256
`bd3f8db57ef3c46f8d826571d25f6bd4f69200db90729eb09915fa4dcba52601`.
Dispatch created `5fb82a5e-fa7c-403a-bd85-84a97a4005b0`; its watch was registered and the turn
ended. Before dispatch, bounded budget showed 233 builds, $99.3435 used, $0 reserved;
maximum after G3 submission was $100.1535 of the $118.96 project cap, including $0.8100
reserve. No competing code, credentials or raw logs were accessed.

The completion notification reported Cloud FAILURE. Bounded summary is COMPLETE, Kani exit1,
gate false and expectations false. This is not a compile error: backing28 PFC completed
successfully and both consumers reached bounded verification timeouts. The three-row page
binds exact build/source/request identities, total=3, offset=0, next_offset=done.
check-tooling passed the standard4 pool, all protected lane paths, source/build binding
and all six bound tooling hashes against `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`.

| Root | Status | Time s | Failed/total | Unreachable | Covers |
| --- | --- | --- | --- | --- | --- |
| unstable_network_permutation_u8_n32_kissat | TIMEOUT | not reported | not reported | not reported | not reported |
| swap_permutation_u8_backing28 | SUCCESS | 34.31302 | 0/289 | 4 | 7/7 |
| unstable_network_permutation_u8_n28 | TIMEOUT | not reported | not reported | not reported | not reported |

Bounded k1g log-grep locates N32 kissat at kani.log:2710, VERIFICATION FAILED at2715 and
timeout at2716. N28 begins at2718, reports VERIFICATION FAILED at2723 and timeout at2724.
Both exact timeout diagnostics are:
`CBMC timed out. You may want to rerun your proof with a larger timeout or use stubbing to reduce the size of the code the verifier reasons about.`
Neither timeout reports completed verification time, failed-check inventory or covers.
Configured limit is 600 s per root, not a measured successful-proof time. A timeout does
not establish a failed permutation assertion or an impossibility result.
Backing28 PFC begins at2726, satisfies all seven covers at2731 and is SUCCESSFUL at2734.
All its covers (both comparator outcomes, equal/increasing/decreasing positions, exchange
of distinct values and normal return) are satisfied; four unreachable checks are separate
from successful proof credit.

The N32 root explicitly selects kissat in source and otherwise calls the identical
`exercise_network::<32>(false)` with the same verified swap/panic stub/unwind40 attributes.
The bounded process summary reports kissat processes attributed to that exact N32 root,
peak RSS0.29 GiB, alongside its CBMC peak1.97 GiB. This supports actual solver execution;
it does not isolate a cause for the timeout. The original default-solver N32 root remains
unchanged and its G1 TIMEOUT remains historical. N28 and its PFC use the unchanged macros
with no solver override. No library or request changes follow the completed G3 run.

New bounded credit is the swap's full u8/backing28 contract with arbitrary positions and
same stateless reading function item. Matching backing28 PFC passes, but N28 consumer
times out; no consumer composition credit follows from the PFC alone. G1's backing32 PFC
still matches N32's T/F/backing, but neither default nor kissat N32 consumer completed
within its configured ten-minute limit. Solver choice does not change that logical domain.

Across all three builds, established full-u8 swap PFC domains are backings9,17,18,24,28,32.
Successful fixed identity-tag consumers remain N17,N18,N24, and the post-sort single-element
corruption checker is validated at N9 by the G2 expected mask failure. The historical N17
negative remains TIMEOUT. Backing4/13 roots are unrun, existing safety PFCs were preserved
rather than rerun. u64 has a conditional model but no proof credit here; other T have
trivial ensures. No universal T/F, sortedness, arbitrary-payload consumer, panic-unwinding
or disabled uninit/value-validity guarantee is inferred. The explicit order-violation
panic remains the only manual cut; claims concern normal returns.

N17 400.42688 s versus task-reported PERMTAGS335 s still gives no observed speedup and is
not an independently reproduced or controlled causal comparison. N24 succeeds at498.13196 s;
N28 default and N32 default/kissat remain unresolved at600 s. This experiment did not reach
N32 by composition under these limits; impossibility is not inferred from timeouts.

Whole G3 verify run including compilation: 21:44.11, max RSS2383104 KiB. Per-CBMC peak2.27 GiB
is attributed to N28; sampled largest sum RSS2.28 GiB. OOM scan none_seen is not proof of
memory headroom. Combined bounded `k1g.sh budget G1 G2 G3` reports `3 1.1880 0.0000`:
G3 cost $0.3915 plus previous $0.7965, total $1.1880, reserve zero, below the newly authorized
$4.00 own cap. Three authorized primary builds are consumed; no compile error, repair,
unchanged-input retry or fourth build occurred. No further dispatch is authorized.

The final RESULT-PERMENSURES.md preserves all fourteen G1/G2/G3 row outcomes and exact
ensures in <=35 lines, with expanded identities/evidence/limits in the phase packets.
Only that result and this packet change at closeout. Publish [skip ci], non-force push,
REVIEW REQUEST / PERMENSURES ЗАВЕРШЁН, then stop.
