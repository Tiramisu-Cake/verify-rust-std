# CC3 type/API audit — static source assurance only

Official nightly-2026-10-23 manifest identifies rustc
`7189d39d9ce936881b8132c6addeaf3e295cd455` (TOOLCHAIN.json).
RUSTC-API.json pins official source URLs, lengths and SHA256 fetched read-only;
no compiler or build was run. Runtime/typecheck acceptance remains NOT_RUN.

- rustc_public `unstable/convert/internal.rs`: RustcInternal for public Ty returns
  internal Ty lifted into the supplied TyCtxt. `rustc_internal::internal` drops
  its bridge borrow before returning. Existing Kani uses this conversion.
- `rustc_middle::ty` publicly reexports context::tls; tls::with passes TyCtxt to
  a higher-ranked closure. The collected return contains public types only.
- `rustc_type_ir/ty_kind/closure.rs`: ClosureArgs::upvar_tys obtains the actual
  substituted tuple's elements, not all parent generic arguments; List::iter
  yields copied Ty values. `unstable/convert/stable/ty.rs` implements Stable for
  internal Ty. Public GenericArgs exposes no direct upvar_tys API at this pin.
- Kani `codegen/typ.rs::codegen_ty_closure` uses precisely the same internal
  args.as_closure().upvar_tys; codegen_ty_tuple_like still lays out the original
  closure type. CC3 follows that capture identity/layout separation.
- Public abi::FieldsShape::Arbitrary offsets are indexed by logical field;
  fields_by_offset_order returns those indices sorted by physical offsets.
  Cardinality assertion and index lookup keep each mask with its own field.

| Field | Existing recursive mask / preserved boundary |
| --- | --- |
| bool true/false, ints | Scalar::Initialized data bytes; no value-dependent false bool handling |
| Thin/fat ref or raw pointer | Existing scalar/scalar-pair representation at field offset; pointee untouched |
| Ordinary struct/array/tuple/nested closure | Recursive mask at composed offset; padding excluded |
| Zero-size closure and ZST fields | Empty data contribution; original sized zero-byte fast path retained |
| MU/ordinary union by value | Existing UnionAsField propagated; no flattened initialized payload |
| &MU / &union | Pointer representation supported; actual payload reads still checked |
| Coroutine/foreign/unsupported | Existing diagnostics retained; no broader type claim |

Padding-negative pointer remains within the copied closure's live captured
Padded field. Every target hole starts as valid MU/raw/union storage; no invalid
typed bool is constructed before the intended read. Copy helpers require Copy,
with no destructors or duplicated exclusive references. Logical/physical order,
actual nonzero wrapper offset, source→model binding and last setters are UNKNOWN
until selected coordinator evidence; source syntax does not prove them.
