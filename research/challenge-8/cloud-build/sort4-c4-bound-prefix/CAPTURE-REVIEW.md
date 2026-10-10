# C4 capture exact-delta review

**Conditional GO for the capture-only step after a full C3 verdict and the
gate corrections below.** The capture profile is correctly marked
`profile_accepted=false`, `actual_sort4_callable_summary=false`, and
`dispatch_authorized=false`. It must remain un-dispatched until C3's positive,
all required controls, and independent raw-result review establish the full
C3 verdict. This review did not touch Build3 or run compiler, exporter,
verifier, or proof tools.

The delta is pinned to the C3-bound translator
`d2f132148d409eb9a9e27afd24603d992405ec1984849817da9e427ab070db6e`, patch
SHA-256 `364b52d9291b06c9dbc8daa8ff5770bd08eb8171cc2c2d4ab28e8e5ac10adc60`,
and expected output
`7361f1c26af1db68d3f172e9124d3a74c2d5ea8415a7edcc4164d43ffdcfc5b8`. The
patch changes only `vf_mir_translator.ml`. C4 opt-in defaults off; the new
capture gate rejects C3 bound/capture, C2 bound/discovery, C1 prefix mode,
non-strict settings, and active C1/C2/C3 controls. The existing C3 bound and
capture modes also reject a simultaneous C4 capture. The named-lifetime parser
requires exactly one each of `cmp2`, `cmp3`, and `cmp4`, validates their parsed
type-id/witness declaration shape, and requires ordered cuts
`'cmp`, `'cmp2`, `'cmp3`, `'cmp4`. The C4 branch checks the `sort4_stable`
target, isolated single-body/full-unwind conditions, serializes the full
original AST, and then deliberately raises
`SORT4-C4-CAPTURE: FULL_ORIGINAL_AST_CAPTURED_NOT_PROOF`.

The driver starts from the fixed C3 annotated source hash
`087123b12072a19b0490260e509ce6773c1ed3dce0ed7c14c95991fdaf82996e`, inserts
the C4 annotation exactly at the unique unchanged `let c4 = is_less(&*d,
&*b);` line, and checks ghost stripping against the original source before
writing the fixture certificate. The annotation keeps `(d,b)` order and adds
only ghost lifetimes/contracts; the unchanged call is the fourth callback.
The profile expects a new source hash from Cloud, a new complete normal and
readonly MIR pair, and a fresh pre-AST; the C3 local numbers are not reused.
The driver confirms C3 positive replay and mandatory unbound-C3 refusal with
C4 capture mode off before exporting the new C4 MIR and invoking the
intentional refusal. All stage records label `proof_credit=false` and the
capture result initializes `target_proof=NOT_RUN`.

Two guard gaps must be closed before dispatch. First, the profile's
`dispatch_authorized=false` is not checked by `driver.run`; it checks only C3
`positive_ok`/zero exit. That is weaker than the required full C3 verdict,
because the C3 result can be a positive candidate while its C1/C2/C3 controls
still await first-VC raw review. Require an explicit authorized/full-verdict
gate (for example, a separately recorded all-controls-reviewed result) before
calling C4 `prepare` or running any C4 capture stage. Second, the driver accepts
the C4 refusal when its expected fatal appears and the pre-AST exists, but
doesn't verify that the log contains no `Verifying function 'sort4_stable'`
entry. Add that absence check before classifying the capture as
`FRESH_C4_SOURCE_MIR_PREAST_CAPTURED_REFUSED_NOT_PROOF`; otherwise the
`NOT_RUN` field is asserted rather than checked.

The snapshot check is currently before/after the C4 translator patch/build in
one invocation. It protects frozen non-translator inputs during that build,
but it does not compare the pre-C4 snapshot to the saved C3-bound snapshot. At
dispatch, compare those frozen fields to the completed C3 run as well, or
record the independently checked match. `bin/verifast` is expected to rebuild;
all other binaries, critical files, effective RSSpecs, proof-std inputs, and
repository HEAD must remain equal.

With those guards, the capture-only source/MIR/pre-AST step is in scope after
the full C3 verdict. Its result must remain NOT_RUN/no-proof-credit and must
not enable C4 bound projection by itself. A later C4 projection requires a
separate fresh correspondence/allocation review and same-version selected
helper proof; no C4 normal/unwind, C5, select, copy, or whole-function result
is implied here.

## Follow-up gate review after C3 Build3 raw verdict

The current `driver.py` closes both previously identified gaps. Before any C4
patch or build, it now requires `dispatch_authorized=true`, the exact
`INDEPENDENT_RAW_REVIEW_PASS` verdict, a fresh-review filename matching the
pinned format, and a review file containing the exact Build ID whose SHA-256
matches the profile pin. It also requires the C3 zero-exit positive and exact
annotated-source certificate; the complete expected control-name set with
each control reaching the target before its first error; a source mutant with
zero target proof entries; and equality between the current tool snapshot and
the saved C3-bound snapshot. The capture classification also checks the raw
log has no `Verifying function 'sort4_stable'` entry before assigning the
intentional refusal/NOT_RUN result.

Independent C3 raw review is recorded in
`../sort4-c3-bound-prefix/FRESH-A956B0B2-REVIEW.md` for Build
`a956b0b2-4e05-4c19-90b4-408f381ba1fc`. **Conditional GO for this C4
capture-only diagnostic** once the coordinator records that exact C3 verdict,
Build ID, and review-file SHA-256 in `capture-profile.json` and explicitly
sets `dispatch_authorized=true`. At review time the profile still has
`dispatch_authorized=false`; no dispatch is authorized by this note alone.
The C4 capture remains only a fresh source/MIR/pre-AST correspondence step,
with no proof credit or C4 projection admission.
