# Incoming span / actual MIR storage lifetime candidate

Design selected at 19:03 UTC, before implementation. Experimental, NOT_ACCEPTED.
Missing fact: for actual tmp/src and incoming tail/dst, positive sizeof(T) implies
src+sizeof(T)<=dst OR dst+sizeof(T)<=src. Consumer is the unchanged literal-one
CopyOnDrop fragment, before and after FBC. No separation premise is added.

A new local allocation event must be actual MIR StorageLive, not hoisted DeclStmt.
The exporter already retains and serializes StorageLive/StorageDead. Translator
currently discards both. Candidate lowers trusted internal lifecycle markers;
address-taken MIR declarations are deferred until StorageLive. StorageDead must
consume the existing full (or immutable half) local storage and remove its current
path-local address binding. Later StorageLive creates a fresh address; old saved
raw pointer numbers remain unconstrained. Block cleanup skips absent bindings.
Unsupported lifecycle/resource paths must fail closed. Drop remains elaborated MIR;
retirement does not invent a second Drop or erase resource obligations.

Incoming criterion: exposed initialized/uninitialized physical storage
present at function proof entry BEFORE heapifying parameters/declarations, whose
exact heap chunk remains present at the allocation event. A positive real fraction
certifies physical bytes, not initializedness/T.own. The entry list alone is not
a live witness: removed/reconstructed chunks are ineligible, including deallocation
and ordinary contract consume/produce. Direct reads preserve physical representation;
ManuallyDrop wrapping does not allocate the tail. Framed permissions forbid a
verified callback from deallocating those same bytes; no authority is inferred from
pointer parameter status, provenance, type or symbol inequality. A closed predicate
or reconstructed byte representation is conservatively unsupported by this rule.

This depends on enforcing actual StorageDead for caller stack storage in the same
candidate translation domain; merely narrowing the previous heap scan is inadequate.
Preconditions retain their usual conditional meaning: callers must provide genuine
physical storage. Safe caller slice provenance is not reconstructed from raw numbers,
and the standalone supplied caller premises remain an admission debt.

At StorageLive, only currently eligible incoming chunks are compared to the new
local; current-function locals never qualify as incoming. Conditional geometry uses
supported fixed scalar/pointer extents, with both sizes strictly positive.
Readonly overlapping aliases within one allocation are untouched. Subobject witnesses
cover only their own byte extent. Zero extent grants no address distinctness; concrete
T=() specialization is not qualified by abstract size-zero tests.

Conservation: geometry creates no bytes, fractions, values, initializedness, reference
init/end tokens, or T.own. StorageLive uses existing allocation resource production;
StorageDead requires existing storage cleanup. Actual shared src/guard packaging
must conserve values/fractions and sole CURRENT owner. Pure numeric facts can survive
FBC only if stored for its current fields; old held_ref equality is not assumed.

Trust changes: translator lifecycle lowering and kernel declaration/allocation/
retirement bookkeeping plus incoming geometry. Exporter, copy spec, prelude and
permission/lifetime/leak/unwind checks stay authoritative. Independent review and
Cloud controls are required; testing does not prove global model soundness.

Critical self-review gates: no early hoisted allocation; no retained permission
past StorageDead; no double-live or double cleanup; fresh repeated allocation;
entry authority cannot be resurrected by equivalent address/chunk reconstruction;
branch-local bindings must determine active epochs. If these cannot be preserved
within the bounded patch, candidate is no-go, not an axiom.

First Cloud gates, predeclared: live incoming/local positive; retired local must
fail on marked numeric inequality (not on mandatory equality); overlapping readonly
reads succeed and marked disjointness fails; resource-free raw pointer fails at
marked disjointness; consumed incoming authority grants no marked disjointness;
abstract zero extent fails at marked inequality. Frontend/setup failure is
INCONCLUSIVE. Then actual separation before FBC, current-field geometry after FBC,
and literal-one copy are fresh results, never inherited from the rejected profile.

## Critical review refinement before execution

Generic geometry is DISABLED. The existing Rust struct-size axiom can specialize
sizeof(T) to a positive modeled size for the actual ZST T=(). Abstract zero testing
would not repair that semantic mismatch. New candidate therefore excludes generic,
struct and array extents; it is a runtime-lifetime primitive and fixed-size rule,
not a complete solution for the unchanged generic actual consumer. Re-enabling T
requires an independently valid runtime extent/layout bridge; do not add an axiom.
Old broad candidates2f61/8c are not ancestors and their declaration-heap scan is absent.

## Final admission gate after static review

Tool75099c95 is NOT_FOR_INTEGRATION. Six Cloud mechanism controls match, including
verified actual MIR retirement, but ordinary CallExpr marker spelling is not an
unforgeable origin. The extern-prototype/diverging-call route described by the
independent reviewer is a code-derived potential soundness defect, NOT a tested
exploit. No new experiment or implementation was started after the main deadline.
An internal AST event with trusted MIR origin is required before integration.
Separately, generic/struct/array geometry is excluded until a sound runtime byte
extent bridge is available. The actual generic consumer therefore fails pre-FBC
span at line69; reusing an old candidate PASS or adding separation premises is
not permitted. See EVIDENCE-cae0f3cc.json for exact new-profile results.
