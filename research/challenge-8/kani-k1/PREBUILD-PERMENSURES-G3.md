# PERMENSURES G3 — coordinator-authorized exact packet

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
