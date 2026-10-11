# Bounded one-cell caller composition, 2026-10-11

Status: first attempt **INCONCLUSIVE_PREPARATION**, first corrected adapter **INCONCLUSIVE_ANNOTATION**; actual-address correction **FRESH_PASS_FRAGMENT_ONLY** (`1ce46121`/`bc08afa0`). Build `c226905b-2b8c-49ef-b795-c6818874bef2` reached source/MIR/AST admission but refused unsupported local RawPtr in refinement and unsafe helper safety_proof without a prototype before either checked copy or caller call. These are not ownership negatives. This card records a
falsifiable experiment for the frozen `df6b3fbf` tool candidate and profile
`0b8cf55b`. A fresh hosted Build, its full raw logs, stage/source receipts,
positive and intended negative classifications are required before any proof
claim. The candidate remains experimental and is not accepted for integration.

## Actual consumer and bounded domain

The pinned std `insert_tail` body supplies adjacent `tail.read()` and the
`CopyOnDrop { src: &*tmp, dst: tail, len: 1 }` initializer at lines 550–551.
The pinned `CopyOnDrop::drop` body supplies the exact runtime expression
`ptr::copy_nonoverlapping(self.src, self.dst, self.len)`. The fixture specializes
the source to concrete `u64` and substitutes only `self.field` with
`(*guard).field` in a separate ordinary unsafe helper. Its caller uses the
actual read and initializer, takes a mutable borrow of the live guard, casts that reference to the helper raw pointer, and calls the helper.
The fixture does **not** contain an actual `Drop` implementation, natural
cleanup/glue, a comparator, or a generic `insert_tail` body.

The caller's inherited entry contract supplies valid initialized `tail`
storage and `<u64>.own(t, held)`, thread token, type interpretation, positive
`u64` size, alignment, object limits and no-overflow bounds. It does not
supply a guard allocation, guard size, source/destination separation, a
snapshot of CURRENT, or a helper summary. The read creates live `tmp` storage;
the constructor creates live guard storage and literal `len == 1`.
Source/destination identity and separation are derived from that constructor
and the compiler-qualified live allocations. The fixture depends on the
already reviewed concrete guard layout and allocation-span rules; no new
trusted rule or tool patch is proposed here.

## Resource path and target obligations

The caller creates the readonly held reference, closes nonempty
`<CopyOnDrop>.own` from the source quarter, destination gap and current
`u64` owner, then closes and opens one half of the generated full borrow
content. The other physical half preserves the field identities. The
established field-frame merge and two half-own opens restore the same field
chunks, padding, source quarter, destination singleton and type
interpretation. Typed storage lemmas and the actual constructor geometry
derive the strong helper's alignment, bounds, length and separation. The
singleton arrays are packaged from those chunks before the real call. The initialized guard fields and padding fold through existing `close_points_to(&gap_guard)` before the actual mutable borrow. Fresh419034 MIR/AST shows this expression lowers to AddressOf(gap_guard) and then AddressOf(Deref(reference)), with no create_ref_mut or token. Its physical aggregate is opened with `open_points_to(guard_ptr)` and the actual pointer equality is asserted rather than assumed. After the helper returns those same fields and padding, the caller checks their original allocation identity and retains the full physical frame for ordinary StorageDead cleanup. The erroneous token assertion/end_ref_mut from the prior adapter is preserved as an annotation refusal, not a resource negative.

The helper requires that complete strong precondition, executes its exact
dynamic-length copy, and uses an inline ghost statement after the runtime copy to close `CopyOnDrop_drop_effect` on the resulting
CURRENT source/destination payload. Its normal post returns thread token,
the original guard fields and padding, and that effect. The caller opens the
effect, checks the conserved held quarter, ends the readonly reference and
lifetime, and establishes the original full normal post
`thread_token(t) * type_interp::<u64>() * (*tail |-> held) *
<u64>.own(t, held)` with return and leak checks. The original caller unwind
post remains present, while this helper's contract permits no unwind. This
normal-only diagnostic does not prove panic cleanup or Drop glue.

The positive case must reach the helper copy, call, effect open, full normal
post, return and leak checks. A false assertion at the caller entry tests
that the derived strong resources are reached before the call. A second
false assertion after the call tests reachability of the returned CURRENT
effect. These negatives count only at their exact assertion sites after
source/MIR/AST admission and stage integrity; setup, unsupported operation or
unrelated failures are inconclusive. Source stripping must reproduce the
runtime adapter byte for byte. MIR and proof AST gates must bind the helper
copy and call to the exact source lines, nonempty own, generated borrow
content, and effect definition.

If all cases pass, the result is only bounded concrete-`u64` normal
composition. If source/MIR/AST preparation fails, repair that specific gate
and submit new exact inputs. If the first proof refusal is a resource or
value obligation, retain that location and repair only conserved annotation
steps; do not infer a trusted-semantics defect or add premises. A success
does not establish actual `Drop::drop` receiver origin, compiler drop glue,
panic unwind, generic/ZST types, whole `insert_tail`, or any other caller.
