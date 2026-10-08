# M2 callback admission matrix — design before implementation

This work evaluates the already pinned experimental `callback.patch` shape and
the existing HRTB equality registration rule. It introduces no new patch,
axiom, ownership assumption, compiler rule, or proof summary. The profile stays
experimental until the owner reviews fresh hosted evidence and the remaining
M2 proof obligations.

## Trust boundary

The tool source is VeriFast 26.10 commit
`f76012fb518703b1d98e243ac4f487f16877cfcb`; the callback parser/translator
patch is `callback.patch` SHA-256
`0a006df94f04d6425d70280967d6652bdd33ccb88ead4a44f02a2e36775aaa5e`; its
prelude baseline is SHA-256
`d7058d43557a2b5147eb1377e85bb67d04b94c83594b6c1c27650c9c571841b5`.
Exporter, schema, kernel, refiner, runtime source and Rust signatures remain
the hosted profile pins. Invalid tuple declarations are produced only by
copying the complete built tool home into a fresh disposable directory and
changing one exact `std_tuple_2_` declaration there. No other installed file
may differ. The unchanged `tuple2_field_resources` source remains the valid
control for every declaration-shape probe.

Tuple shape controls ask whether the parser rejects variants of the generated
tuple-2 declaration at the dedicated
`Parse error: std_tuple_2_ ownership expansion requires the pinned two-field tuple shape`
error. The valid baseline must pass the complete body, normal return, leak,
source-integrity, export/decode and refinement gates. Invalid controls require
the exact parser error, successful export/decode/refinement, unchanged fixture
bytes, and no entry into the marked body. Separate resource cases retain full
normal and unwind ownership posts while targeting missing first/second field
ownership, wrong field thread/value and frame loss. Each negative must execute
its own body and fail at its intended resource obligation.

HRTB controls use compiler-origin bounds and actual `FnMut::call_mut` sites.
Their certificate binds the named source function, `F`, `T`, associated output,
bound regions, call source location, registration bit, and AST registration
node. Positive Boolean/equal-lifetime cases require registration at every
eligible call. Wrong function, referent, output, lifetime, missing source
bound, and sibling-body bound cases require no registration at the marked
call. These are admission certificates only. If later resource verification
fails, report the admission status separately and leave proof status
`INCONCLUSIVE`; never count registration as a proof negative or proof pass.
Resource-bearing HRTB inputs retain complete normal/unwind posts.

## Outcome classes

- `PASS`: exact valid tuple body and all existing positive gates pass.
- `EXPECTED_SHAPE_REJECTION`: exact parser diagnostic on the exact declaration;
  exporter/decode/refinement succeed and the fixture body was not entered.
- `EXPECTED_RESOURCE_REJECTION`: exact intended resource obligation rejects
  after the case body executes; all other stages and source-integrity gates pass.
- `ADMISSION_CERTIFICATE`: exact HRTB source-bound/call/AST evidence matches
  its predeclared registration expectation. A separate proof result is always
  retained.
- `INCONCLUSIVE`: any setup, unrelated parser, unsupported, stage, source,
  body-entry, missing-evidence or full-post mismatch.

Classifier mutations must reject wrong shape location/message, altered stage or
source, body entry on a parser rejection, missing body execution on a resource
negative, and wrong/missing/extra HRTB bound, call, output, lifetime, AST node
or source location. A green tuple fixture, parser rejection, or HRTB
registration certificate alone proves neither the soundness of the patched
front end nor actual merge callback resources.

## Fresh-evidence boundary and remaining M2 work

Run 37711781188 provides a full positive tuple-2 body and one missing-second
field diagnostic. Its HRTB logs show two exact registrations for
`hrtb_bool_common_lifetime_two_calls` and unregistered mismatch controls, but
the HRTB body proofs remain inconclusive at earlier aliasing/resource
obligations. These historical records are calibration only; this classifier
must use fresh exact-SHA hosted artifacts.

Still open after admission classification: justify the limited tuple ownership
expansion, prove full real-resource callback normal/unwind posts for unrestricted
`FnMut`, and complete source-linked `merge_up`/`merge_down` integration. Do not
weaken posts or treat registration/parser outcomes as evidence for those goals.

The first executable classifier component is intentionally limited to tuple-2
declaration admission. `m2-admission-prove.py` runs the unchanged full-body
tuple-2 positive control, then tests renamed/reordered generic parameters,
reordered/missing/extra fields in fresh complete tool-home copies. It reports
only exact parser-shape rejections with passing export/decode/refinement,
unchanged source and no body entry. The pinned parser constructs every tuple
field as `Public`, so a visibility negative cannot be expressed by changing
only a prelude declaration through that parser. This shape-only component does
not complete the whole M2 matrix; the resource and HRTB certificate extensions
below cover separate dimensions and retain their own evidence gates.

## Resource and HRTB certificate extension

`m2-resource-cases.rs` adds one full positive tuple ownership/frame case and
separate missing-first-owner, wrong-thread, and wrong-value tuple controls.
Each carries current-thread, both field ownership, and frame obligations in
both normal and unwind posts. Run 37715432190 calibrated the three tuple
negatives at the exact field-zero diagnostic in `bin/rust/prelude.rsspec`
(15,8-20), after the intended body close executes, with stages 0/0/1/0. The
frame-value assertion reaches `verified/lib.rs` (28,23-26) with exact message
`Cannot prove 41 == 73`, stages 0/0/1/0, and three body executions. The fixture
now records that exact `EXPECT_REJECTION`; it must be reconfirmed against the
new fixture SHA before it counts. The positive uses a body with no panic or
callback, so its full unwind post is a contract check rather than evidence of
unwind-path execution.

`hrtb-admission-certificate.py` reads the callback and prepared-HRTB artifacts
from one hosted evidence root. It cross-checks the recorded source fixture,
decoded MIR bounds/output, `MERGE_HRTB_BOUND` and `MERGE_HRTB_CALL` records,
call substitutions and locations in `proof-ast.ml`, every stage's source
integrity and exit record, and full artifact hashes. Its matrix requires the
exact two-call Boolean case to register twice; wrong output, unconstrained
output, one-region bounds, wrong ghost F/T, unequal ghost lifetimes, and a
sibling-body bound each have an explicit expected registration result. The
prepared resource cases are certificates only: their proof classifications
are copied separately and remain `INCONCLUSIVE` unless their own full proof
gate says otherwise. The prepared missing-comparator-owner case is excluded
because its normal and unwind posts are `true`.

The HRTB certificate harness in run 37715432190 stopped on a classifier
mutation attempting arithmetic on the registered-marker schema's absent
`eligible_n` field. That field is only logged for unregistered calls. The
classifier now mutates registered records to a forged numeric count and flips
the explicit unregistered count, while the positive registered case derives
its single eligible bound only when the exact source-bound record and decoded
MIR clause both match. The run's original proof outcomes remain inconclusive.

Hosted run 37713243201 currently records two registrations at the Boolean
two-call fixture's distinct source locations and one at the prepared positive;
the wrong ghost-F/T, unequal-lifetime, output, and body-scope controls record
the expected zero-registration locations. Every sampled HRTB proof remains
`INCONCLUSIVE` at earlier resource/aliasing obligations. These artifacts
calibrate the certificate fields, not its fresh-run acceptance.

Neither tool invokes compilation, VeriFast, decoding, or the refinement
checker. A certificate records only source-bound and translation admission
evidence; it never reclassifies an unrelated resource/setup error as an
intended proof negative or accepts a registration marker as a proof result.
