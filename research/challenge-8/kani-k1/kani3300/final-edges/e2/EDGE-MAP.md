# E2 source map — SOURCE-REPORTED / NOT_RUN

Base C0: 478aad601fc5a45b142d6a8a2ae85594add9a0e6. Worker14 continuation; no new model.
The supplied bounded C0 log reports incompatible-layout transmute failures twice per subrange/relocation harness, and an uninitialized `[u8; 3]` read in static legal. It does not expose actual MIR.

| Edge | Source -> expected operation | Guard / mask -> property |
|---|---|---|
| Subrange | const shared reference, offset 1, extent 3 into 4-byte allocation; only SUBRANGE referenced by harness -> expected retained raw_eq | anonymous_origins still rejects offset != Some(0) / extent mismatch; raw_eq checks whole three bytes. Scalar-transmute avoidance is a lowering hypothesis pending MIR. Hole at allocation offset 3 (subrange offset 2). No admission extension. |
| Relocation | anonymous three-slot MU<&u8> array -> expected retained raw_eq over 3 * pointer_size bytes | real reference relocation retained in slot 0 and 2; actual hole remains slot 1. Descriptor::admitted still rejects relocations. No pointer initialization model. |
| Named static | SOURCE -> MonoItem::Static -> eval_initializer -> codegen_alloc_in_memory -> register_immutable_static -> model finalization -> reset completion -> raw_eq | require existing immutable_origin_type_supported, Freeze, immutable allocation, no relocations, exact sized extent, matching emitted declared type, const/static/nonextern/nonTLS flags. Descriptor retains Some(0)=true, None=false. Seed only original object at reset, never a pointer use/copy. |
| Named/promoted cache alias | anonymous address binding may reuse a named static symbol through alloc_map | named qualification applies only if full Allocation equals captured initializer; descriptor conflicts remain fatal. Named declared layout is checked separately from anonymous single-byte-array storage. |

The 2-byte/2-pointer original fixtures are valid storage; the observed rejection is not evidence of source UB. Using three slots preserves the edge while avoiding scalar-sized raw_eq lowering on the target. Actual operand/cast/lowering, data masks and full failure sets require coordinator CI.
