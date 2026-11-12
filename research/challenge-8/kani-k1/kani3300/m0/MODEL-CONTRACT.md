# KANI3300 M0 — immutable allocation contract (design, NOT_RUN)
1. Scope: Part1-B flat `[MaybeUninit<T>;N]` / `[MaybeUninit<T>]` remains required; retain both raw_eq checks.
2. Base: read-only `6134e42dd1c65dc980336e7d9455aba02d423edf`, production `dc5f5a406749a73f1c3192e0b5338441e79508bb`.
3. Inputs: R2 `124a45e373` answers 2–5,8,11–13; D0-A `ff5cabbfca`; C1-P `d8d3e6d4ca`; exact hashes in CONTROL-MAP.json.
4. D0 established RHS immutable Some×4 without init update; left normal-return setter executes and reads TRUE on .2 paths.
5. D0: 12 capped captures, four complete target fragments, eight unavailable; runtime OBJECT_SIZE UNKNOWN, .1 independent witness absent.
6. AllocId9/5 are observations, never model constants; singleton reproduces .2, not universal cache independence.

## Invariants (normative obligations for implementation)
I1 State: distinguish proved immutable allocation mask A, mutable tracked state S, and unknown coverage U logically; retain bool runtime witness.
I2 Coverage: each admitted byte read needs a source-bound immutable mask or a complete instrumented state history for its range.
I3 False: None maps to false; initial false stays false without a justified event; unknown origin/effects requires pre-effect Unsupported or blocks release.
I4 Identity: compiler-local allocation keys are not runtime object numbers; emitted object plus checked byte offset determines witness matching.
I5 Ranges: raw read/copy covers actual extent; typed transfer uses D(T), discards padding, never changes false data to true on the source-following path.
I6 Reset: seed each completed witness reset before any user read/write/transfer; never seed again on reference use, call return, overwrite or alias access.
I7 Aliasing: one emitted object has one compatible descriptor; masks cannot be OR-merged and mutable objects cannot enter the immutable registry.
I8 Paths: dynamic choices and helper propagation retain all origins, offsets and effects; an empty relevance set is not proof of initializedness.
I9 Protocol: preserve actual false argument/return transfers, normal/abnormal edges, private state and paired ABI boundaries.
I10 Evidence: per-harness retained operand/property binding and reached legal/negative controls; source shapes/design review earn no proof credit.
The existing witness can nondeterministically follow a source byte into a destination, or retain an optimistic destination branch.
Thus I2/I5 require a counterexample-preserving source-following history for every copied hole, not exact concrete state on every optimistic branch.
Do not add new optimistic branches; require both transfer alternatives and actual false snapshots in qualification controls.

## Identity, masks and relevance
Descriptor: `{unit/compiler identity, referent AllocId, byte_len, allocation mutability, freeze evidence, Some/None mask, relocations, emitted symbol, emitted layout}`.
Operand binding additionally records carrier ConstOperand, referent offset, requested extent (possibly runtime expression) and origin alternatives.
Decode pointer carriers from actual provenance + addend, not carrier bytes as pointee mask; a reference type never proves origin.
Carrier relocation requires target pointer width P, offset+P within carrier, initialized addend bytes, resolvable target and matching target layout/endianness.
Do not admit exposed-address, unresolved/function/vtable provenance as anonymous data; diagnose before effects or block release.
A[i] = is_some(actual referent.bytes[i]), captured before codegen_allocation_data/unwrap_or(0); byte value and D(T) are irrelevant to A.
M1 admits relocation-free, fixed byte extent anonymous/promoted referents with actual Mutability::Not, validated immutable emission and no UnsafeCell mutation capability.
Require source/compiler immutability evidence independently of backend const flags and its hardcoded has_interior_mutabity=false; missing evidence is U.
Pointer-containing carriers are supported; relocation-bearing referent masks are deferred: intervals [r,r+P) must be nonoverlapping/in-bounds,
with every represented pointer byte initialized and exact emitted size/offset preserved before future admission; never infer this from zero fill.
M1 source metadata must retain no-UnsafeCell/freeze qualification through casts/erased reference types; otherwise no immutable admission.
Use MemLoc::Anonymous(compiler-local key) plus a descriptor/origin side table; extend constant seeds and both points-to constant paths.
Whole-object graph edges conservatively select instrumentation; separate offset/extent expressions survive projections/calls/joins and are checked at runtime.
All alternatives must resolve to qualified immutable or fully tracked storage; unknown alternatives are not dropped. Both raw_eq operands seed relevance.
Mutable write/reset/copy destinations keep existing instrumentation even when an immutable source is also reachable; no type-only positive shortcut.
At alloc_map hit AND insertion bind the requested key to the returned symbol; compare full extent/mask/mutability/relocations/freeze qualification.
Incompatible descriptors for one symbol stop emission with diagnostic; do not repair by OR, intersection or trusting Allocation equality alone.
Equal descriptors may share a symbol with several AllocIds. Validate emitted struct field sizes/offsets (including implicit padding) against source bytes;
if no byte-exact address mapping exists, reject this admission. IDs/hashes alone do not establish that mapping.
For each read pointer p: object(p), base-relative offset d, n; enforce no overflow and 0<=d<=L, n<=L-d; subrange uses A[d..d+n].
Zero extent performs no mask indexing or pointer-object query solely for seeding/checking; preserve independent validity and call protocol rules.
Supported layouts: byte-exact fixed arrays/scalars and existing qualified typed masks, flat arrays/slice views with runtime length/bounds.
New compound/ordinary-union layout semantics are excluded; canonical MU ZST retains existing separate qualification requirements.

## Placement: two alternatives, one selected
A (selected): finalize a per-codegen-unit immutable descriptor registry after all item/contract codegen, before symbol-table export.
Patch every normal completion of InitializeMemoryInitializationStateModel: after its existing nondet object/offset, false value and buffer reset,
before returning to harness code, apply exact mask to matching witness. No new runtime bitmap or per-reference initialization event.
For each canonical nonempty symbol q, base=address(q), L=descriptor.byte_len: if tracked_object==object(base) and 0<=tracked_offset<L,
assign value=A[tracked_offset]; object base offset must be validated zero, otherwise translate by its proved base offset.
Use live emitted address -> pointer_object/offset, never compile-time AllocId as runtime identity; no change for unmatched/out-of-bounds witness.
Finalize registry before reset body emission is sealed, independent of item order; verify all reset sites in ordinary/PFC/transformed entry roots.
Static constant materialization precedes seeding; late/unbound symbols or user effects between reset and seed are release blockers.
Each reset creates a new analysis epoch; aliases and repeated harness entry seed only there. Singleton/shared AB/BA use the same compatible registry closure.
B (rejected): derive immutable state on each get/copy/snapshot query by runtime object lookup. It needs every state consumer covered;
a missed transfer consumer loses false propagation, and lookup/use interactions add work beyond the reproduced entry-state gap.
Idempotence of A: for fixed witness inside immutable q, F(F(S))=F(S) since both assignments use identical A[k]; elsewhere F is identity.
Distinct live immutable symbols have disjoint object identities; coalesced symbols require identical descriptors, so seed order commutes.
This argument applies only to the seed phase before transfers. Reapplying it after mutable updates/witness moves is forbidden.
Immutability must exclude legal writes/deinit/realloc throughout the epoch, including aliases/UnsafeCell; otherwise use tracked S, never seed A.

## Composition and finite eligibility table
| Path | Admission/state source | Diagnostic and required control |
|---|---|---|
| Immutable anon/promoted, relocation-free | A from actual referent; symbol/range bridge above | D0 + direct/helper legal and left/right None; mask bridge failure stops M1 |
| Named static | Existing static tracking; no automatic anonymous seed | Static init/alias legal/hole qualification; if alloc_map aliases a seed symbol require same immutable descriptor, else reject |
| Mutable anon/local/flat scratch | Existing fully instrumented S; never seed | write/reset/overwrite/copy/alias negatives; lost effect is blocker |
| Heap/foreign/realloc affecting tracked bytes | No new support | Reached pre-effect Unsupported or release blocker; no B4 integration |
| Relocated referent/unknown extent/origin | U until exact supported bridge exists | Early Unsupported before read/transfer; no silent skip; required flat paths cannot be excluded |
| By-value DST | Unsupported before Store/Load construction | retained DST control; pointer/slice-reference support is separate |
| Compound storage/ordinary union constants | No new G1/B3 layout semantics | Existing qualified paths only; retained constant guard before operand unwrap, otherwise blocker |
| Ordinary Item return | Existing normal edge D(T) only with proved callee typed initialization | D0 left setter preserved; padding negative and destination binding |
| Shadow Item return/argument | Existing paired false snapshot/transfer, not blanket D(T)/true | Item true/false plain/seeded; original indices/counts/return0 |
| Intercepted/shim/bodyless/unresolved calls | Pair only if actual lowered caller/callee/hooks qualify | Otherwise pre-effect Unsupported preserving entry loads/checks; B1I-A does not prove Shim coverage |
| Unwind/abort, private DFCC state | No normal setter/return0 consume; private witness updates only | reached abnormal-edge and legal/frame/clause controls; no ABI extension |
Raw copy preserves full extent including padding/false, typed transfers clear padding; snapshot precedes overlap/overwrite, never reseed destination.
M2 qualifies setters/false transfers and adds a setter only for a separately reached gap; M3 qualifies offsets/aliases/reset/reuse and composition.
B3/G1/B4/T1b/general cache redesign remain outside this fix. Every unsupported path needs an actual reachable guard, not this table alone.
Model/control outcomes NOT_RUN; M0 accepts a design contract only. Unbound init/mask/symbol bridge in implementation requires STOP, not optimistic handoff.
