# Static type and layout audit

worker14; source 0ad35c0a9345d6dc460ef0f2ed2adea7b76d235b, parent 4f64cc617c. Compiler/verifier NOT_RUN.
Only `check_uninit/ty_layout.rs:472–476` is added to production code.

| Expression / binding | Concrete type and static evidence |
| --- | --- |
| `ty` | `rustc_public::ty::Ty`, explicit `data_bytes_for_ty` argument. No new generic parameter or capture binding. |
| `ty.layout().unwrap().shape()` / `layout` | `rustc_public::abi::LayoutShape`: same expression assigned to the explicitly typed `LayoutOf.layout` in `kani_middle/abi.rs:9–20`. Successful rustc query; existing unwrap remains. |
| `layout.fields` | `rustc_public::abi::FieldsShape`, outer match. `Arbitrary { ref offsets }` borrows offsets; guard adds no move, mutation or offsets binding. Other fields-shape arms are unchanged. |
| `ty.kind().rigid().unwrap_or_else(...)` | A shared `RigidTy` match from the existing rigid-type accessor; guard `RigidTy::Closure(_, _)` binds neither field. Wildcards discard no capture data: they identify the type kind, and full layout decides size. |
| `layout.is_sized()` | `bool`; same method used as the direct return expression of `LayoutOf::is_sized() -> bool` (`abi.rs:24–26`) and existing `from_ty` condition (`ty_layout.rs:227`). Immutable receiver borrow. |
| `layout.size` | `rustc_public::target::MachineSize`, used as the same `size` field throughout the file; existing enum tag/stride/scalar sizes use this representation. |
| `layout.size.bytes()` | `usize`; existing `generate_byte_mask` passes `data_bytes.size.bytes()` directly to `Iterator::take(usize)` and `from_ty` passes this value to `generate_byte_mask(usize, ...)`. No cast/narrowing. |
| literal `0`, `==`, `&&` | `0` inferred as `usize` from `bytes()`; comparison returns `bool`, combined with `is_sized(): bool`. This is the identical predicate already in `LayoutOf::is_zst` (`abi.rs:29–31`). |
| `Ok(vec![])` | `Result<Vec<DataBytes>, LayoutComputationError>` from the function and all neighboring match arms. The inferred vector element is private `DataBytes`, not `bool` or a rustc size. |
| `current_offset` | Existing `usize`; no chunk exists to offset for a zero-byte closure, even nested at a nonzero enclosing offset. |

The exact nightly's external rustc_public definitions are not installed locally.
This audit uses the pinned repository's explicit types, signatures and identical
existing predicate; it does not claim a compiler/typecheck result. rustfmt is
unavailable on PATH and was not run; formatting would not validate these types.

The query is still `ty.layout().unwrap().shape()` before either match. No query
failure becomes zero or success. The new arm is only in `FieldsShape::Arbitrary`
and only `RigidTy::Closure`; sized nonzero or unsized closures still match the
unchanged UnsupportedType arm at479. Coroutine, coroutine closure/witness,
foreign, FnDef/FnPtr, Dynamic, union-field and niche branches retain their paths.
Zero-sized primitive support predates this patch and is unchanged.

`PointeeInfo::from_ty` checks sizedness first, gets size0, calls data_bytes_for_ty,
then `generate_byte_mask(0, [])` returns `Vec<bool>[]`: `PointeeLayout::Sized`.
`check_uninit/mod.rs` still builds the normal check/set, `mk_layout_operand`
builds `[bool; 0]`, and `resolve_mem_init_fn(layout.len(), Ty)` supplies const0
as target-usize. Runtime `mem_init.rs:254–281` has get=true/set=return *before*
raw pointer decomposition or any MEM_INIT_STATE access. Its copy models likewise
return for const0 (`381–424`). No witness, tracked object/offset/value or protocol
field is changed by the empty-mask get/set, including when another payload's
witness is false. A read of that `u8` still gets its own one-byte layout/checks.
Runtime/points-to/S3/pass/check count and transfer policies are unchanged.

Layout comparison callers: `tys_layout_cmp_to_size` still requires two successful
layouts, excludes Union/TraitObject, enforces destination length <= source, then
compares zipped bytes. Empty→nonempty fails length; empty→empty is vacuous; a
nonempty→empty destination has no required bytes, as for existing ZSTs. This may
avoid previously conservative target seeding for equal zero-byte pointees in
`delayed_ub/initial_target_visitor.rs:80–99` and permit size-compatible ZST
transmutes in `ptr_uninit/uninit_visitor.rs:911–925`. No nonzero payload byte is
licensed by either result. Nonzero closures remain Err/false. No error-tolerant
fallback or immutable-origin admission change is introduced. General capture
layouts require a separate patch with recursive upvar masks and real offsets.
