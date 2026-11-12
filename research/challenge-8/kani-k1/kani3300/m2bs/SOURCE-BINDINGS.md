# M2-B/S source audit — PREPARED/BLOCKER

Pin `5f7f2b7364135a0a8b7cfd86c43b4491a8911bac`; all source hashes in INPUTS.json.
Local candidate `35fab624af19b8c724ddc9c80a7cc79289541459` adds only a handoff document.
The supplied task summary and M2-A package contain no curated C03 MIR/property/trace receipt.
This statement concerns supplied inputs, not absence of artifacts at the coordinator.
No raw logs/archives were accessed. Static source rules below do not establish an actual C03 operand binding.

## Three sites, two operands each

Unchanged C03 ordinary-singleton.rs has body equality line30, ensures line14 and root equality line39.
For each row ALL emitted bindings remain UNKNOWN: transformed instance/block/location, actual raw_eq/CheckAs,
property ID, both origin/carrier alternatives and AllocIds, mask, symbol/object/range, reset/seed,
last witness setter/retarget/copy, and read. The task reports SpecArrayEq<[u8;3]> only.

| Site | Left source candidate | Right source candidate | Required distinction |
| --- | --- | --- | --- |
| body | value:[u8;3], assume_init return destination | [1,2,3], possible promotion | normal setter versus immutable seed |
| ensures | *out:[u8;3] after assignment, generated captures/copies possible | independent clause literal/promotion | out referent versus generated local versus immutable RHS |
| root | caller out:[u8;3] after actual normal call continuation | independent root literal/promotion | caller transfer/setter versus immutable seed |

These are source candidates, not concrete origins. Do not assign the failure to the right operand from its
spelling, SpecArrayEq specialization or C04 differential. Neither AllocId nor source hash is runtime object identity.
The scalar result ==7 clause is retained; it does not discharge the array obligation.
No old() occurs in ensures; an old-copy explanation has no binding.

## Existing collection, binding and placement

| Anchor at pin | Verified static behavior | Remaining C03 question |
| --- | --- | --- |
| context/immutable_allocations.rs:80–116 | prepare scans each reachable item's original instance.body(); ConstantCollector visits ConstOperand; observe retains anonymous_origins | Which original generated-clause bodies and typed constants were reachable and observed? |
| codegen/function.rs:94–116; codegen/operand.rs:93–112 | codegen uses transformer.body(); codegen_const observes the actual emitted MirConst before allocation lowering | Did a transformed clause introduce a constant absent from original bodies, or erase its typed origin? |
| kani_middle/anonymous_allocations.rs:33–99 | Allocated carrier provenance decoded; shared Ref whole referent, slot0, one pointer, source layout/extent, offset0, supported type and independent is_freeze required; every resolvable unqualified origin retained | Actual constant.ty(), carrier slots/addend/options, referent type, Freeze and Mutability::Not UNKNOWN; closure/stack/capture immutability cannot be inferred |
| operand.rs:339–340,383–384,448–481,565–590 | memory/anon-static pointer routes bind actual returned direct symbol address; codegen_const_allocation returns alloc_map insertion OR reuse result | Which requested key/symbol/layout did each C03 operand use, including erased requests and coalescing? |
| compiler_interface.rs:140–204 | prepare before item emission; finalize after item/contract codegen and handle_quantifiers, before pretty/type/vtable snapshots/export | Actual model closure and requested generated-clause constants UNKNOWN; no source-order cure established |
| immutable_allocations.rs:162–208 | finalizer compares requested allocation with retained typed frozen origin, captures Some/None before zero-fill, compares canonical descriptors; admission requires frozen + Mutability::Not + no referent relocations | Is the failing source unqualified, missing binding, correctly seeded, or subsequently changed? |
| immutable_allocations.rs:210–315 | exact one-field [u8;n] layout, extent, static const/lifetime, live object + base0 + unsigned offset<n; original mask index assigned only to matching witness | Actual emitted storage/range and observed true/false seed UNKNOWN |
| immutable_allocations.rs:316–365; library/kani_core/src/mem_init.rs:240–249 | each original reset normal Return patched with seeds; original nondet object/offset, false and buffer resets retained | Actual reset completions, epoch, first effect and last setter/copy/retarget before read UNKNOWN |
| codegen/contract.rs:138–176 | existing marked private state included in modifies assigns | Actual Assert/generated routes and PFC frame behavior not established by source |

Original pointer carriers and referents are distinct. codegen_alloc_in_memory's hardcoded
has_interior_mutabity=false and is_static_const do not replace independent Freeze evidence.
Backend None-to-zero emission (operand.rs:654) is not an initializedness certificate.
All source alternatives, exact byte layout/extent, None false and descriptor conflict diagnostics must survive.
Existing D0 normal setter remains untouched; the current record supplies no new setter reproducer.

## Narrow proposal conditional on returned binding

1. If an actual generated-clause typed constant is missing from the original scan but retains a qualified
whole referent, collect that observed typed origin at an existing collection/emission site before sealing;
retain all alternatives and independent Freeze, Mutability::Not, exact layout/extent and original options.
2. If origin exists but its requested key is not bound, repair only that demonstrated emission route,
binding both insertion and reuse to the actual returned symbol. Carrier data never certifies referent bytes.
3. If correct seed exists and later witness changes cause the failure, collection/reseeding is not a fix.
Return the exact last-effect defect; do not bless ensures entry, call return, copies or mutable destinations.
4. ABI/protocol/DFCC rewrite, general retarget model or ambiguous epoch requires STOP with proposal.

No branch above is selected as an established diagnosis. A positive default, OR mask, early None blessing,
removed failing property or missing alternative is forbidden. The precise next action is CI-REQUEST stage A,
not a guessed semantic patch. M2-B/S semantic acceptance stays BLOCKED; no new B1/B2 credit.
