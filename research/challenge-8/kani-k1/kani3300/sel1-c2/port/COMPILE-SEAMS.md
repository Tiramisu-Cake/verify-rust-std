# SEL1-C2 bounded compile-seam review

Read the required `c2-slices/slice-02/COMPILE-SEAMS.md` and reused unchanged
`c2-slices/seam-audit/check_seams.py`. Exact base `8e299aa6243bc5f06a29c51e98aafa9564478220`,
head `14bc57fdb99960240c4944845a3d985c8af4dcf7`, reference `39a6521bf1b042358801cf613fd340623f35f851`.
Here the reference is the old SEL1 result, not final C2: added declarations must
come from that reviewed port while existing declarations/import leaves may come from C2.

`SEAM-AUDIT.json`: **PASS_BOUNDED_STATIC_SEAM_AUDIT**, 34 changed .rs files,
36 explicitly bound contracts / 54 call sites, no errors. All declarations,
imports and impls in those files are inventoried; generic impl consumers are also
checked across the compiler. The seven checked generic type names are recorded
in the report. Ten existing synthetic Python checks pass. The seven unchanged
controls.inc files are separately inventoried in `INCLUDE-INVENTORY.json` and
verified byte-identical to old SEL1; the .rs wrappers include those controls.

| Seam | Manual binding review |
| --- | --- |
| kani_middle::has_intrinsic_fallback | Public module helper, stable Instance input, bool result; one call each from codegen, reachability and select classifier. Same definition/predicate for all consumers. |
| kani_middle::select_unpredictable_fallback | Public `(TyCtxt, stable Instance)->Option<stable Ty>` helper. One analysis caller converts its internal Instance to stable. Two local visitor calls use stable types directly. Existing CrateDef/CrateDefType, rustc_internal and TyKind imports resolve the same APIs as old SEL1. Local DefPathData use is exact old SEL1. |
| Visitor additions | validate_select_fallback and store_call_arguments signatures match old SEL1; is_select_unpredictable helper matches it. Existing inherent/TargetFinder/MirVisitor impl headers and explicit lifetime arguments remain C2. Combined import includes both KaniFunction and select classifier; its leaves are baseline/reference union. |
| Shared protocol signature | Added TyCtxt at all three real entry/call/return consumers. Four-clause item/hook conjunction retained inside parentheses, select classifier outside it. Both paths return bool. No missing old one-argument caller. |
| Existing layout APIs | maybe_uninit_storage(TyCtxt,Ty)->Option<Ty>; for_typed_storage(TyCtxt,Ty)/from_ty(Ty)->Result<PointeeInfo,LayoutComputationError>; layout(&self)->&PointeeLayout; argument_size()->Option<usize>. All declarations exist in current C2. pub(super) admits this descendant pointer-uninit module. |
| Points-to regular call | Existing `(state,internal Instance,args,destination,Location)` explicit arity5 now has two callers. Same internal MIR operand/Place/Location types and existing analysis lifetimes. Recursive analysis still has8 arguments and preserves selected bodies, provenance and active-call failures. |
| C2 APIs retained | Baseline resolve_call/initial-target, immutable origin/registry and closure-layout APIs retain their current consumers. F6 reset helper has two calls, arity3. DelayedUbPass has two journal writer calls, arity2. No production signature changed outside the permitted visitor predicate. |
| statement/reachability | No declaration/import/impl changes. Removing the local FnDef match does not remove needed imports: TyKind/RigidTy remain used elsewhere in both files. |
| Fixtures | 29 root wrappers/bodies and corresponding expected files present, exact selectors and original flags; 65/65 files match old SEL1, no changed C2 fixture. Includes have no missing local helper declarations. |

First audit exited1: `SEAM-AUDIT-INITIAL.json` preserved. Two copied slice02
contracts had stale counts for already-final-C2 APIs: for_storage in check_uninit/mod.rs
is3 (lines273/288/941), maybe_uninit_storage in ty_layout.rs is2 (153/181).
Those files are unchanged by SEL1 and were inspected directly. Updated only those
counts to final C2; no arity weakened, source change or error hidden. Final audit exited0.
The intentional change to regular-call count1→2 binds the new select caller.

Reproduce from g0:

```sh
python3 research/challenge-8/kani-k1/kani3300/c2-slices/seam-audit/test_check_seams.py
python3 research/challenge-8/kani-k1/kani3300/c2-slices/seam-audit/check_seams.py --repo /root/kani-fix-3300-sel1-c2-w14 --base 8e299aa6243bc5f06a29c51e98aafa9564478220 --head 14bc57fdb99960240c4944845a3d985c8af4dcf7 --reference 39a6521bf1b042358801cf613fd340623f35f851 --contracts research/challenge-8/kani-k1/kani3300/sel1-c2/port/CALL-CONTRACTS.json --out research/challenge-8/kani-k1/kani3300/sel1-c2/port/SEAM-AUDIT.json
python3 research/challenge-8/kani-k1/kani3300/sel1-c2/port/check_port.py
```

Limits: lexical source checks plus manual binding review, no Rust parser/name
resolution, inference, borrow/trait checking, macro expansion or compilation.
No claim that this compiles. Native fmt/build/clippy/LLBC/Kani and all new gates
are NOT_RUN; independent worker15 review remains required.
