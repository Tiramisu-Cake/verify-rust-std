# Compile dependency audit after the E0726 finding

Current head2 `932fb8395a58f8c86c0d702ba2cae835823b2962`, parent/accepted head1
`d82752c8bc878398e672bffaa631ca6a28430acc`. Audit reads exact Git refs, not an assumed worktree HEAD.
Coordinator reports run43699468860 on superseded b0a5a4fff9 failed with E0726. No raw logs were read.

The original source-map assigned the replacement trait impl together with the adjacent raw_eq comment
on3. The earlier static validation checked agreement with that map and could not detect its mistake.
The correction changes only the impl header to exact F `impl MirVisitor for InitialTargetVisitor<'_>`.
Canonical `B1--F:14:006` now has three unique parts: B1:68 deletion→2, F76 comment→3, F77 impl→2.
No raw_eq functionality, tests or unrelated signature/API changes enter2. Head1 and F stay unchanged.

## Method and scope

`../seam-audit/check_seams.py` inventories every function/type/module declaration, impl header and use
in ALL changed Rust files:10 on1 (six production + four comment-only fixtures),21 on2 (15 production
+ six new fixtures). It tokenizes comments/literals separately, balances delimiters, compares added
signatures to exact F, compares import leaves to baseline/F, and retains complete current imports/impls.
The pre-F7 combined import is checked by individual paths, not incorrectly rejected for mixing owners.
Generic types from changed files are checked against impl headers throughout all compiler Rust files,
including unchanged consumers: required explicit lifetime/type arguments and arity must agree.
Explicitly bound API call contracts check arities and occurrence counts; all same-spelling references
in the entire compiler are separately inventoried for human binding review. Common names do not
silently become symbol-resolution claims. The report records every new/removed signature, not only
signatures named in a hand-written shortlist.

Manual review below connects these inventories to their real symbols/imports. Pure internal helpers,
trait callbacks and unit helpers in exact-F files are checked with their enclosing type/trait/imports;
new APIs crossing files are bound to their concrete callers in CALL-CONTRACTS-01/02.json.
Ordinary baseline interfaces retained until4/7 are checked against baseline, not forced to future F.

## Slice1 dependencies reviewed

| Files / interface | Paired pieces and consumers | Result |
|---|---|---|
| points_to/mod + points_to_analysis | AnalysisBodyOverride/BodyProvenance declarations and public reexports; delayed registration HashMap/body selections | All declarations/imports/export paths present1. |
| run_points_to_analysis | New fifth body_overrides argument, Result return; sole delayed/mod root caller and Err/Ok handling | Five arguments; Result consumed before graph join. |
| PointsToAnalysis::run | Shared `'a` borrows for body/call_graph/overrides/active_calls, `'tcx` MIR types; inherent and Analysis impl targets | Eight arguments at both root and recursive callers; generic arguments explicit in all impls. |
| ActiveCalls/AnalysisKey/CallerLocation/error | Generic declarations, Display impls, RefCell/HashMap/Display/SourceLocation/readable_name imports, constructor fields | Declared and imported1; inherent/trait impl generics agree. Unit types have their own scopes/imports. |
| apply_regular_call_effect | Added location argument; terminator caller; recursive analysis with caller metadata | Five explicit call arguments, eight recursive run arguments. |
| resolve_call | Added tcx argument; public export, analysis call, pointer visitor wrapper and its caller | Both resolve_call sites have2 arguments; pointer wrapper/caller have3. Existing TyCtxt import available. |
| delayed initial_target helper | Same spelling try_resolve_instance, distinct local Option-returning helper | Remains two arguments and no new tcx; slice1 changes comments only here. |
| delayed/instrumentation visitor | needs_set(&self, place), PointeeInfo/PointeeLayout, MutableBody/SourceInstruction/InsertPosition and pre-existing layout methods | Import paths/constructors/method calls present1; no for_storage/type/protocol helper needed. |
| delayed/mod | GlobalPass impl unchanged; registration/failed-root paths use imported attributes/models/body APIs and real pre-F7 writer | Imports are exact baseline/F leaves; no F7 API required until7. |
| ptr uninit visitor | Only tcx resolver declaration/call; existing body/impl/imports and baseline diagnostics/helpers | No late visitor/storage helper deletion or dependency. |
| Four fixture edits | Only comment text changes | Function declarations/flags/goldens unchanged. |

PointsToAnalysisError is a `pub struct` inside a private module. Its inferred public return is usable
by current callers; the absence of a reexport makes its external spelling unavailable but does not
establish a private-interface compile error. No visibility refactor is introduced into this extraction.
The accepted source1 commit and its own hunk parts remain byte-identical; the new audit is additional
static checking, not a rewrite of its NO_REGRESSION/PENDING integration history.

## Slice2 dependencies reviewed

| Files / interface | Paired pieces and consumers | Result |
|---|---|---|
| initial_target_visitor + delayed/mod | Struct<'tcx>, tcx field, inherent impl<'tcx>, new(body,tcx), initializer, MirVisitor target<'_>, sole constructor caller | Complete2 after correction; caller has2 arguments; no raw_eq seed/comment from3. |
| anonymous_allocations + kani_middle/mod | Module export, AnonymousOrigin fields, anonymous_origins(tcx,constant), referent_extent and target_matches | Origin helper has three real consumers (graph/target/registry); target check in finalizer; declarations/imports present2. |
| points_to_graph + analysis | constant_successors(&mut self,tcx,constant), MemLoc::Anonymous and metadata, all graph impl targets/lifetimes | Two analysis callers each have2 explicit arguments; graph constructors/join/closure fields paired. |
| initial target/delayed graph arms | AnalysisTarget::Anonymous producer and exhaustive conversion; direct referent analysis targets | Enum arm and its conversion present together; no unmatched new generic type. |
| context/mod + goto_ctx + immutable registry | Module registration; public registry type with Default; GotocCtx field and constructor initialization | Explicit super module path resolves; field is initialized; all GotocCtx impls use both lifetimes. No extra reexport needed. |
| operand emission | observe(constant), bind(key,&allocation,&address) at four emission/reuse paths | Declaration+current imports in registry;1/3 arguments, all five real call sites covered. |
| static_var emission | Clone allocation before emission; register(def,&alloc) | Two arguments, StaticDef/Allocation APIs unchanged; no move after consumption. |
| compiler_interface | prepare(&items), finalize(), existing quantifier handling/metadata/split | Both methods declared2;1/0 arguments; same MonoItem slice input; no F7 scope required. |
| registry internals | Descriptor::new/admitted/compatible, register, seed_returns, ConstantCollector MirVisitor callback | Exact F file including all impls/trait imports and nine units; GotocCtx type resolves to existing ancestor definition; reset/private-state model markers already U. |
| anonymous origin imports | CrateDef trait for def_id/eval paths; TyCtxt/TypingEnv/rustc_internal and allocation/target types | Exact F use set present2; no assumed implicit trait import. |
| qualification/export | immutable_origin_type_supported and transform reexport; caller paths in anonymous/static | Both consumers have2 arguments; helper calls recognized storage layout already2. |
| ty_layout recognition/layout | LangItem, TyCtxt, CrateDef/CrateDefType/rustc_internal, GenericArgKind imports; wrapper_inner/maybe_uninit_storage/for_storage | Every new import used by current recognition code; 3/2/2 argument helpers paired. Existing data_bytes_for_ty signature unchanged, closure branch not required. |
| Six new fixtures | Functions/static/const declarations, imported traits/types and flags | Exact F fixtures; no call to delayed features3/4/5. All existing fixtures remain unchanged. |

Whole changed-file import/impl inventories are in the JSON reports, including unchanged impls in
shared files. Trait callbacks retain their existing trait signatures. Reference equality is supporting
source evidence; it is not substituted for checking cross-file availability at this cumulative head.
No additional missing compile prerequisite was found in the bounded static/manual review.

## Results and limits

- SEAM-AUDIT-01.json: PASS_BOUNDED_STATIC_SEAM_AUDIT at exact accepted1.
- SEAM-AUDIT-02.json: PASS_BOUNDED_STATIC_SEAM_AUDIT at exact revised2.
- SEAM-REGRESSION-OLD.json: expected FAIL at old b0a5a4fff9, exactly one error, InitialTargetVisitor impl lacks its required lifetime argument at line76. Original process exit1 preserved as intended detector outcome.
- Ten synthetic Python tool checks pass: missing/explicit lifetime and type generics, wrong generic arity, cross-file impl, comments/raw strings, nested imports, argument arity/nested calls and missing constructor argument.
- Canonical map coverage/owner-part bijection and unchanged owner1 parts checked separately; source/residual alternate-index endpoints match exact revised2/F trees.

This tool is a source-token checker, not a Rust parser/name resolver/trait checker/typechecker. Its call
bindings require a reviewed contract; macros, inference, full field/borrow checking and external trait
resolution need native CI. Reports must not be called compile PASS or full proof that every possible
Rust dependency is closed. The new head needs worker15 correction review and fresh exact-head CI;
old overlays/reviews are not silently rebound. All native builds/tests, push and CI in this revision
session remain NOT_RUN. Deferred fixtures/qualification heads3/4/5 remain unchanged.
