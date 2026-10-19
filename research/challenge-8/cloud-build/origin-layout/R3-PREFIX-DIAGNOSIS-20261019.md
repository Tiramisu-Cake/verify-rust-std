# R3 prefix — source-linked diagnosis, v0.11 follow-up

Updated from instruction6b688232, read-only follow-up after R3 CLOSED. Tool
08d6a578/profile82973e1e/translator2ff7b16f/runtime/posts unchanged. No new Build,
proof code or tool implementation. Earlier v0.9/v0.10 JSON observations and
closed ledgers remain historical evidence, unchanged.

## Actual source, MIR and AST

Old Build5f668cd9-fb34-4570-ad1c-4b97abbb36d0, executed sourcea0f3b7da;
prefix verifier reports verified/lib.rs214:17–23, Placeholders are not allowed
here. [Exact Rust](R2-PREFIX214-TARGETED-20261019.json): receiver `values` in
`let begin = values.as_mut_ptr();`. R2 Buildc78529d0 reports the same source
location, but the MIR/AST identities below belong to **old prefix Build5f668cd9**.

| Exact observation | Established fact |
| --- | --- |
| [MIR body11810–11815](R3-V011-MIR-BODY.json) | fn body defPath=b2_three_from_local and checked wrapper entry resources |
| [Local_5 declaration12030–12041](R3-V011-MIR-LOCAL5-TYPE.json), [continuation12042–12053](R3-V011-MIR-ARRAY3.json) | mutable reference to u64 array; region='<erased>; usize constant length h=0,l=3,size=8 |
| [Local_4 declaration12002–12013](R3-V011-MIR-LOCAL4-TYPE.json) | mutable reference to slice_u64; region='<erased> |
| [Cast span12414–12425](R3-V011-MIR-CAST-SPAN.json), [assignment12428–12439](R3-MIR-CAST-ASSIGNMENT-20261019.json) | verified/lib.rs, source low214/pos16, high214/pos22; lhs_4, rhsRvalue.cast |
| [Cast operand12438–12449](R3-MIR-CAST-OPERAND-20261019.json), [cast tail](R3-MIR-CAST-FRAGMENT-20261019.json) | move_5, projection=[], target erased region/mutable slice_u64; kind.pointerCoercion=void |
| [AST877](R3-V011-PREFIX-VALUES-TYPE.json), [878–889](R3-V011-PREFIX-ARRAY-STORAGE.json) | values:StaticArrayType(u64,3); actual RustStorageLive(values)887; _4/_5 declarations agree with MIR |
| [AST890–901](R3-PREFIX-AST-RECEIVER-CONTEXT-20261019.json) |894 AddressOf(values)→$_5;895 CastExpr to RustRefTypeExpr(InferredTypeExpr,Mutable,Slice(u64))→$_4;897 later as_mut_ptr call |
| [Actual stage argv](R3-V011-PREFIX-STAGE-ARGV.json) | source-reported verifast command includes -dump_ast_with_locs proof-ast.ml verified/lib.rs |

The nested assignment/cast fields, complete local types, array length, wrapper
identity, source range and translator's _4/_5→$_4/$_5 mapping provide the
source-linked correspondence. Text proximity to as_mut_ptr was used only to
locate the region; it does not establish node containment. This is not independent
parser replay: generic parser_input_binding=NOT_ESTABLISHED and causal_status=
UNKNOWN are retained. Stage command is data, not executed by this follow-up.

Frozen checker verifast1.ml4909 checks CastExpr target strictly; RustRefTypeExpr
2223 visits its lifetime; InferredTypeExpr2242 invokes the exact placeholder
error2252. Translator3777–3840 translates CastData.ty; reference handling1541ff
uses vf_ty_arg_of_region568ff, mapping erased region to InferredTypeExpr.
**Erased target region and source/target types are now directly observed**,
not merely inferred from those source branches. Generic arguments on the later
as_mut_ptr call cannot repair the preceding cast.

The Rust coercion **category** is directly observed as pointerCoercion.
Exporter lib.rs2724 collapses PointerCoercion{..} to unit; schema vf_mir.capnp598
stores Void. Its precise Rust coercion subtype, including Unsize, was discarded.
No amount of further reading this decode.out can recover that lost field.
A strict subtype gate needs a separately approved exporter/schema decision,
or a reviewed justification using exact source/type/identity instead.

## Metadata gate: concrete source route, not a later observed failure

values is a StaticArrayType local and has an actual StorageLive before its
AddressOf. In verifast.ml1007–1055, StorageLive for that type creates its address
using get_unique_var_symb_non_ghost(PtrType t). verifast1.ml6779–6789 constrains
Rust pointers to sized pointees to pointer_metadata_none; StaticArrayType is
sized (4428–4446). AddressOf(Var values) returns that existing WVar (4982–4988),
whose evaluator reads env (8563–8568). The element assignments shown between
StorageLive and AddressOf do not replace the array address.

At the array-reference→slice-reference cast, the sized-source case5551–5564
produces Upcast; evaluator8633 is identity. Therefore the source route carries
the array pointer's metadata_none through this cast rather than constructing
slice length3. The slice model consumes ptr_len(l): prelude_core.rsspec71–95,
462–469 and translator1259–1352. There is no established equation making
pointer_metadata_as_usize(pointer_metadata_none)=3. This is a **source-derived
metadata deficiency**, not an observed later verifier failure or a formal
soundness verdict. It is sufficient to reject a lifetime-only fix as justified.

Existing frozen std/lib.rsspec642–645 has slice_from_raw_parts_mut with post
`result as *T == data` and `result.len() == len`; translator2658–2674 already
uses it for raw pointer cast_slice. It is a possible representation building
block, **not evidence that this implicit cast already uses it**, nor permission
to add a new ownership bridge or use an unverified actual callee. Raw slice
pointer ownership remains unsupported in translator1231ff. Any proposed reuse
must justify pointer provenance/address, length and borrow/resource handling.

## Narrow proposal BEFORE implementation

1. Limit any new admission to this exact source-bound mutable array3/u64→same
   element slice coercion. Check source/body/operand/destination identity,
   mutability, length, element and lifetime; retain rejected mismatches.
2. Bind a real checked source lifetime/borrow rather than choosing static or
   allowing arbitrary InferredTypeExpr casts. Existing ghostGenericArgs bind
   calls; CastData has no cast-target ascription hook. No permitted proof-only
   binding for this generated cast has been found in the frozen profile.
3. Include correct length metadata construction with preserved data/provenance,
   preferably using an existing justified model operation if admissible. Do not
   pretend identity Upcast already preserves length3. Frontend/model/exporter
   deltas need explicit scope/profile decisions and reviewed pins before edits.
4. Prove the resource relation; metadata alone grants no array ownership,
   borrow, lifetime token or CURRENT resources. Preserve all full normal/unwind
   posts and runtime/std/generic signatures. Later as_mut_ptr support is not
   assumed successful merely because the cast is repaired.

Minimal **future Cloud** reproducer proposal, not implemented/run:

```rust
unsafe fn array3_slice_probe(values: &mut [u64; 3]) {
    let view: &mut [u64] = values;
    assert!(view.len() == 3);
    let _p = view.as_mut_ptr();
}
```

Supply checked physical array-cell/borrow/lifetime resources and full resource
return on normal/unwind. Frozen baseline should reproduce the lifetime blocker;
a separately approved candidate must establish len3/data/provenance before the
real call. Wrong-length assertion must fail after successful setup; pair wrong
mutability/element/length/lifetime/source/cast-shape negatives at intended gates.
Then run actual prefix false/true/firstContinue-panic with full CURRENT posts
and all4resource/admission/CURRENT18/HRTB/unwind/late-Cleanup/default-off/B1/
helper/receiver/end/retirement controls. The reproducer is not that theorem.

## Reporting limits resolved, proof limits unchanged

v0.11 client SHA0b14d80b… exposes info/value-start/locate/offset; targeted replies
schema v2, policy economical-exact-v1, content_filtered=false. Old16-quota and
WITHHELD are historical, not current blockers. Formerly refused local types and
argv now read successfully; administrative projection is no longer needed for
these fields. No raw GCS/full-log access or automatic full-file reconstruction.
[Per-request provenance](R3-V011-PROVENANCE.json) records exact file/index/archive
identities/selectors. New observations do not add proof credit: B2 OPEN,
normal false/true/Continue-panic remain unaccepted; no new control execution.
