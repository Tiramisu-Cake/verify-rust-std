# HANDOFF — re-review of issue #5206 fix revision

**Verdict: APPROVE.** R1 and R2 from the previous review are resolved
correctly. No further source or test changes are required by this static
review. Native validation remains outstanding; this is not a test/CI pass.

One coordinator stage complete; stop with this HANDOFF. Review performed
directly in the assigned review session, without helper delegation. Candidate,
author packages, previous review and upstream state were left unchanged.

## Reviewed identities and scope

- Candidate: `/root/kani-fix-5206-w13`, branch
  `fix/stub-contract-target-conflict`, clean HEAD
  `a5ebb0bf8ac2ad141f7e8f173ae5e8548948b097`.
- Its sole parent is the previously reviewed fix
  `e58623967899e51f9716bdb1d76b8d5bf7f80944`; that commit's sole parent is
  base `0997d11c14cb2da0824efc34e2c4001e53ac0faf`.
- Candidate tree: `798c53188fd806e6684ce71844fd7d8b62c572ec`.
- Both fix commits have author and committer
  `Tiramisu-Cake <igkharin@gmail.com>`.
- Inputs: [previous review](../issue5206-fix-review/HANDOFF.md),
  [revision package](../issue5206-fix-r2/HANDOFF.md) and its
  [PR draft](../issue5206-fix-r2/PR-DRAFT.md).
- Revision: exactly three files, 33 insertions and 2 deletions: the stubbing
  module and the existing positive `.rs`/`.expected` pair. Combined with the
  first commit: exactly five files, 105 insertions, comprising the module
  and the positive and negative test pairs. No dependencies, transformation
  code, macros, runner or other source files changed.

## Findings resolved

**R1 — positive coverage: resolved.**
`tests/expected/function-contract/ordinary_stub_different_target.rs:29`
adds `stub_verified(h)` alongside `stub(f, g)`. Its `assert!(f())` is
discriminating: the original returns false and the replacement returns true.
Dropping the ordinary stub therefore fails this harness even if the verified
contract for `h` works. A regression rejecting all ordinary stubs on a
verified-stub harness also prevents the required successful completion.

Lines 37 and 43 add reverse-direction cases under both contract attributes:
the target is `h`, and `stub(g, h)` uses it only as a replacement value.
Checking map values as conflicting targets would wrongly reject these
harnesses. Both call only `h`; neither `h` nor the harness calls `g`, so the
cases test acceptance without requiring the separate #5204 replacement-body
fix. `check_reverse_contract` supplies the corresponding proof of `h`'s
contract. The original `check_caller` control is preserved byte-for-byte as
part of the original source prefix; it still requires `f -> g` to establish
`caller`'s postcondition. All four harnesses have name expectations, and the
summary now requires four successes, zero failures, four total.

**R2 — repeated verified-target diagnostics: resolved.**
`kani-compiler/src/kani_middle/stubbing/mod.rs:55` applies
`unique_by(|target| target.def_id())` to the resolved verified-target vector
before checking conflicts. This deduplicates function identities, including
different paths to the same function, rather than textual spellings. It
uses the already imported `Itertools` and existing dependency.

For each selected harness invocation, the new conflict diagnostic is emitted
once per conflicting resolved target and attribute kind. The optional
`proof_for_contract` target is checked once first; verified targets follow
in first-occurrence order. Deduplication is confined to `stub_verified`, so
it does not collapse different attribute kinds or different target IDs.
`KaniAttributes::for_item` preserves the compiler attribute sequence within
each kind, and the interpreter preserves that sequence; `unique_by` yields
the first occurrence and uses its internal hash set only for membership.
It does not iterate a hash set to emit diagnostics.

This establishes deterministic order **within a harness**. The existing
`group_by_stubs` iteration over the harness HashMap at
`codegen_units.rs:250` does not promise a global diagnostic order across
harnesses. The revision leaves that behavior unchanged; the expected files
correctly do not impose global order. Existing duplicate-attribute warnings
and other pre-existing errors are outside the count of new conflict errors.
The returned stub map, conflict predicate, wording, spans and validation
placement remain unchanged.

## Compiletest semantics and regression strength

Rechecked `tools/compiletest/src/runtest.rs:488,528,564,590`. Both suites use
expected mode and read sibling `.expected` files. These files contain no
continuation backslashes: each trimmed line is an independent, unordered
literal substring requirement in combined stdout/stderr. They are not regexes
or exact transcripts. The driver emits the expected harness announcements
and summary format at `kani-driver/src/harness_runner.rs:273,339`.

The positive fixture's four-success summary excludes a missing, rejected or
failing harness even though its single `VERIFICATION:- SUCCESSFUL` pattern
alone would not prove all four succeeded. The normal suite invocation does
not require a successful exit separately; the output requirements supply
the relevant success oracle here. A one-harness run or three successes with
one failure cannot satisfy the expected summary.

The negative pair under `tests/ui/function-contracts/` is byte-identical to
the reviewed parent. It still requires both complete public conflict texts
and the two-error abort line; a missing/wrong diagnostic or four-error abort
fails. The qualified `crate::f` identity case and the proof harness needed
for the verified target remain present.

There is no new duplicate-annotation or ordering regression fixture. The
unchanged negative fixture contains no repeated verified target, and the
matcher does not count diagnostic occurrences or enforce their order. Thus
deduplication/order are approved by source inspection, not claimed as tested
regression coverage. This is a coverage limitation, not a new correctness
finding; the previous review did not require a duplicate-target fixture.

## PR draft and upstream history

The draft accurately describes the conflict predicate, resolved identities,
pre-transformation diagnostic, retained different-target behavior and
verified-target deduplication. `Resolves #5206` remains appropriate. Its
Testing TODO accurately distinguishes static checks from unrun native
tests/CI and includes both kinds of positive controls. Replace that TODO
with authorized results before publication; no fresh main/fix or #5204
combined runtime validation is established by this review.

The following lines each occur exactly once and match byte-for-byte both
the original draft and the existing `pr-5195/PR-BODY.snapshot.md`; the
license also matches Kani's `.github/PULL_REQUEST_TEMPLATE.md`:

> By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

> *Disclosure: this change and description were prepared with the help of AI assistants.*

**Squash recommendation: yes.** Publish the two fix commits as one logical
upstream commit containing the complete fix and regression coverage, for
example with subject `Reject ordinary stubs of contract targets`. This
matches the owner's clean-history preference for the new PR and avoids
publishing the intermediate coverage gap. Preserve the final tree and
`Tiramisu-Cake <igkharin@gmail.com>` identity. No squash or history rewrite
was performed during this read-only review.

## Validation and boundary

- Revision and combined `git diff --check`: PASS.
- Exact ancestry, tree, clean candidate status, changed-file sets, unchanged
  negative pair and preserved original positive prefix: PASS.
- Small Python checks of the actual non-continuation matcher semantics:
  reordered/extra output accepted; missing harness announcements, wrong
  success totals, missing diagnostics and wrong abort count rejected. These
  are synthetic oracle checks, not native compiletest execution.
- Exact license/disclosure comparisons: PASS.
- Original author-package hashes still match the previous review. Revision
  package hashes: HANDOFF
  `248efa2dc14022ccbf5bf7cd800afc43de6340fff235be95d19bfecd0e5f8834`;
  PR draft
  `7fa3f2edb78a6a55d3005a6d92fad4d897e9172a7e05df91b4b605e55a17765c`.

Cargo/rustc/Kani/CBMC, formatter/native regressions, push and CI: **NOT_RUN**.
No build, coordinator, ledger, evidence history, candidate or publication
changes were made. Only this review HANDOFF is committed with `[skip ci]`
as `Tiramisu-Cake <igkharin@gmail.com>`; its SHA is reported in the final
response. This HANDOFF grants no execution or publication authority.
