# CC3 ordinary upvar layout — source candidate only

Base is accepted CC2 `9631aaf89e869624fbfc8cd22d327ce194eb779d`.
Only `ty_layout.rs::data_bytes_for_ty` changes in production. Existing sized
zero-byte closure guard remains first. For a nonzero ordinary closure, convert
its actual public monomorphized type to the internal type inside rustc TLS,
obtain `args.as_closure().upvar_tys()`, then convert each actual upvar back to
public Ty. Collect and leave TLS before recursive public layout queries; no
internal lifetime escapes and no rustc_public bridge borrow is nested.

Use the closure's own FieldsShape::Arbitrary offsets and physical-order indices.
Field count is checked against the upvar list; each field recurses at
`current_offset + offsets[idx]`. The existing mask builder starts padding false.
This is the same capture list used by codegen_ty_closure, without asking for the
layout of a new tuple or presuming source order equals physical order.

CC2's ordinary environment aggregate SetRef was blocked by UnsupportedType.
A supported closure now supplies that existing setter with its data-byte mask,
including the saved &initialized slot. Source-read Check/CheckRef, entry/copy/
normal-edge policies and pointee checks are unchanged. Emitted setter and actual
&bool consumer binding remain UNKNOWN until coordinator evidence establishes it.

Recursive field computation propagates UnionAsField for by-value MU/union;
there is no all-true fallback, flattening, new transfer protocol or payload seed.
A reference field uses only pointer representation bytes, never referent bytes.
Coroutines, foreign/dynamic types and other unsupported guards remain unchanged.
CC1 active-cycle diagnostics, S3 actual registration/discarded bodies, M1 masks,
A3 pairing/Move/false, private assigns and marker diagnostics are untouched.

Twelve closure-zst goldens now state future CC3 requirements: six supported
positives, three payload negatives, three by-value UnionAsField boundaries.
Their Rust inputs are byte-identical to CC2. No historical observations or
strong JSON oracle bindings are rewritten. Three new files add eight roots;
expected files are acceptance requirements, never locally observed PASS.
Independent semantic review and all Rust/solver execution are coordinator-only.
