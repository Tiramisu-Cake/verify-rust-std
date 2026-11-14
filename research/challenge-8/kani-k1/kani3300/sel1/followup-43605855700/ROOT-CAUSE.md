# SEL1 quick43605855700 — exact recognition defect

Prior tool46e46583ff112cae9c43aea1ba5dd6145e5e8387. Owner-provided SUMMARY/values-main excerpts report28/29 new controls FAILED, with repeated generic fallback refusal; existing205 expected,24 kani,17 ui and2 script controls remain intact. Composition remains known S5 debt. New source outcomes are NOT_RUN; the excerpts are not a new independent receipt/proof qualification.

## Cause and short-circuit

The defect was the identity check `def.name() != "core::intrinsics::select_unpredictable"` in kani_middle::select_unpredictable_fallback. That name is a rendered diagnostic path, not the defining item's canonical identity. The supplied values excerpt renders the intrinsic as `std::intrinsics::select_unpredictable::<u64>` and locates its actual fallback in toolchain library/core/src/intrinsics/mod.rs. The same error is shown for primitive and storage instantiations. Current repository source already documents this exact re-export behavior beside multi_char_eq_searcher_kind (mod.rs, original lines1471ff): def_path_str can render through std rather than core, so that helper matches crate and DefPathData instead.

The old string comparison rejects this spelling before reaching its signature and checked_body tests. Adding the printed std spelling would leave recognition dependent on rendering. The fix checks the defining DefId's canonical path: crate core; exactly two segments TypeNs(intrinsics), ValueNs(select_unpredictable). This admits both std/core references to the one definition, including core local in verify-std, without opening other intrinsics or prefixes.

## Predicate audit

| Predicate | Source/result | Followup |
| --- | --- | --- |
| InstanceKind | The local select-only Unsupported is emitted only after is_select_unpredictable checked Intrinsic kind and intrinsic_name | Unchanged |
| Compiler intrinsic name | Exactly select_unpredictable | Unchanged |
| Definition identity | Printed path incorrectly required core; supplied run prints std re-export | Canonical crate/namespace/item segments, exact match |
| must_be_overridden / has_body | Shared has_intrinsic_fallback is exactly the codegen/reachability rule. The supplied run has an instrumented intrinsic body property at core/intrinsics/mod.rs:744, demonstrating that reachability selected its body | Unchanged; no blanket bodyful-intrinsic support |
| Signature/generics | Frozen intrinsic source is const fn select_unpredictable<T>(bool,T,T)->T; supplied diagnostics show monomorphized bool/u64/char/pointer/MU signatures. The failing name check short-circuited before fn_sig on this path | Same exact bool input, equal two arm/output types, arity3, non-variadic, sized/mask guards |
| checked_body | Existing shared #5152 tail-call-aware body availability check | Unchanged; no unchecked body substitution |

Frozen source library/core/src/intrinsics/mod.rs:749–758 has the real if/forget fallback. Both shadow transfers and points-to still follow this same body; there is no additional backend result model, mask change or pointee initialization. No F5/F6/F7 fixes or refusal weakening were imported.

## Controls, filename and format

Existing selected_scalar_values now calls both core::intrinsics::select_unpredictable and std::intrinsics::select_unpredictable directly for u8, with one named useful value assertion and both branch covers. All previous scalar/pointer/MU/hint/Copy/Move controls remain. BlackBox and nested-layout refusal controls remain mandatory. The nested expected file matches exact MU payload/UnionAsField fragments without assuming whether diagnostic types print the std prefix; it still requires exactly one select-specific refusal and FAILED verdict.

The named panic comes from File::create in compiler_interface.rs:682. The supplied command names a very long test stem that is also its crate/harness name; artifact naming repeats this information in a mangled leaf. That existing test/file/harness is now overwrite_hole, including its exact-selector flag and expected header. No compiler filename/truncation mechanism was changed, and the negative was not removed; the manifest still has29 selectors.

The owner-provided rustfmt.sh was run with --edition2024 --config-path rustfmt.toml on mod.rs, uninit_visitor.rs, the three reported main.rs, the changed values main and renamed wrapper. The corresponding --check passed. The visitor changes are formatting only. No local build/rustc/Kani/CBMC/Miri/push/CI was run.
