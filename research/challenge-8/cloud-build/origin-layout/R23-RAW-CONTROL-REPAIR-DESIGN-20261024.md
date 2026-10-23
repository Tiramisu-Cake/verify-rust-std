# R23 raw-control repair — design before semantic edits

## Defect and applicability

The R23 P3 Evidence Brief reports the unsupported-index RawPtr control as
INCONCLUSIVE at the refiner stage. The verified program changes a whole-array
RawPtr place into an indexed-element RawPtr before the point where the
refiner compares the two MIR command streams. The observed stage result
therefore does not isolate the intended unsupported projected-place rule.
Changing only the control's original source to the exact indexed variant is a
source-pair alignment fix; it does not claim that the rule accepts the
projection.

The R19 synthetic F5 resource negative reaches its exact resource error at
the intended line, but the classifier reports a missing caller-call trace.
The bounded P3 Evidence Brief query `8639a5a375d1c89f8b0933bd77f4e4627a13a3c738fcdf9b4300f9d906324c27`
(located verifier trace in file `bb9085752d83266a92da8f4e4242338027041867adfc4eab055664729aedc8e1`,
SHA-256 `3818525fa6b6d57654b939c6f035eb81b83467444718af1cdef6a8688e701de8`)
shows `insert_tail` at source lines 2–21 and the panic call at
`core/src/panic.rs(52,9-51): Verifying call`. This is the `core::panic!()`
macro definition span, not the synthetic source's panic line. So accepting a
second trace spelling alone cannot fix the source-bound callee-call check.

The synthetic fixture now spells the already checked panic callee directly as
`core::panicking::panic("explicit panic");` in both original and verified
units and enables `#![feature(panic_internals)]` in both crate headers. The
pinned standard-library specification already provides the function's checked
string-bytes precondition and never-returning normal contract; no new summary
or premise is added. The macro's definition calls this same function, but
accepting an arbitrary macro-definition span is rejected because it is not
bound to this source target. This fixture rewrite only changes the synthetic
always-panicking callee; it does not change the actual std body, actual caller,
or posts.

## Invariants and gates

- Keep every existing R17 case's source pair unchanged except the
  `unsupported_index_projection` original, which must become byte-identical to
  that case's verified indexed variant. Preserve its unique source target and
  all diagnostic, local-pair/context, source hash, and stage gates.
- Keep every existing R19 source, classification, stage, exact resource error,
  target execution, ordered unique caller/callee header, and cleanup control.
  The call-trace predicate remains bound to the recorded source call line and
  only to its caller body segment. Permit exactly the long and short native
  wording; do not accept target inference from the error alone.
- Negative synthetic checks reject a wrong function, wrong source span, absent
  call trace, missing callee, or unrelated error. Preserve all existing
  R19 normal, unwind, Drop, and Resume controls.
- The synthetic F5 result remains a source-reported historical INCONCLUSIVE;
  this classifier repair does not rewrite or reclassify that receipt. All
  results remain diagnostic-only with no proof credit.

## Cause versus hypothesis

The R17 source-pair divergence and its earlier-prefix consequence are directly
visible in `_original_source` and `_variants`; this is the source-level cause
of the observed premature mismatch, subject to the existing source/stage
binding gates. The R19 parser accepts only the two native call trace wordings
at the exact synthetic source call lines. The Brief directly establishes the
macro expansion's different source span; the direct fixture call makes the
synthetic panic call span source-bound. Whether the R19 caller call trace was
present in P3 remains under Brief investigation. Neither this fixture change
nor trace parsing retroactively accepts that historical result.

## Validation

Run focused synthetic/static service tests, Python compilation, and scoped
diff checks only. Do not run a compiler, verifier, source preparation, or Cloud
job; do not change evidence receipts.
