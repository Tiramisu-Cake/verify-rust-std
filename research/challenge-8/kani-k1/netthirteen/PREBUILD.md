# NETTHIRTEEN PRE-BUILD REVIEW

Status: WAITING FOR COORDINATOR GO. No build dispatched; no proof result claimed.
Review SHA is the published research/request commit carrying this packet.
Task: TASK-NETTHIRTEEN.md, including mandatory «Уточнения»; one stage, one build, no retry.
Branch: experiment/kani-k1-netthirteen-20261102, based on N1 dfaba49ddc.
Pre-edit task head: b47dc20eba5ae095f44dc26ca1df81df3fbf8c2d.
Library commit: d60b2c975d18ef8f69234f0269c5cf89faa2fa24.
Library tree: a618a0bdce2816d5d50ce73b351fcdcba1a59d1e.

## Full diff and source contract

Full library diff: library.diff, network.rs only, 50 insertions, zero deletions.
Removing the new block restores the exact original network.rs bytes, including both N9 harnesses.
All other library files and runtime bodies/signatures are unchanged. No competing PR code opened.

Positive: network::netthirteen_full_value_count_u8_n13, full any [u8;13], pre=v,
independent any u8 probe. Actual F is the function-item type of strict_less::<u8>:
let mut cmp infers that type, with no fn-pointer coercion. No stubs or input assumptions.
Real UnstableSmallSortTypeImpl -> Freeze/Copy specialization -> small_sort_network:
u8 size1 <=8 and scratch fits; len13 <18 -> sort13_optimal -> insertion_sort_shift_left
with already complete prefix13 (tail equals end, zero insertions), return without merge.
Assertions: sortedness under default < and count(pre, probe) == count(v, probe).
Covers: sort moves elements, probe hits input, probe misses input, duplicates present.
Positive SUCCESS requires 4/4 covers; duplicate detection uses adjacent sorted output values.

Negative: network::netthirteen_full_value_count_u8_n13_negative, same real route and F.
Fixed input=[0;13], probe=0; after real sorting v[12]=1, sortedness remains true,
count(0) changes13 ->12. Sortedness is asserted AFTER corruption (network.rs:1053).
Two reachable covers: sort returned before corruption; count-check reached after sortedness.
Only accepted FAILED: literal kani::assert "netthirteen negative: full-value count preserved"
at network.rs:1055 (condition1056, literal1057), exactly matching request expect_check.
No positive covers copied into this witness. Unwind/sortedness/unsupported/setup failures
do not satisfy the negative control, even if a summary gate happens to accept its substring.

Both harnesses retain unwind25. Count loops have13 iterations; sortedness/duplicates12,
prefix comparison at most13; network has fixed swaps and its route loop returns after one pass.
Insertion suffix is empty. Bound25 is retained as required, with unwinding assertions enabled;
no trial build or bound adjustment. Compile/proof acceptance remains NOT_RUN until GO.

## Static gates

static_check.py / static-check.json: PASS; ordinary exact200 unchanged; cfg-on384 +2 =386.
Exact membership checked against ordinary baseline and controls baseline plus N9 and N13 names.
Source preservation checks all existing network bytes and limits library changes to network.rs.
Both new harnesses opt-in under kani_smallsort_controls. Counts are composition checks, not proofs.
pfc_order.py: ordinary pfc sites16 / bad0 (pfc-order.txt).
TASK-SPECFIX rustfmt wrapper --check and git diff --check: PASS.
Protected tools/workflows/toolchain/pin/checker paths unchanged (tooling-static.txt).
No local cargo/rustc/Kani/CBMC run; no Actions/CircleCI/macOS build.

## Exact G1 request and budget

RUN-REQUEST.json byte-equals g1.request.json; request netthirteen-g1-full-value-count-20261102.
SHA256 af58fb068502f9342ad5c8badfca7a030e7e88b4c11d3c5ed443d9c73f2b1a07.
Exactly two full exact names, under slice::sort::shared::smallsort::verify::network:::
netthirteen_full_value_count_u8_n13 (expect SUCCESS),
netthirteen_full_value_count_u8_n13_negative (expect FAILED, exact literal above).
Validator PASS; generated g1.args uses --exact and selects only these two rows.
measurement; controls:true; kani_jobs:1; uninit_checks:false; timeout10min per row.
gcb-e2-standard-4 / k1-standard4, 4CPU/16GiB; pin and nightly unchanged.
Full envelope (2*10+30)=50min; reserve50*$0.0135=$0.675; one build without repeat.
Own UUIDs none, spent $0, reserved $0 (runs.json). Global snapshot budget-prebuild.txt:
159 builds, used $76.7175, reserved $0; with proposed reserve $77.3925 <=cap $88.96.
Refresh budget immediately before dispatch after GO. No budget/history/cap changes.

## After coordinator GO

Dispatch this published reviewed SHA once; record request/source/library/UUID identities and cost.
Run tools/k1g.sh watch UUID with CODEX_THREAD_ID, then end turn as required by task.
After terminal: bounded summary/status/peaks, needed log-grep/log-lines and tooling identity check.
Record rows/status/VT/RSS/covers/failed checks and exact negative failure location/reason;
no unrelated failed checks accepted. Distinguish expectation, measurement gate, and task outcome.
TIMEOUT remains a resource-fit result with cap600s, available wall/RSS, VT UNKNOWN if absent.
Do not narrow input/probe, retry, run inherited controls, move to MACSPLIT/v6, or proceed to N18.
RESULT-NETTHIRTEEN.md <=30 lines must state actual function-item F and the prefix13/no-merge route;
opt-in and uninit-off limitations remain. SUCCESS says nothing about N18 or u64.
Task-specific K-1 reporting uses k1g bounded interfaces, not Select-Merge/Evidence Brief.
Publish final REVIEW REQUEST <sha> / NETTHIRTEEN ЗАВЕРШЁН and stop after this stage.
