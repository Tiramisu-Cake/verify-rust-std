# Source type audit for both Rust deltas

Audit against exact U/R1 git objects and sibling V01/V02 commits in manifest; source hashes in INPUTS. No cargo/rustc/Kani/CBMC/Miri/build was run. Pinned TASK-M1 rustfmt wrapper `--check --config-path /root/kani-fix-3300-m2br3/rustfmt.toml` returned0 on each variant's extracted file; this establishes formatting only. First coordinator fork build must check actual Rust types, including -D warnings and macro expansion. Prior B3 E0308/E0277 precludes claiming compilation from static audit or Luna review.

## V01 — one expression delta

R1 mem_init.rs:404 `store_argument<const LAYOUT_SIZE:usize,T>(from:*const T,selected_argument:usize)->()` unchanged. Old comparison has both operands usize (literal0 inferred), result bool; `||` operands bool and `any()` inferred bool. New `if super::any()` infers bool directly from condition, same as U's explicit `let should_store:bool`. No arithmetic, integer conversion, deref, signature, bound or mutability changes. Removed use of selected_argument in condition does not make it unused: field assignment still consumes it. from.to_raw_parts and pointer_object/pointer_offset calls remain before choice. Value/index/layout fields and unsafe mutable static assignments remain R1. No imported symbol or enum match changes.

## V02 — coherent U runtime against R1 emission

Replaced whole file equals U SHA256 `88f260ddc5b315a32e64b0f6f396451373d2fb54f1a4898233508ebd81cd993c`. All14 fn_marker declarations (13 model functions plus private static marker) and normalized exported model signatures match U/R1/V01/V02. Core signatures:

| Marker/API | Operand/result types and consumer |
| --- | --- |
| StoreArgumentModel / LoadArgumentModel | const LAYOUT_SIZE:usize,T; (*const T,usize)->(); R1 mod.rs:648–698 builds exactly pointer operand + MirConst::try_from_uint(argument_no as u128,UintTy::Usize), return unit; no typed layout/signature/count parameter at R1 |
| CopyInitStateModel / SingleModel | (*const T,*const T,usize)->() / (*const T,*const T)->(); R1 build_copy and build_assign_union use these arities; single supplies count1 inferred usize |
| IsPtrInitializedModel / SetPtrInitializedModel | (*const T,Layout<N>)->bool / (*const T,Layout<N>,bool)->(); same U/R1 generic const/type order; set/get slice/str/chunk marker signatures also identical |
| KaniMemoryInitializationState | static mut MemoryInitializationState; constructor const fn new()->Self. Both versions declare marker. Internal fields change coherently; contract.rs:146–170 finds whole symbol, never names removed buffer fields |
| PointerObjectHook / PointerOffsetHook | mem.rs:281,289: <T:PointeeSized>(*const T)->usize on both pins. No u64/i64 return assumption; saved ID/offset fields are usize in R1 |

U ArgumentBuffer derives Clone,Copy, fields selected_argument:usize, saved_address:*const (), layout_size:usize; ARGUMENT_BUFFER:Option<ArgumentBuffer>. `let(from_ptr,_)=from.to_raw_parts()` gives thin *const () for assignment; load uses copy_init_state_single::<N,()>(saved_address,to_ptr), both *const (); fallback casts to *const u8. No reference dereference or mutable-pointer coercion added. Copy/bless receive &mut self and raw *const u8; assignments occur inside existing unsafe static blocks. Option read/copy and None/Some write plumbing restored together; all constructor fields present.

Arithmetic in restored U copy/bless/get/set is usize throughout: IDs, tracked offsets, pointer offsets, num_elts and N. `from_offset + num_elts*N`, `offset+num_elts*N`, comparisons and indices have no usize/u64 mix. `tracked_offset += to_offset-from_offset` restores U's possibly-underflowing subtraction order; R1 used `to_offset+(tracked_offset-from_offset)`. Both sides usize, result usize; guard constrains tracked_offset>=from_offset but not to_offset>=from_offset. Overflow/underflow obligations therefore can change and must be inventoried, not assumed preserved. U fallback copy blesses count1, not num_elts; declined source-follow branch may retain old destination state. These are diagnostic semantic losses, not type fixes. Array layout is [bool;N], index usize; no u128 runtime arithmetic introduced. Only the unchanged compiler index construction casts usize to u128, lossless for admitted <=128-bit target usize, then converts back via checked MirConst Usize; actual target width/bounds receipt remains required.

Dependency closure: R1 git grep finds copy_by_id/bless_by_id/new buffer field references only inside mem_init.rs; whole-file rollback removes callers and definitions together. External compiler code selects model marker IDs, not these internal methods/fields. Both compiler call sites carry tcx; new MemoryInitOp variants and exhaustive consumers, layout helpers and uninit visitor are byte-identical R1 in both variants. No enum removal, missing match arm, partial API rollback, new ABI, deref or trait arithmetic introduced. This static source closure does not certify generated MIR/custom-MIR/macro behavior or absence of compile warnings.

Lost obligations and lifetime hazards are in ABLATION-PLAN; runtime pointer capture can outlive a return slot under unchanged R1 producers. First build failure is SETUP/solver NOT_RUN; no local substitute build or hidden historical pin repair.
