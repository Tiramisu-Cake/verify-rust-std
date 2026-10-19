# R3 prefix: actual AST diagnosis and narrow proposal

Task merge-first-comparator-2026-10-19-r3; frozen tool08d6a578/profile82973e1e.
Proposal only: no tool, runtime, proof contract or matcher changes implemented.

## Observations and boundary of the diagnosis

Old Build5f668cd9-fb34-4570-ad1c-4b97abbb36d0, source a0f3b7da, reports
verified/lib.rs214:17–23, `Placeholders are not allowed here`.
[R2 exact Rust](R2-PREFIX214-TARGETED-20261019.json) identifies the `values`
receiver in `let begin = values.as_mut_ptr();`. This is the unchanged wrapper
location also failing in R2 Buildc78529d0, not an observation of R2's AST.

[Targeted AST890–901](R3-PREFIX-AST-RECEIVER-CONTEXT-20261019.json):
- 894 assigns AddressOf(values) to $_5;
- **895 assigns CastExpr(RustRefTypeExpr(InferredTypeExpr, Mutable,
  SliceTypeExpr(u64)), $_5) to $_4**, all at214:17–23;
- 897 calls slice as_mut_ptr with $_4 at214:17–36. Its inferred generic
  argument has a different call location and follows the failing cast.
The original array has three u64 elements. Source214 location plus frozen
checker route identifies the forbidden placeholder in the archived AST's cast.
At the initial checkpoint no direct MIR region observation had been obtained; the v0.10 follow-up below supersedes that limitation.

Frozen verifast1.ml4909 checks CastExpr target using strict check_pure_type;
RustRefTypeExpr2223 checks its lifetime child; InferredTypeExpr2242 invokes
report_inferred_types_as_error2252 with the exact diagnostic/location.
Translator3777ff translates MIR CastData.ty into this CastExpr; reference
translation1541ff uses vf_ty_arg_of_region568ff, whose erased-region case
produces InferredTypeExpr. Thus erased MIR region is the supported translator
explanation, **initially deduced from source**; the v0.10 follow-up below directly observes the erased target region.

Provenance: AST SHA3193176be89d0f18982253759930c9bdac47f2c1c4b6bc83c2437a69603a1f0c;
archive8ffe3689…/index3e3e6bad…; exact bounded response, requestdd82ccf0…;
coordinates are archived AST lines, not MIR offsets. Four targeted queries
returned37/925 AST lines; no complete file reconstruction/raw access. The header
and final declaration established bounded location context, followed by the
source214 receiver node. No further neighboring scan is proposed.
All generic responses retain parser_input_binding=NOT_ESTABLISHED and
causal_status=UNKNOWN. Runner copy-on-drop-prove.py760 invokes verifast with
`-dump_ast_with_locs proof-ast.ml verified/lib.rs`; concrete-consumer.py289
checks stage/source hash continuity. This supports source-reported linkage,
not independent parser replay. Reader /argv on verifast-stage.json returned
NO_DISPLAYABLE_FRAGMENT with PRIVATE_OR_SANITIZED_KEY omission; no refresh or
alternative access was used to bypass this retention. The archived AST node
is observed; independent parser-input binding remains unestablished.

## Existing checked hooks examined

CastData schema has kind/operand/ty; ghostGenericArgList belongs to FnCallData.
Ghost generic arguments bind the later call, not the preceding cast. let_lft
can create a named lifetime but does not replace this generated unnamed
InferredTypeExpr. No existing cast-target ghost annotation/ascription hook
was found in frozen preprocessing/translation. Replacing the runtime expression,
using arbitrary static lifetime, globally permitting inferred casts, assuming
an ownership bridge or weakening posts is outside the accepted correction.
No safe proof-only correction is established.

## Minimal proposed scope, BEFORE implementation

Authorize a separate reviewed profile only for a checked, source-bound lifetime
ascription on the **implicit mutable array-reference to same-element slice-reference
coercion** at this wrapper node. The ascription must name an existing checked
lifetime with a real ownership/borrow relation; it must not manufacture resources
or choose static. Validate exact source/MIR cast kind, mutability, source array
length/element, destination element and lifetime, and reject all mismatches.
Prefer an explicit narrow annotation over a general inferred-type exception.
The exact implementation diff depends on confirming the decoded cast kind and
existing representation; this is a scoped design proposal, not a ready patch.

**Admission gate:** before allowing this cast, establish slice metadata fidelity.
Frozen checker5551 treats casts from definitely sized pointees as Upcast;
evaluator8633 returns its input unchanged. Array-to-slice length metadata is
not constructed visibly on this path. This is a source-level risk, not an
observed subsequent failure. If existing representation cannot justify it,
stop and seek a separate model decision; do not smuggle a metadata/kernel/model
change into lifetime handling. Existing frozen profile remains the baseline.

Required controls: exact array3/u64 positive; wrong mutability, element, length,
lifetime/region, cast kind and source identity negatives; no permission from
numeric pointer equality; preserved provenance, physical owners and slice
length; rejected unsupported casts remain rejected; normal false/true/first
Continue-panic full CURRENT posts then all resource/admission/HRTB/unwind/
late-Cleanup/default-off/B1/helper/receiver/end/retirement gates. Source/runtime,
cut and contracts unchanged. Independent Luna High GO and exact new reviewed
profile/pins before authorized Cloud execution. No local proof execution.

The separate guard continuation proposal does not repair this prefix coercion.
No new Build, proof credit or B2 closure results from either proposal.


## v0.10 follow-up: direct MIR observations, 2026-10-19

Assignment HEAD52da95cb retains T0/main/absolute and frozen tool. Read-only
continuation began19:46:16Z, after main19:39:27Z; no new experiment, proof edit
or Build. Literal Locators are available now; the earlier deferred-feature
statement is historical. Existing AST/source observations were reused.

Catalogue selected exact **prefix** decode.out in old Build5f668cd9:
file ID7decbe12be84eeb9ce03066a786554e0d80548f8d6e82b2b8a00d6e6ae15c179,
SHA70be7daa815fd80ad8f921b1da2984e3cc64d258a7a0c625d59958b82518723c,
archive8ffe3689…/index3e3e6bad… . This identity is separate from R2 fullbody AST.

Addressed observations, not an automatic MIR parser run:

| Archived MIR coordinate | Observation | Binding/limit |
| --- | --- | --- |
| as_mut_ptr locator455701 / line12519 | One exact match, whole-file complete | Call anchor only; proximity alone does not bind a cast |
| source214 near locator |12 exact matches, scope451605–459797 | Source-token candidates, no invented node ID |
| [12428–12439](R3-MIR-CAST-ASSIGNMENT-20261019.json) | Source-end line214/col.pos22; assignment lhs local_4; rhsRvalue.cast | Actual syntactic containment of assignment/cast start |
| [12438–12449](R3-MIR-CAST-OPERAND-20261019.json) | cast operand.move.local_5; projection=[]; target.ref.region.id="\'<erased>" | Erased target region is now directly observed |
| [position453273 ±256](R3-MIR-CAST-FRAGMENT-20261019.json) | target slice(uInt(u64)), mutability.mut; kind.pointerCoercion=void | Exact target/cast tail; no full source LocalDecl type |

These fragments overlap at the named assignment/cast field and delimit its
operand/type/kind structure; the link is stronger than text-nearest selection.
Translator local-name mapping2030 tags internal _4/_5 as $_4/$_5, matching
AST895's destination/source, target and source214 end. This is a source-linked
structural comparison; full enclosing body identity/span and source LocalDecl
_5 type/region/array3 have not all been directly observed. Array3 is established
in the pinned Rust/AST wrapper, not a separately retrieved MIR LocalDecl fact.
Generic parser_input_binding=NOT_ESTABLISHED/causal_status=UNKNOWN stay intact.

The exact cast **category** is pointerCoercion. Exporter lib.rs2724 encodes
`mir::CastKind::PointerCoercion { .. }` as `set_pointer_coercion(())`;
schema vf_mir.capnp598 stores Void. Its Rust coercion subtype is discarded.
Therefore **Unsize is not directly observable in this frozen decode.out**.
The proposed exact-kind gate cannot pretend otherwise: either justify a narrowly
source/type/identity-bound admission using available fields in a separately
reviewed design, or seek an explicit exporter/schema scope decision to preserve
the subtype. No serializer change was implemented.

Wrapper-name locator429590 found one match; near `name = "_5",` returned
NO_MATCH_IN_SEARCH_SCOPE, not declaration absence (LocalDecl schema actually
contains nested id.name). Corrected schema-based `id = (name = "_5")` was rejected
with BUILD_QUERY_BUDGET_EXCEEDED, request3ad9f013b459fc6500454d8a3441fa54897f28f48cb19874086e129629f60966.
No scope/offset walk, alternate archive, quota reset or new Build followed.
Nine v0.10 MIR queries were delivered before the quota rejection; three returned
bounded text (two12-line windows plus512codepoints), six coordinates/search-only.
Historical/shared reservations also count; no claim of exclusive quota ownership.

Administrative bounded projection requested: LocalDecl_5/_4 within
b2_three_from_local, complete types/regions/array length, enclosing body/source
span and cast assignment relation. Existing verified fragments need not be
repeated. The lost PointerCoercion subtype is a serializer limitation, not a
field an administrator can recover from this decode.out.

## Metadata gate: source evidence and minimal reproducer proposal

Frozen prelude_core.rsspec71–95 models pointer(provenance,address,metadata),
ptr_len reads metadata, and strip_pointer_metadata preserves provenance/address
while replacing metadata. Mutable slice ownership uses
`array(strip_pointer_metadata(l), ptr_len(l), elems)` in translator1259–1352
and prelude462–469. Static arrays are sized and slices unsized (checker4428–4446).
The sized-source pointer/ref cast5551–5564 becomes Upcast, evaluated as identity
at8633. No length3 construction has been established for this exact coercion.
This does **not** prove an observed later failure or that every input pointer
has empty metadata; actual allocation/source-reference route still matters.
It does establish that lifetime acceptance alone is insufficient justification.
No new model fact, pointer equality bridge or numeric-address rule is admitted.

Minimal isolated **future Cloud** reproducer proposal (not implemented/executed):

```rust
unsafe fn array3_slice_probe(values: &mut [u64; 3]) {
    let view: &mut [u64] = values;
    assert!(view.len() == 3);
    let _p = view.as_mut_ptr();
}
```

Supply real checked array-cell/borrow/lifetime resources, full normal/unwind
resource-return posts and unchanged compiler/profile source identities. First
run frozen baseline to locate the same erased-lifetime blocker. A separately
approved candidate may proceed past it only while checking length3, pointer
provenance/address and physical cell owners, then the real as_mut_ptr call.
An explicit wrong-length assertion must fail at that assertion after successful
setup; wrong lifetime/mutability/element/source/cast-shape controls must fail at
intended admission gates. This diagnostic is not the actual prefix theorem and
cannot replace false/true/firstContinue-panic/full CURRENT mandatory matrix.
Any necessary metadata construction is a separate trusted/model decision,
not part of a silently broadened lifetime patch. Current recommendation: no
lifetime-only implementation/Cloud candidate until this gate is resolved.


Additional pinned-source constraint: AddressOf(Var) at checker4982–4988 returns
the existing WVar, and its evaluator8563–8568 reads env[x]; neither constructs
slice metadata. assert_mk_pointer6779–6781 sets metadata_none for Rust sized
pointees, with get_unique_var_symb_6784–6789 applying it to pointer/ref symbols.
Applicability to the exact _5 binder is still conditional on the missing local
and environment binding; do not report metadata_none as directly observed here.
This strengthens the need for the requested source-local projection and a
separate checked metadata reproducer. Independent Luna High read-only source
investigation found the same open gate; no trusted patch was implemented.
