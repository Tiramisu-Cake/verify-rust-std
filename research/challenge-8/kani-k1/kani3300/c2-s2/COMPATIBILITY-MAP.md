# C2-S2 — compatibility and qualification

Candidate `f96ad419bcae4e920708ff4bffe2b28d310f422e`, tree `bb02e1177745835e17878db00e7f9b653f43c5df`, over accepted S1 `69b13711e60a87458200833445d47488ab466344`. Static source reasoning only.

`Descriptor::compatible` compares full `Allocation` equality and exact mask/layout equality. The existing allocation representation includes `Vec<Option<u8>>` (therefore extent and Some(0)/None distinction), alignment, mutability and provenance/relocations. Equality does not zero-fill holes or compare emitted bytes alone. `frozen` remains an independently compared field in derived Descriptor equality; only registration uses physical compatibility.

| Existing symbol / new descriptor | Registration | Stored descriptor |
| --- | --- | --- |
| No prior symbol | Insert | Exact incoming descriptor |
| Compatible, false / false | Ok | Same allocation, mask/layout, frozen=false |
| Compatible, false / true or true / false | Ok | Same allocation, mask/layout, frozen=true |
| Compatible, true / true or repeated input | Ok | Same allocation, mask/layout, frozen=true |
| Incompatible, either descriptor admitted | Err(previous.clone()) | Completely unchanged |
| Incompatible, neither admitted | Ok | First descriptor unchanged, inherited policy |

OR is associative/commutative/idempotent only within an exact compatibility class. No such order-independence claim is made for incompatible, unqualified inputs that the inherited policy retains without error. No mask, layout, byte value, relocation, extent or alignment is merged or replaced.

Qualification still originates in `anonymous_origins`: supported monomorphic whole referent, offset zero, exact extent, Freeze. Finalize requires exact source Allocation equality and checks its mask. Exact named-static `static_source` remains an alternative. Register cannot create qualification when every input has frozen=false. `admitted()` still requires qualification, immutable allocation and no relocations; even synthetic qualifying mutable input remains unadmitted.

Unchanged: origin collector, named-static gates/types, binding/materialization/rebinding checks, model-local registry/seal, target match, canonical symbol/layout/lifetime/extent checks, diagnostics for genuine conflicts, reset-completion insertion and original reset edges. The BTreeMap still emits at most one seed mask per symbol, at reset completion, with no use/copy/overwrite reseeding. No runtime, visitor, points-to, DFCC, JSON, admission-domain, subrange or relocation-support changes.

Source/unit-only assertions do not establish actual AllocId coalescing or provenance. Real-source qualification remains UNKNOWN until coordinator inspection.
