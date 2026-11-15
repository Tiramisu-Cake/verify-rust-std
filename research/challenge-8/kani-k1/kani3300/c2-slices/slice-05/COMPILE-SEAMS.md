# Slice 05 compile seams — bounded static check

Candidate `96f5d5dc8dedd369c6986a4f1dd5e698b6167f0f` on accepted4
`345cedfd67df679e326474385308349d609fc43d`. No native compiler was invoked.

Only `ty_layout.rs::data_bytes_for_ty` changes in production: two canonical owner5
parts, +28/-1. Its complete resulting blob is F's
`1cba3ff26fb96d4d9a248c4ef861d8c4d6c82e73`. Every other production file stays
parent-identical, including the authorized pre-F7 writer/import adaptation.

| Interface | Source check |
|---|---|
| Imports and type context | `rustc_public::rustc_internal` and public `Ty` already belong to owner2/accepted4. No import, signature, generic declaration, impl header, field or public API changes on5. Internal types use fully qualified paths. |
| TLS lifetime | Convert public `ty` to internal type inside `rustc_middle::ty::tls::with`; destructure the internal Closure type, take monomorphized `args.as_closure().upvar_tys()`, convert each capture back with `rustc_internal::stable`, collect `Vec<Ty>`. The internal context ends before public recursion. |
| Capture type agreement | `codegen_cprover_gotoc/codegen/typ.rs::codegen_ty_closure` lines830–833 takes the same monomorphized upvar list and calls `codegen_ty_tuple_like` with the actual closure type. No substituted tuple layout. |
| Field/index/offset agreement | Within the existing `FieldsShape::Arbitrary { ref offsets }` branch, require upvar count == offsets count. Traverse the closure's `fields_by_offset_order`, use logical index for both capture type and actual offset, add enclosing `current_offset` once. |
| Recursive mask API | The unchanged three-argument `data_bytes_for_ty(machine_info, ty, current_offset)` has one additional call. Inherited call contract count changes12→13. The caller passes public `upvar_tys[idx]` and propagates layout errors with `?`. |
| Zero bytes | A sized closure with size0 returns empty data bytes before querying upvars. Nonzero environments recurse through the existing layout/error rules. |
| Fixtures | All47 source files and47 goldens exactly match F. Source/golden identities, unchanged directives and semantic oracles are in ORACLE-DELTA; dependency analysis in FIXTURE-DEPENDENCY-AUDIT. |

The reusable checker inventories every declaration/impl/import in all48 changed Rust
files and checks explicitly bound calls across compiler sources, including unchanged
ancestor consumers. CALL-CONTRACTS-05 extends the accepted4 contracts with the TLS,
conversion, upvar and stable-map seams. Ten existing Python synthetic checker tests PASS.

The first draft contract retained ancestor recursive-call count12 and bound the general
`map` token with an incorrect expected count2. The checker reported actual counts13
and6. Draft contracts/report are retained; the final contracts use the added recursive
call and the fully scoped upvar-map token sequence. This corrects audit metadata only;
the source candidate and its SHA never changed.

Independent Luna HIGH reviewed the source/API and every new fixture pair, with no
actionable findings (INDEPENDENT-SEAM-REVIEW.json). Worker15's full review remains
PENDING. These checks do not expand macros, resolve Rust symbols/traits, typecheck,
establish MIR binding or prove compilation. Native fmt/build/clippy/unit/Quick are NOT_RUN.
