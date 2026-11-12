# M2-B/S3 witness and source binding

## Established from supplied trace

User reports run43252039413, CI4804129592, exact5f7 + M2-A C03. INPUTS hashes supplied files;
source/tool executable identities remain coordinator-reported. MIR/GOTO are the previous r2 files,
not asserted byte-identical outputs of this new run. No compiler or solver ran in this session.

Failed property is `<u8 as std::array::equality::SpecArrayEq<u8, 3>>::spec_eq.safety_check.1`.
This is LEFT CheckAs `_4`, not right `_11`, per transformed MIR 2072–2125 and GOTO7220/7228.
Names “inner Assert” here refer to the contract body copy, not to the first/second operand checks.
Text states8926/8931/8935 show actual invocation in `write_initialized::{closure#3}::{closure#0}`;
States8940–41 and8958–59 forward its operands through PartialEq to SpecArrayEq.
It is the BODY equality at C03:30, not ensures or harness/outer Original. MIR2885–3149 confirms.

LEFT pointer is `&value!0@1`, runtime CBMC object50, query base offset0, length3 and [true;3] mask.
RIGHT points to emitted `AllocId(1,ThreadLocalIndex).0`, runtime object20, base offset0, length3.
These runtime IDs are not rustc AllocId keys, MIR alloc labels or stable type intern indices.
The selected witness byte is **(object50, offset2)** (text States830/929), inside the query range.
Its final state-changing write is reset `MEM_INIT_STATE.value=FALSE`, State1009, text line3015–3017.
No subsequent assignment updates tracked_object_id/offset/value. JSON independently shows hidden static
initialization first, then reset indices826/922/999, and no later tracked value assignment.
At9039–40 object matches;9042–43/9076–77 establish range;9084 returns selected FALSE;9092 is the failure.
Value bytes are [1,2,3] at8926. A later set(FALSE),8775–78, targets source object49, offset0;
it does not update or retarget selected byte50:2. Argument-buffer state is separate from witness value.
TRACE-SELECTION.json contains bounded excerpts and original source coordinates; no full trace copied.

The immutable RHS seed already exists (r2 GOTO6940–6941). It cannot seed this mutable stack object50.
No missing-RHS-seed repair is justified. Selected witness retains reset false because the typed
normal return `_16=assume_init(move _17)` has no matching setter before its first raw_eq read.
MIR3057 returns directly to bb14 (3025–3032); `(*_22)=_16` (3042) likewise has no post-write setter.
The out write is AFTER this failing read and not reached by this counterexample. Absence of its
setter is statically confirmed, but no runtime out failure is claimed from this property-filtered run.
Outer Original has normal setter bb61, typed read bb63 and out setter bb66 (2692–2721).

## Narrow relevance correction

Source bootstrap.rs defines `kani_register_contract<T,F:FnOnce()->T>(F)->T` as unreachable;
FunctionWithContractPass replaces it with the MIR of `run_contract_fn<T,F:FnOnce()->T>(F)->T`,
which calls F (contracts.rs transform and library/kani_core/src/lib.rs:747).
The old points-to path follows raw instance.body() in apply_regular_call_effect, so it visits
panic instead of this actual closure call. It cannot discover the Assert copy's local alias edges
from the harness. Delayed InstrumentationVisitor selects normal-return SetRef only via those edges.
The observed missing `_16` setter is consistent with this concrete raw/emitted body mismatch.

The candidate passes a shared, per-pass override map into the existing recursive points-to analysis.
It selects only emitted registration trampolines and one-empty-block Unreachable closure bodies;
the latter preserve the contract pass's discarded closures and avoid resurrecting unused paths.
Original bodies remain the fallback. Caller/callee instance identities, argument/upvar/return-edge
construction and layout resolver stay unchanged. Restored relevance lets the EXISTING typed
normal-return/write instrumentation do its work; no new unconditional positive setter is added.

No change to memory/shadow model, initialization seed admission/placement, MU transfers, ABI/DFCC,
retargeting, runtime std, original tests, control oracles or assertion assumptions. No new trust premise.
Static bridge repair is prepared; compilation, actual restored setters and complete C03 success
are UNVERIFIED and must be established by coordinator CI. PFC resource gate remains separate.
