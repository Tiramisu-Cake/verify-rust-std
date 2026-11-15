# Slice04 compile seams — bounded static audit

Source `345cedfd67df679e326474385308349d609fc43d`, parent accepted03
`5ca51679e3f433718807a2e44add0d5abac128e7`, reference F `ad499e41dd2db9ccd432f89721638a1f3a0bbd44`.
Method follows `../slice-02/COMPILE-SEAMS.md` and `../seam-audit/README.md`.
The unchanged reusable checker inventories every declaration, impl and import in all107 changed
Rust files (eight production and99 fixture inputs), checks generic impl arguments throughout the
compiler, and records every same-spelling reference to changed functions. CALL-CONTRACTS-04.json
retains the earlier concrete bindings and adds the reviewed owner4 caller interfaces. Token matches
are not name resolution; the table supplies their intended binding.

| Seam | Definition and actual consumers reviewed | Result |
| --- | --- | --- |
| Instrumenter context | `UninitInstrumenter<'a,'tcx>`, matching inherent impl, `run(tcx,body,instance,safety,unsupported,cache,finder)`, field initialization; delayed and pointer passes | Both real callers pass seven arguments, including the same TyCtxt used by their visitor. Existing module/reexports resolve locally. |
| Operation API | All `MemoryInitOp` variants, constructors in pointer/delayed visitors and every exhaustive helper (`mk_operand`, `operand_ty`, `position`, value/count/union/argument helpers) plus dispatch | `CheckRefAs`, `SetStorage`, `BeginArgumentTransfer`, positioned `AssignUnion` and Load/Store metadata travel with producers and consumers. No future variant stub. |
| Address materialization | `mk_ref`, `mk_cast`, `expect_assign_union_operands`, CheckRefAs builder | Cast arity5/ref arity4; source/destination addresses are produced while live; reference CheckAs reborrow from03 retained. Imports include ProjectionElem and constant types. |
| Storage layouts | Existing owner2 wrapper/storage recognition, `for_storage`; new `for_deinit`, `for_typed_storage`, `PointeeLayout::argument_size` and test module | Sibling `pub(super)` helpers visible at all call sites; MachineInfo/FieldsShape/TyCtxt/LangItem imports available. Sized admission rejects Slice/TraitObject instead of using element size; existing unit filter adds one test. |
| Shared constant mask | `constant_init_mask(&Operand)` in relevant_instruction, visitor constant/repeat/transmute/ordinary-union consumers and builder constant StoreArgument materialization | One exported sibling helper, all callers pass one operand; None bytes remain false. Full ordinary-union constant branch V420–424 included. |
| Pointer visitor context | `CheckUninitVisitor<'tcx>` + matching TargetFinder/MirVisitor/inherent impls; `new(tcx,instance)` and pointer-pass caller | Declaration, constructors, generic impl arguments, field initialization and imports paired. No missing explicit lifetime. |
| Direct-call pairing | `has_transfer_protocol`, entry argument loads, callsite begin/stores/return load, Return store | One predicate at all three sites. Ordinary Item + body + nonforeign; exclusion exactly `KaniFunction::Hook`. Model/intrinsic marker classification is not broadened into Hook. Signature is the same monomorphized `instance.ty()`, argument indices1..n, mandatory return0. |
| Ordering and F6 | Caller gathers/snapshots all arguments, then clears only actual Move places; nested reset helper shared by ordinary and BlackBox paths; normal-edge destination reset | Full-storage `SetRef(false)` uses `for_deinit`, not payload mask. Copy sources are retained. Existing resolver Err/read/common-flush behavior and assignment UnionAsField refusal retained byte-for-byte from F. |
| Runtime markers | Compiler constants/KaniModel/lookup/SKIPPED_ITEMS, library `BeginArgumentTransferModel`, Store/Load/Copy models and `MemoryInitializationState` fields/new/setup reset | Begin emitted args `(signature,count)` match runtime2, Store `(ptr,index,signature)` runtime3, Load `(ptr,index,signature,count,layout)` runtime5, typed copy `(from,to,layout)` runtime3. `resolve_mem_init_fn` supplies matching layout-size/type generics. State stays within existing verifier-private marked object. |
| Runtime masks | Raw copy passes all-true extent mask; typed copy/load applies payload mask; snapshots use ids/offsets/value while source live | Compiler/runtime signatures present together. Runtime macro is inventoried as source; expansions/borrow/type constraints require CI. |
| Marker classification | `BeginArgumentTransfer` enum serialization and `marker_category_tests` | Hook, Model, Intrinsic and unknown names remain distinct; new filter has one test, no zero-test acceptance. |
| Remaining source seams | Owners1/2/3 source parts retain exact identities; layout keeps baseline Closure Unsupported arm; delayed writer retains exact pre-F7 forms | No closure5 or F7 API imported. Six of eight changed production files exactly equal F; layout differs only by owner5 Closure arms, delayed/mod only by authorized pre-F7 writer/import. Other F7 files remain parent-identical. |
| Fixture signatures/imports |99 exact-F fixture inputs and goldens; independent fixture dependency review | No altered golden or directive; seven capture-free closure syntax cases audited separately in FIXTURE-DEPENDENCY-AUDIT.json. Native discovery/expansion remains NOT_RUN. |

SEAM-AUDIT-04.json: PASS_BOUNDED_STATIC_SEAM_AUDIT; ten Python synthetic checker tests PASS.
The initial draft call contract used `layout.argument_size` rather than the actual
`pointee_info.layout().argument_size`; it correctly failed occurrence-count coverage with zero
matches. SEAM-AUDIT-04-DRAFT-CONTRACT.json preserves this detector result. Correcting only the
contract token sequence produces the final PASS on the same source SHA. No source change/retry/build.

Independent Luna HIGH read-only interface review is bound to exact candidate production blobs in
INDEPENDENT-SEAM-REVIEW.json. It reviewed the dirty candidate based on03, then confirmed all eight
blobs after its single commit. This bounded helper review does not replace worker15's full review.

These checks do not parse/typecheck Rust, resolve external traits, expand macros, establish MIR
lowering, prove runtime behavior or close deferred integration. Native fmt/build/clippy/unit/regression
results, push and CI are NOT_RUN. Full worker15 review and coordinator exact-head runtime results remain PENDING.
