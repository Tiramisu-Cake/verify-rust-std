# Worker14 static review — not independent acceptance

Exact candidate `14bc57fdb99960240c4944845a3d985c8af4dcf7` / tree
`1efb6e4dfa69d346df8e23741d11839b1932403d`, sole parent final C2 `8e299aa624`.
No remaining finding in this bounded author review. Worker15 independent delta/C2
seam review is **PENDING** and belongs to the next authorized stage. No compilation claim.

## Conflict-hunk types, comparisons and conversions

| Hunk / expression | Explicit source types and review |
| --- | --- |
| Combined visitor import and protocol predicate | KaniFunction is the unchanged current enum; try_from receives stable MIR Instance and returns Result<KaniFunction,_>. Hook(_) pattern exclusion remains only inside ordinary Item conjunction. select_unpredictable_fallback receives TyCtxt plus stable Instance, returns Option<stable Ty>; is_some yields bool. InstanceKind comparisons use the stable enum, not internal rustc InstanceKind. |
| Entry load indices | body.locals() is the stable local-declaration slice. enumerate yields `(usize,&LocalDecl)`; skip1/take(body.arg_count()) use usize. union_args is Vec<(usize,&LocalDecl)>. bb_idx==0 is usize equality. LoadArgument argument_no/argument_count fields are usize; dereferenced idx and len() stay usize. Valid `(bool,T,T)->T` leaves bool local1 out and original arm locals2/3 in. |
| Coexisting F6 helpers | needs_nested_call_reset(Ty)->bool, reset_nested_call(&mut self,&[Operand],&Place,bool) are unchanged. target in current Call is an Option of a stable MIR block index; is_some() supplies returns:bool. Operand::Move binds a borrowed Place; cloning it creates the existing stable Place value in Operand::Copy. SetRef(false) remains Before for moved inputs, After for a returning nested destination. No new cast or size comparison here. |
| New snapshot helper | args:&[stable Operand]. enumerate/filter/collect yields Vec<(usize,&Operand)>; filter's references are autoref/deref, retained values borrow args, not mutable self. iter().copied() copies the `(usize,&Operand)` tuple; operand.clone() supplies an owned Operand to MemoryInitOp. idx+1 and len() are usize, same arithmetic as extracted C2 stores; Begin count matches the entry loads. A later loop consumes the vector of references and deinitializes only actual Move places. All Stores precede that loop. No source borrow is invalidated by constructing ops. |
| Call signature checks | instance.ty():stable Ty; kind().fn_sig() returns a polymorphic signature, skip_binder gives its monomorphized signature. args.len() and sig.inputs().len() are both usize. zip pairs `&Operand` with `&Ty`; arg.ty(&self.locals).unwrap() and *ty are both Ty. destination.ty(...) and sig.output() are Ty. Equality is type identity, no numeric conversion or ABI coercion. |
| Classifier signature pattern | sig.inputs():&[Ty] destructures into three &Ty values. condition.kind() compares TyKind with RigidTy::Bool; left!=right compares &Ty, *left!=output compares Ty. c_variadic is bool. instance is stable Instance throughout, def.def_id() converts through rustc_internal into the internal DefId expected by tcx.def_path. DefPathData patterns borrow the path components; module/item Symbols compare their str views to fixed names. No display-name admission. |
| Payload/layout guard | layout()/shape().is_sized() yield layout result and bool; PointeeInfo::for_typed_storage(TyCtxt,Ty) and from_ty(Ty) return the same Result<PointeeInfo,LayoutComputationError>. map_err converts the error to String, not memory/type data. info.layout():&PointeeLayout; argument_size():Option<usize>, tested only with is_none. No integer cast, width mismatch or blanket full-mask replacement. |
| Points-to new caller | Analysis instance is internal rustc_middle Instance<'tcx>, args are &[Spanned<internal Operand<'tcx>>], destination is &internal Place<'tcx>, location is internal mir::Location. rustc_internal::stable(instance) is used only for classifier admission; the existing regular-call helper receives the original internal types, five explicit arguments. Its graph borrows and shared active_calls/body_overrides lifetimes remain C2. |
| Return witness | Place::from(0) and argument_no:0 are unchanged existing usize/local-index conversions. Predicate adds TcX plus select validation; Store still copies return place, uses real instance.ty(), and executes only in Return. Caller Load index0 remains After, through unchanged normal-edge insertion. |

No new `as`, try_into, integer widening/narrowing, pointer cast or dereference was
introduced in a conflict hunk. Existing unrelated conversions (raw_eq byte extent,
array indices and points-to usize→Local) remain baseline code. The source-token
checker is not a typechecker; native Rust borrow/trait/inference validation remains NOT_RUN.

## Required invariants and C2 intersections

1. Shared codegen/reachability fallback predicate and exact-core select classifier
   agree on body admission. Local size/layout/mask/type validation occurs before
   select-specific shadow operations. No new intrinsic model was introduced.
2. Points-to follows the same fallback via current ordinary-call analysis. Parameters
   receive actual operand successors, not caller-slot addresses. The fallback's two
   possible assignments join value-arm referents; return successors reach destination.
   There is no bool edge or pointee initialization/read introduced by selecting a pointer.
3. Begin/Store/load entry/return use the same real signature, original indices and
   counts. Both shadow arm snapshots precede either Move deinit; Copy is preserved.
   Selected false state and padding follow existing typed-mask assignments, with one
   result owner in the fallback. There is no second backend copy or blessing.
4. F6 helpers and both reset calls retained. Hook exclusion remains in all three
   shared predicate consumers. Existing unsupported intrinsics, foreign/bodyless/shim
   protocols and B1 traversal/flush retained. No true-conflict or caller control removed.
5. Immutable/F5, typed masks, closure layout, S3/CC, runtime/DFCC and all existing
   C2 fixture bytes are unchanged. Five final-F7 files are exact C2; both delayed
   writers still use replace_delayed_body, with journal scope/restoration unchanged.
6. All29 original selectors retained in12 groups; 65/65 files match old SEL1,
   including corrected39a6521bf1 goldens. No changed ignore/filter. Nested refusal is
   general aggregate UnionAsField before select; no select-specific coverage claim.
   Absent/overridden fallback and unsized T remain static-only guard review.
7. Docs edit only replaces the blanket select refusal with the sized/layout/mask/
   fallback boundary. No all-T/N, all-intrinsic, all-SmallSort or #5104 claim added.

Static fallback inspection: exact std70ba5befc6 intrinsics/mod.rs:749–757 forgets
the unselected arm and returns the selected arm; hint.rs:838 onward is the real
wrapper with pointer selects and a MaybeUninit select. File hashes and limits are
in FALLBACK-BINDING.json. This is source inspection, not measured compiler/sysroot,
emitted-MIR/body or binary binding; those remain native-CI obligations.

Validation: `git diff --check`, exact parent/tree/scope/fixture checks,
`PASS_BOUNDED_STATIC_SEAM_AUDIT` and10 synthetic Python checker tests. The initial
stale slice02 call-count mismatch is preserved and explained in COMPILE-SEAMS.md.
Compiler/fmt/build/clippy/LLBC/Kani/CBMC/Miri/new Quick/Gate A/replay: **NOT_RUN**.
No push, CI dispatch, Cloud build, upstream change or proof credit.
