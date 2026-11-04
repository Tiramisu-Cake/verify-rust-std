# ENSURES G1 — exact PRE-BUILD packet

PREPARED, NOT DISPATCHED. Await coordinator exact-packet review/GO.
Task: [TASK-ENSURES.md](TASK-ENSURES.md), issued at `37d8dacb60634e770dc634512bb951a323c0124d`.
Worktree `/root/verify-rust-std-kani-ensures`; branch `experiment/kani-k1-ensures-20261105`.
Library commit `bc216ac8ac14ddc344b3feff088329b66314d89d`.
Tooling base `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`;
Kani pin `cd355b0bccd32300713bc2ce4f765dafa1510607`.
Request `ensures-g1-20261105`, SHA-256 `44acf34a023016972263cff248e4465f72fed07d4d094b6c28ae5f4fd2db5139`.
Selected stable owner `k1-network`; it must be free at actual dispatch. Preparation does not
reserve an owner. Coordinator GO must confirm availability of the selected owner; if it is
occupied, wait for release or obtain an owner-only packet update/GO before dispatch.
No competing code, branches, diffs or evidence were opened.

## Model and exact contract

All additions are gated by cfg(kani), including the core `fn_traits` feature. Existing
`min_specialization` and `unboxed_closures` suffice for the remaining syntax. The mechanism is
an attempted blanket default implementation of `InsertTailComparatorModel<T>` for every F,
specialized only for the concrete pair `(u64, InsertTailU64Less)`. Compilation/feasibility has
not been established locally. The default says no model, sorted=true, count=0 without reads;
its two ensures therefore impose no order/count promise on arbitrary callbacks. No runtime
function body or signature changes. Existing safety requires and modifies stay unchanged.

`InsertTailU64Less` manually implements FnOnce/FnMut with strict full-u64 `<`. Its immutable
probe field is `kani::any::<u64>()`, fixed before the PFC call or whole consumer composition;
the comparator ignores it. Model order reads whole u64 values; model count counts exact
full-value equality to that probe. No generated nondeterminism occurs inside a specification,
no function pointer address check or mutable global model state is used. Fully qualified
`<F as InsertTailComparatorModel<T>>` calls bind the model to F, avoiding reference blanket
selection and making the type parameter explicit. Old expressions capture only bool/usize.

The exact two new attributes on the real insert_tail are:

```rust
#[cfg_attr(kani, crate::kani::ensures(|_|
    !old(<F as InsertTailComparatorModel<T>>::has_model(is_less))
        || !old(unsafe {
            <F as InsertTailComparatorModel<T>>::model_sorted(
                is_less, begin, insert_tail_contract_len(begin, tail).saturating_sub(1),
            )
        })
        || unsafe {
            <F as InsertTailComparatorModel<T>>::model_sorted(
                is_less, begin, insert_tail_contract_len(begin, tail),
            )
        }
))]
#[cfg_attr(kani, crate::kani::ensures(|_|
    !old(<F as InsertTailComparatorModel<T>>::has_model(is_less))
        || old(unsafe {
            <F as InsertTailComparatorModel<T>>::model_count(
                is_less, begin, insert_tail_contract_len(begin, tail),
            )
        }) == unsafe {
            <F as InsertTailComparatorModel<T>>::model_count(
                is_less, begin, insert_tail_contract_len(begin, tail),
            )
        }
))]
```

Order is conditional on the canonical type and pre-state sorted prefix. The full-value probe
count is preserved even when that prefix is unsorted. The PFC has no sortedness assumption,
so both branches of the order implication are exercised. The existing modifies region covers
only begin..=tail, so a verified stub must preserve the later backing suffix and comparator
probe. The model routines require readable initialized spans supplied by the safety requires.
Length subtraction is saturating so it introduces no arithmetic panic on an invalid geometry.
This does not make raw reads valid outside the existing safety preconditions.

The proof/stub/history design follows the
[Kani contract documentation](https://model-checking.github.io/kani/crates/doc/kani/contracts/index.html).
The pinned compiler remains the authority for this experimental specialization and macro use.

## Four-row request

Diagnostic, controls=true, jobs=1, standard4 (4 vCPU / 16 GB), ten minutes per harness;
organizer flags, --no-assert-contracts and uninit/value-validity settings unchanged.
All row names are under `slice::sort::shared::smallsort::verify::realcontracts::`.
All three new roots use unwind16, as does the existing safety PFC.

| Row | Expectation | Concrete domain and purpose |
| --- | --- | --- |
| insert_tail_ensures_u64_tail1_to4_backing5 | SUCCESS | PFC of actual insert_tail; full arbitrary u64 backing5; arbitrary tail1..4; InsertTailU64Less with arbitrary probe; no sorted-prefix assumption |
| insertion_ensures_u64_n5_stubbed | SUCCESS | real insertion_sort_shift_left from offset1; stub_verified(insert_tail); all five elements sorted and full-value probe count preserved |
| rejects_insertion_ensures_u64_n5_corruption | FAILED: `ensures consumer n5 sortedness` | identical real entry and stub, then v[0]=u64::MAX and v[1]=0 force an inversion |
| insert_tail_safety_u64_tail1_to4_backing5 | SUCCESS | unchanged historical safety PFC; arbitrary_less::<u64> uses the no-model default; prefix need not be sorted |

The canonical PFC also directly asserts model selection, conditional output order, the full
probe count and unchanged suffix via scalar comparisons. It requests covers for all four
tails, sorted/unsorted premises, movement/early return, a present probe and normal return.
The positive consumer requests normal return, a present probe, nonconstant output and reaching
all assertions. Covers must be inspected separately; a SUCCESS label is insufficient to infer
reachability. The negative request binds its named sortedness check; unrelated failures cannot
satisfy the expected control. Its mutation may also fail the count check, which is not the
acceptance target. No panic stub or extra comparator assumptions are added.

## Composition domain and limits

The consumer executes the unchanged real insertion loop on one u64 backing5, offset1. Its
four actual helper calls have tails1/2/3/4, exactly the canonical PFC's T/F/backing/tail domain.
A singleton initial prefix is sorted; the conditional summary extends it at each actual call.
The same immutable arbitrary full-value probe is used at all four calls, and count preservation
composes with the suffix frame. Independent harness-side sorted/count checkers assess the
whole output rather than invoking the comparator model to assert its own summary.

This is bounded full-value-probe evidence, not a universally quantified multiset axiom attached
to every individual havoc outcome, nor an independent universal generic proof. No credit is
claimed until PFC, consumer and intended negative pass their expectations with reachability.
N8/N16 require a larger matching PFC backing and tail range; they are not in this packet.
This G1 tests whether real-helper summaries can support the insertion component toward the
16/32 thresholds; it establishes neither threshold, stable blanket dispatch nor ordered merge.
Other types/comparators, panic unwinding, Drop/ZST, uninit/value-validity and universal callback
effects remain outside the claim. No tooling, workflow, trusted-rule or ordinary-suite expansion.

## Validation, budget and handoff

The unchanged Python validator accepts exactly the four roots and emits exact matching harness
arguments, ten-minute timeouts, jobs1 and the controls cfg. git diff --check passes. Removing
only the new cfg(kani) model/attributes from smallsort.rs and feature from lib.rs restores both
files byte-for-byte to the task commit, preserving every runtime body/signature and old safety
attribute. All protected lane/tooling paths match the full tooling base. Static source checks
confirm all four requested roots and the precise matched composition domains. No local
cargo/rustc/Kani/CBMC, credentials, raw logs or competing work were accessed.

2026-11-04T21:51Z bounded k1g budget snapshot: 228 builds; used $96.8460, unfinished reserved
$1.0800. G1 worst-case reserve `(4*10+30)*$0.0135=$0.9450`; project maximum with this packet
$98.8710 < $118.96. Own spend is $0, own cap $3.50. Dispatcher must refresh accounting at
submission; any repair/G2 must remain within task build/repair limits and own/project caps.
G2 requires a new GO. No dispatch is authorized by preparing, committing or pushing this packet.

Publish library and research commits separately, both [skip ci], push without force, then
`PRE-BUILD REVIEW <full HEAD SHA>` and stop. After exact-packet coordinator GO and owner release,
use only k1g.sh to dispatch the published branch, immediately register `k1g.sh watch BUILD`,
then end the turn. On its notification, read bounded summary/tooling evidence, write
RESULT-ENSURES.md in <=35 lines with exact ensures, rows, matched domains and limits;
publish [skip ci] reporting and `REVIEW REQUEST <sha>` / `ENSURES ЗАВЕРШЁН`, then stop.
