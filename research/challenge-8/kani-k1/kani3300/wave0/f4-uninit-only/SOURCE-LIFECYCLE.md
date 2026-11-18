# Conditional per-harness body lifetime

Source `ca1452227d6ad319f1b9bc1ad33bf618120733eb`, tree `baedd51d92073ecb2b96991bae7dc562ee8f58a2`, direct parent `b5a9678fd7c2a0f67c3fcafd90057fc2afaf9b5d`.
Frozen main `faffcee3bca2770c03bd21c3bde89cc8f6f7a14e`. Static source reasoning; native execution is NOT_RUN.

## Defect and chosen boundary

DelayedUbPass::transform computes targets and the points-to graph from the current
starting_items, obtains bodies from the transformer, and writes instrumented
TransformationResult values into its Instance-keyed cache. codegen_items receives
one harness as starting_items and uses the same transformer for reachability,
global instrumentation, any recollection, and codegen. Sharing these globally
instrumented bodies between harnesses contaminates the initialized control.
The previously published b5 fix clones the transformer for every harness.

The new check_uninit boolean is exactly
`queries.args().ub_check.contains(&ExtraChecks::Uninit)`, the effective predicate
used by DelayedUbPass::is_enabled. With it enabled, a complete BodyTransformation
clone is owned by the current harness and used through codegen. With it disabled,
codegen_items receives `&mut shared_unit_transformer`, as on frozen main.
DumpMirPass reads/dumps MIR, returns false, and its presence has no influence on
this guard. The PubFns path is unchanged.

BodyTransformation's derived Clone (unchanged from b5) copies both pass vectors,
cache entries including Body and modified flag, and both loop-contract metadata
maps. Their matching state therefore travels together. clear_codegen_cache and
template_passes.clone remain at the same harness boundary. Ordering, codegen,
result collection, unit contract/stub configuration and worker exports retain
the reviewed b5 lifecycle. validate.py restores the narrow edits in memory and
compares the rest of compiler_interface.rs byte-for-byte with b5.

## Cache and practical limits

Prewarming occurs only when export workers enable order_harnesses. In that path,
the enabled mode clones the warmed unit transformer. Without ordering, the
shared template starts with an empty body cache, and local transformations can
repeat across the enabled harness copies. Bodies first discovered after ordering
can also require local transformation in a harness copy. In disabled mode, the
shared transformer accumulates/cache-reuses bodies throughout the unit as main
does. Actual order, allocation cost, compile time and RSS are unmeasured.

## Inherited review boundary

The transform module, every pass implementation, loop maps and metadata, fixture
Rust, library, scripts, toolchain, dependencies and all 16 workflows are byte
invariant from b5. Prior whole-clone review remains historical evidence for that
unchanged implementation; review14 must review this new predicate/reference and
the two-mode Python oracle delta. Earlier CI covers b5 alone.
