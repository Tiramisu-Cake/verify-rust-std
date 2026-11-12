# R8 type/signature audit — source only, NOT_COMPILED

Both edited files and all dependency hashes are recorded in SOURCE-MANIFEST.
B3 E0308/E0277 remain reasons to require actual compilation: rustfmt and Luna are not
a compiler. No cargo/rustc/Kani/CBMC/Miri/build ran locally.

- kani_mem_init retains ($core:path). `use $core as kani_mem_init_core` aliases the
  supplied core/std path using a complete use-path; avoids appending `::ptr` to an
  opaque path macro fragment. Existing kani_lib invocations pass core and std.
  This private alias is used by both null construction sites; no unused import.
- ArgumentBuffer fields saved_base/saved_byte are *const u8; new()->Self is const,
  every field initialized. ptr::null<T:PointeeSized+Thin>()->*const T is const; field
  and if-branch tuple context infer T=u8. Raw pointers do not require dereference,
  valid initialized payload bytes, Sync on this static mut, or a reference to source.
- Store retains fn<const LAYOUT_SIZE:usize,T>(from:*const T,selected_argument:usize,
  signature:usize)->(). T is the original sized generic; from.to_raw_parts() gives
  existing thin from_ptr. cast::<u8>() yields *const u8. `*const T::cast<U>` is const
  and requires no data read. `*const u8::wrapping_add(usize)->Self` is safe/const,
  requires sized u8, and scales by one byte. It calls wrapping_offset(count as isize),
  then arith_offset; Kani handles that intrinsic as pointer plus offset (source audit).
- pointer_object<T:PointeeSized>(*const T)->usize and pointer_offset with the same
  signature are exact library/kani_core/src/mem.rs hooks. New queries pass *const u8.
  Every offset/r/size/index operand is usize. `wrapping_sub(self,usize)->usize` is
  target-width modular arithmetic; no fixed-width cast or offset_from exists.
  Expr pointer_offset is ssize_t; hook casts to usize. CBMC6.11 BV zero-extends its
  O-bit slice, so do not assume signed extension or usize-width pointer offsets.
- Source match remains bool && usize comparisons. any() guard still infers bool.
  captured_value:bool and has_witness:bool are scalar copies before new calls.
  if tuple branches unify (*const u8,*const u8); inference does not involve references.
  All static reads/writes and hook usage stay in existing unsafe blocks; no new
  unsafe fn/signature/borrow or reference to static mut is introduced.
- Load retains fn<const LAYOUT_SIZE:usize,T>(to:*const T,selected_argument:usize,
  signature:usize,argument_count:usize,layout:[bool;LAYOUT_SIZE])->(). decoded index
  is usize; explicit range assertion precedes layout[index]. value && mask is bool.
  Destination offset+relative is the unchanged base expression/overflow obligation.
- Compiler typ.rs maps ty::RawPtr(u8) through codegen_ty_ref to codegen_ty(u8)
  .to_pointer(); codegen_uint(U8) returns Type::unsigned_int(8). The correct expected
  type is therefore Type::unsigned_int(8).to_pointer(), not Type::void_pointer().
  Type::unsigned_int<T:TryInto<u64>> and to_pointer(self)->Type are existing APIs;
  literal8 has the same established call pattern as typ.rs. The field tuple array
  remains homogeneous (&str,Type); assert_eq takes &Type and the same Type value.
- Symbol::to_expr(&self)->Expr, Expr::member(self,field,&SymbolTable)->Expr and
  Lambda::as_contract_for(&Type,Option<InternedString>,Expr)->Lambda remain unchanged.
  Member target stays a cell lvalue, not a cast rvalue/dereference/pointee. The same
  Vec<Lambda>, emitted-global identity checks and public routing remain intact.

Rust API implementation snapshot (not a claim about actual CI sysroot):
/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/wt-ci-kani-array-select-repro-20261101,
HEAD10d329311243aacf87b5d1aabf0453d549b8a694; core/src/ptr/const_ptr.rs:52,497,1154,
core/src/ptr/mod.rs:889, core/src/num/uint_macros.rs:2726. Exact hashes in manifest.
Kani pin rust-toolchain.toml is nightly-2026-10-23. CI must bind actual sysroot/API,
expanded macro, u8-pointer IR, target W/O and -Dwarnings. No local compiler available.

All other model functions, main constructor, Begin/reset/finalizer/skip/provider/
caller instrumentation, registry and old tests are byte- or token-compared to base.
Pinned TASK-M1 rustfmt formats/checks only the two source files; diff --check and
bounded Python audit check field coverage, capture/guard placement and unchanged code.

Research container diff --check reports only the one-space context line at SOURCE.patch:37
and identical review-packet/diff.patch:37. These are immutable patch data, not source
whitespace defects; patch hashes are preserved. Actual source diff --check passes.
