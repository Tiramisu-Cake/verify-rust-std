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
No direct MIR region observation has been obtained.

Frozen verifast1.ml4909 checks CastExpr target using strict check_pure_type;
RustRefTypeExpr2223 checks its lifetime child; InferredTypeExpr2242 invokes
report_inferred_types_as_error2252 with the exact diagnostic/location.
Translator3777ff translates MIR CastData.ty into this CastExpr; reference
translation1541ff uses vf_ty_arg_of_region568ff, whose erased-region case
produces InferredTypeExpr. Thus erased MIR region is the supported translator
explanation, **deduced from source**, not a directly observed MIR field.

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
