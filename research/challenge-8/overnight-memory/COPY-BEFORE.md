# M1: initialized representation into uninitialized scratch

Problem: stock VF26.10 `std::ptr::copy_nonoverlapping<T>` requires initialized
typed destination cells. Actual sort4 writes four representations to caller
scratch, normally MaybeUninit. It neither transfers nor creates `T.own`.
This operation must not be confused with a cloning theorem for arbitrary T.

First experiment is diagnostic only, with no changed specification: call the
same `ptr::copy_nonoverlapping(src,dst,1)` as the actual four call sites in an
isolated generic unsafe probe. Compare initialized and uninitialized destination
storage. Full normal target preserves source value, writes the same destination
representation and preserves thread/frame; unwind target is false. Neither pre
nor post obtains new `T.own` from bytes. A false-result post control must fail at
the probe post after the operation, not at setup or the primitive precondition.

Prospective model: source initialized representation plus writable optional
destination representation and explicit aligned/live/nonoverlapping ranges
yield unchanged source and initialized destination representation. `T.own`
stays in the caller frame; source and destination cannot both be dropped using
one such owner. Preserve optional padding bytes and complete embedded pointer
provenance. Initial source/byte correspondence uses existing stock
`to_u8s_`/`from_u8s_` lemmas; compiler untyped copy correspondence is trusted.
Actual std wrapper and compiler intrinsic source/MIR must be certified before
actual-call use; this diagnostic using a stock summary is not that proof.

Trust review: kernel/prelude and memory/alias model remain unchanged. No added
axiom in the first diagnostic. A future primitive changes only an explicitly
named spec/frontend component, after inspecting the pinned wrapper's UB checks
and complete MIR. Destination ownership disposition must be explicit; `none`
is the sufficient scratch domain, not every overwritten initialized owner.
No Copy/Freeze/comparator-purity premise. Generic nonzero-size storage is the
first useful domain; distinct logical ZST occurrences remain an open gate.

Outcome mapping: initialized control passes and uninitialized fails at dst
array precondition => justify precise optional-storage extension. Earlier
frontend/setup failure => fix evidence, no semantic acceptance. Unexpected
owner creation => reject candidate. Later actual use still requires all four
copies, caller geometry and permutation/SWO bridges.

## O9 outcome and corrected next decision

O9 run37707055478/proof0781cdbd falsifies the initial premise: initialized AND
`dst[..1] |-?-> cons(none,nil)` destination probes both pass full VF (return,
leak,no deadcode), NORMAL/readonly/decode/refinement0. Original uninitialized
classification remains INCONCLUSIVE because the initial classifier allowed
only initialized positive; full log explicitly0errors. Kernel stock
`verifast1.ml:6925` maps RHS DummyPat `_` to `array_` and optional values;
`assertions.ml:1650` does the analogous points_to_ selection. No kernel/spec
repair is warranted. Falsepost and owner_creation fail at target post line6.
The target claim remains raw representation copy under stock summary, no
actual wrapper body proof and no ZST conclusion. Next meaningful controls
retain one arbitrary T.own in caller frame with uninitialized dst, and reject
duplicating that owner after the copy. These verify the ownership separation
without imposing Copy/Freeze or inventing T rights. Exact stock spec stanza
and active spec hashes recorded; classified negatives require target entry,
return and exact post file/line/predicate.
