# Source audit, not compilation

Authority: exact U/R1 git blobs and committed `bcc1a2af3fe13599b88acabc78c33e1394407dc5` / `899ffb5f26b79e89cec1b7cc537d54be494ab390`. No dirty source input. STATIC-AUDIT.py checks committed declarations/trees/references/arities and full coherent reconstructions; STATIC-CHECKS.json holds exact signatures. Pinned TASK-M1 rustfmt wrapper --check and git diff --check passed. These establish source consistency/formatting only. **Compile-plausible by source audit is not compilation PASS**; actual macro expansion/types/-D warnings must be checked by the first coordinator fork build, especially after prior B3 E0308/E0277.

## Every model producer/callee boundary

All14 existing fn_marker declarations equal U/R1/both siblings: one static marker KaniMemoryInitializationState and13 model functions. No extra static marker. Normalized generic order, argument/result types and arities are exactly equal; full declarations are in STATIC-CHECKS.json. Internal copy/copy_by_id/bless/bless_by_id signatures also exactly R1 in both siblings.

| Producer in pinned check_uninit/mod.rs | Model signature, const N:usize first | Arguments / return |
| --- | --- | --- |
| ptr_uninit/mod.rs:101–138 inject_memory_init_setup | InitializeMemoryInitializationStateModel, no generic | 0 / () |
| build_get_and_check Sized | is_ptr_initialized<N,T>(*const T,Layout<N>) | 2 / bool |
| build_set Sized/Union | set_ptr_initialized<N,T>(*const T,Layout<N>,bool) | 3 / () |
| build_get_and_check CheckSliceChunk | is_slice_chunk_ptr_initialized<N,T>(*const T,Layout<N>,usize) | 3 / bool |
| build_set SetSliceChunk | set_slice_chunk_ptr_initialized<N,T>(*const T,Layout<N>,usize,bool) | 4 / () |
| build_get_and_check Slice | is_slice_ptr_initialized<N,T>(*const [T],Layout<N>) | 2 / bool |
| build_set Slice | set_slice_ptr_initialized<N,T>(*const [T],Layout<N>,bool) | 3 / () |
| build_get_and_check Str | is_str_ptr_initialized<N>(*const str,Layout<N>) | 2 / bool |
| build_set Str | set_str_ptr_initialized<N>(*const str,Layout<N>,bool) | 3 / () |
| build_copy | copy_init_state<N,T>(*const T,*const T,usize) | 3 / () |
| build_assign_union | copy_init_state_single<N,T>(*const T,*const T) | 2 / () |
| build_argument_operation StoreArgument | store_argument<N,T>(*const T,usize) | 2 / () |
| build_argument_operation LoadArgument | load_argument<N,T>(*const T,usize) | 2 / () |

Producer get returns bool local; setters/copy/argument calls use unit locals. resolve_mem_init_fn takes layout length then pointee type; no ABI/layout/count addition. Copy and assign producers pass3/2 values respectively; store/load pass pointer plus checked MirConst Usize index, return unit. Compiler dispatch, all enum consumers, resolver, test and contract files remain byte-identical R1. Static checks restrict the entire tree diff to mem_init.rs, not just listed dependencies. Actual generated/retained MIR/GOTO instances and widths remain UNKNOWN.

Frozen pre-existing generic-arity caveat: mod.rs:821–829 resolver constructs `[Const(layout),Type(associated_type)]` for every call, while both str models declare only const N; Slice/Str producer selects u8 for str. This audit does not establish acceptance of a str instantiation or silently repair the compiler. That discrepancy is identical U/R1/both variants, outside this mem_init-only rollback and P1 scalar input; actual str acceptance remains UNKNOWN. The zero-argument initializer separately resolves `GenericArgs(vec![])` in ptr_uninit/mod.rs and calls with `vec![]` into a unit local.

## Integer operands, inference and bounds

Pinned mem.rs:281/289 signatures are `pointer_object<T:PointeeSized>(*const T)->usize` and `pointer_offset<T:PointeeSized>(*const T)->usize`, not u64/i64. tracked IDs/offsets, saved scalar IDs/offsets, argument index, layout_size, num_elts and const N are usize. Every ID/index equality compares usize to usize (literal0 inferred usize); active and &&/|| operands are bool; should_store/should_reset are explicitly bool; R1 `any()` in || is inferred bool. Comparisons `tracked_offset>=from_offset`, `<from_offset+num_elts*N`, `>=offset`, `<offset+num_elts*N` compare usize expressions and return bool. Multiplication and each range sum are usize→usize. R1 retarget `to_offset+(tracked_offset-from_offset)` has both operations usize; source guard ensures tracked>=from, not absence of addition overflow. R5-02 `tracked_offset += to_offset-from_offset` uses usize subtraction and addition; guard does **not** imply to>=from, so legacy underflow/overflow obligations change. No wrapping/saturation/assume or index truncation.

Layout<N> is [bool;N], tracked-relative array index is usize, entry/value bool. get_slice/set_slice num_elts and range arithmetic stay exact R1; zero-layout guards and bool truth tables outside the two groups are unchanged. No runtime usize/u64/u128 mixing/conversions. Compiler mod.rs:684 casts host argument_no usize→u128, then `MirConst::try_from_uint(...,UintTy::Usize).unwrap()`; this is an unchanged checked target conversion, host usize<=128 bound applies. Resolver mod.rs:825 separately casts host layout_size usize→u64 then calls `TyConst::try_from_target_usize(...).unwrap()`: explicit cast is type-correct but could narrow on a hypothetical host usize>64; preservation requires layout_size<=u64::MAX and accepted target-const range. These are existing compiler conversions, not new assumptions or changed runtime casts. Actual host/target widths, range acceptance and object-bits are receipt requirements, never inferred from host or assumed equal to object-ID width. No new conversion bounds, type bounds or coercion premises.

## R5-01 pointer/Option/constructor/unsafe audit

U main state has tracked_object_id:usize,tracked_offset:usize,value:bool; const new() initializes exactly0,0,false. initialize randomizes the tracked usize fields and sets value=false; **no ARGUMENT_BUFFER epoch reset** is added. Option starts None at static initialization; matching load clears it to None only after copy; mismatch keeps it. U reset semantics and stale state are diagnostic losses.

ArgumentBuffer derives Clone,Copy; usize/raw pointers implement these, so Option<ArgumentBuffer> is Copy and `unsafe{ARGUMENT_BUFFER}` reads a value, without moving a non-Copy static. selected_argument/layout_size usize; saved_address:*const (). `from:*const T` to_raw_parts produces (thin *const (),metadata); saved pointer uses that exact type. On load `to:*const T` yields thin *const (); `copy_init_state_single::<N,()>(saved_address,to_ptr)` expects two *const (), resolves T=(), then calls copy_init_state::<N,()>(...,1:usize), whose pointer casts give *const u8 to copy<N>. Layout N remains the original transfer size despite T=(), as in exact U; no size_of(()) replacement. R1 copy captures pointer IDs/offsets and invokes copy_by_id with five usize arguments. U capture does not query source object before choice; R1 pointer queries occur at consumption and may encounter an expired source slot. There is no new Rust dereference or mutable pointer, but a verifier lifetime/Unsupported/frame failure is possible and must remain visible.

All ARGUMENT_BUFFER Some/None reads/writes and MEM_INIT_STATE method accesses stay in the existing unsafe static blocks. Matching buffer is copied to a local before mutable MEM_INIT_STATE method call; clear occurs afterward. No escaping &mut/static reference or new borrow lifetime is introduced; existing method receiver &mut self is unchanged. No dangling removed field/constructor/helper references: committed git grep finds buffer/by-ID references only in this runtime file. The unmarked separate buffer is **not** added to contract.rs private assigns, so frame admissibility is deliberately not repaired.

## R5-02 scalar capture/consume and adapted core

Main state eight fields (six usize/two bool), const constructor and every initialize/store/load statement are exact R1. Active=false at constructor/epoch reset, store captures two usize values while source pointer is live, writes selected/saved/layout then active=true; return index0 mandatory. Matched load checks active/index, asserts usize layout equality, copies payload locals, computes destination ID/offset, calls copy_by_id<N>(five usize args including1), clears active then returns. Inactive/mismatch blesses one element and does not clear active. No Option/raw saved pointer. These sites/unsafe blocks/borrow order are unchanged R1.

copy<N>(&mut Self,*const u8,*const u8,usize) and bless<N>(&mut Self,*const u8,usize) stay thin R1 wrappers; by-ID interfaces take5/3 usize inputs after receiver. copy_by_id source-range predicate is exact U/R1; successful retarget preserves value (including false), no early return; matched+declined leaves state unchanged, nonmatch calls bless_by_id<N>(to_obj,to_offset,1:usize). bless_by_id keeps exact U range/value body after pointer extraction. This avoids ID→pointer reconstruction and dangling-pointer storage; U's original pointer-based helper is not claimed byte-identical. Retained GLUE changes extraction timing and call structure; underflow, false-state and full-span obligations differ. No default true, new assumption, new disable_checks, new unchecked pointer or hidden index narrowing. Source consistency cannot establish actual retained false paths, frame equivalence, compilation or correctness.
