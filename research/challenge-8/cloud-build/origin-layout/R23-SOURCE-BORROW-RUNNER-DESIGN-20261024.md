# R23 source-borrow runner wiring — design before implementation

## Defect and applicability

The two owned-NLL cycles did not establish a usable body/location mapping for
`b2_three_from_local`; the caller's `values.as_mut_ptr()` to `insert_tail`
path still needs an exact checked source-level route. This runner addition is
applicable only when the selected profile contains the explicit
`r23_source_borrow_registration` field and the admitted, unmutated full-body
parent, its source pair, and its stage receipts pass the existing exact gates.
It is a new diagnostic case and does not claim proof credit.

## Construction and source gate

Build one `r23_source_array_borrow` case from the already admitted full-body
parent. Reconstruct canonical source/runtime and actual `insert_tail` identities
through the existing pinned source module, parent preparation record, and
parent original/verified hashes. The original unit retains the parent's
canonical caller and actual callee. The verified unit is deterministically
reconstructed by adding the checked R20/R23 helper text and the R23 ghost
lifetime envelope around the one original `values.as_mut_ptr()` statement and
actual call. The runtime helper `r23_checked_slice_as_mut_ptr` is byte-identical
in both units and implements the exact two-cast projection; helper contracts,
array/slice conversion lemmas, and the template are separately hash-pinned.

Before dispatch, the gate checks exact expected case/parent paths, complete
parent identity and admitted source/stage receipts, complete deterministic
source bytes and hashes, the single canonical array/pointer/callee markers,
unchanged original runtime/posts, helper/template digests, and that the helper
runtime is identical between source units. After dispatch, preserve the
existing stage receipt/source-hash gates and require exporter, decoder,
refiner, and verifier all exit zero without errors/dead-code, with all three
verifier targets (`insert_tail`, `b2_three_from_local`, and
`r23_checked_slice_as_mut_ptr`) observed for the positive classification.

## Dispatch and invariants

A separate `source_adapter_eligible` argument defaults false at both runner
and diagnostic boundaries. Dispatch copies its environment, strips inherited
`SMALLSORT_R23_SOURCE_ARRAY_BORROW`, and sets it only for the exact registered
new case. Capture remains disabled by the existing post-stop-loss policy. The
normal campaign and every existing control keep their existing dispatch and
classification paths. The new diagnostic runs after full-body admission and
before raw-pointer/control matrix dispatch; if registration is absent it is
reported as not applicable without preparing or running the case.

The existing original `values` initialization, `as_mut_ptr()` expression,
actual `insert_tail` invocation, standard-library body/signature, wrapper
runtime, and normal/unwind posts remain unchanged. The annotations preserve
physical array ownership and element owners through checked Array/slice content
conversion, scope the slice borrow to the original call, and restore the same
array resource with the established normal/unwind cleanup protocol. No NLL
facts, address-only bridge, assumed callee contract, model premise, runtime
call insertion, or control removal is introduced.

## Controls and validation

Keep all existing source, stage, classification, runtime, proof, and negative
controls intact. Static service tests exercise deterministic prepare/source
validation, positive dispatch eligibility, inherited environment removal and
caller-environment preservation, absent registration, corrupted/missing
parent/helper/template/source receipts, and three separate source-pair controls:
missing end marker, duplicate begin marker, and wrong logical-lifetime binding.
Those controls must reach their exact intended frontend refusal; before the
source/stage gate they remain inconclusive. Tests also cover
error/exception/timeout/partial/missing/null/wrong-type/NOT_RUN/stage mismatch
classification. Tests use synthetic temporary source and runner results only;
no compiler, exporter, verifier, or Cloud call is made locally. Every result
remains diagnostic-only and Cloud-unverified.
