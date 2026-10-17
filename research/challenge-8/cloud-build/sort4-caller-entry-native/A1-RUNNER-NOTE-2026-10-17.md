# A1 first-matrix runner checkpoint (UNRUN / NO-GO)

`a1-runner.py` remains an import-inert Cloud-only checkpoint. `run(a)` checks
the exact phase, provider, opt-in, workspace, published profile and proof/infra
pins, then emits a preflight record with `dispatch_ready=false`. It does not
reconstruct a tool, invoke the compiler or verifier, create an admission
record, or publish a receipt. The 26 matrix rows are enumerated, but their
expected classifications are never copied into observed records.

The staged functions now provide concrete source-only and observation hooks:

- `load_pinned_helpers` requires a complete exact SHA256 map before importing
  any A1 helper from the proof checkout.
- `prepare_source_fixtures`, `prepare_off_fixture`, and
  `prepare_legacy_fixtures` create byte-bound source pairs from the certified
  A1 package and pinned existing fixture producers. The five positive A1
  cases must share identical source bytes.
- `prepare_synthetic_inputs` derives seven isolated controls, including two
  separate N-clauses mutations, from one *actual* paired decoded VfMir input.
  `prepare_admission_control_inputs` writes wrong-certificate, wrong common
  binding, and forced-legacy redirect inputs. These are inputs only, not
  observed refusals.
- `materialize_expected_cases` binds all 26 expected source and unit IDs to
  produced bytes before constructing `A1Admission`.
- `collect_source_case` joins the paired compiler inventory, final AST native
  posts, MIR call binding, one same-invocation focused verifier diagnostic,
  and a candidate classifier. `select_focused_body` requires exactly one AST
  definition in the compiler `Body.span` interval selected by the actual
  `-focus` line. Body and caller focus use `Body.span.lo`; native post
  diagnostics use the separate `fnSigSpan.lo`.
- `attest_focused_execution` is a runner inference only after exact frozen
  focus/kernel source hashes, one compiler-bound interval, a same-invocation
  VF0 or intended diagnostic, and the complete native AST structure gate.
  It explicitly sets `proof_credit=false`.
- For N-default-contract and N-freeze-contract, a matching `fnSigSpan` failure
  may occur during header compatibility before body checking. The attester
  requires the *same first error's* source-located `Verifying function
  '<numeric alias>'` context frame at compiler `Body.span.lo`. The pinned
  kernel enters this frame only after prototype compatibility returns; the
  final console emits the context after the fatal symbolic error. Missing,
  duplicate or mismatched frames yield no body-count or reached attestation.
  The classifier must first report `error_context.stage=impl-body` with no
  header frame; the runner's parser is an additional consistency gate.
  This text-format gate is still untested on an actual Cloud verifier result.
- `publish_positive_threshold_receipt` drafts the two-current-body admission
  lifecycle and binds the receipt to the same exact verified/original pair and
  compiler observer focus. It is unreachable from `run` and has never been
  exercised on compiler output.
- `draft_positive_receipt_stage` joins these producers against one supplied
  final tool: P0a and P0b must both finish VF0 and the native-post gate,
  synthetic/control/legacy/OFF input IDs are then materialized, only then is
  the two-body receipt admitted, and P0c must finish on the same source pair.
  This function is deliberately unreachable from `run`; it emits no full
  matrix row or independent proof credit.

The remaining mandatory integration is substantial. The runner must execute
and classify every 26-case row, including isolated decoded-message injection,
the original P1 interface, OFF default behavior, fresh R1–R7, and actual
N-source/N-binding/N-redirect refusals. N-false31 changes verified bytes, so
it requires fresh focused proofs of *both* threshold bodies and native
conformance for that exact pair before its caller receipt. A positive-pair
receipt cannot be reused. The full source/AST/diagnostic attestation and final
profile/helper pins also require independent review. Until those hooks exist,
the first matrix stays **NOT_RUN / NO-GO**; a shaped service record or AST
alone cannot substitute for backend facts.

The first concrete structural blocker is P1's **full** `small_sort` interface.
The current AST gate checks the threshold contract and the common call shape,
but does not bind the decoded required-method `Self,F` and three scoped input
regions, full clauses, and both actual `small_sort` Body signatures to the
common prototype and numeric implementation ASTs. It also does not compare
their entire native pre, returning, and unwind trees under a scoped positional
alpha map. The internal R side record is not itself an external AST
observation. No P1 service row or common small_sort summary can be claimed
from the present threshold-only gate.

The draft repeats paired export/decode/refinement per positive focus. The
900-second shared Build deadline could expire before all 26 rows. A cache is
admissible only for an exact verified/original pair, final tool bytes and the
same Build, with each focused verifier invocation still separate. No such
reviewed paired-support cache is implemented here.

Only static parsing, eleven isolated synthetic AST parser tests, and four
synthetic focused-error context tests were run
locally. No compiler, exporter, verifier, proof, Cloud Build, coordinator, or
raw evidence was invoked or read.
