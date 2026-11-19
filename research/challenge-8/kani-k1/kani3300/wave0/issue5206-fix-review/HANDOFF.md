# HANDOFF — independent review of issue #5206 fix

**Verdict: APPROVE_WITH_CHANGES.** The implementation is correct by static
inspection for the requested conflict predicate. Add the missing positive
regression cases in R1 before accepting the package. R2 is a minor diagnostic
improvement. No relocation of validation or change to #5204 is requested.

One review stage complete; stop with this HANDOFF. Candidate and author
package were left unchanged. This is a source/static review, not native test
or CI acceptance.

## Reviewed identities and scope

- Issue read directly with `gh issue view 5206 -R model-checking/kani`:
  <https://github.com/model-checking/kani/issues/5206>.
- Candidate: `/root/kani-fix-5206-w13`, branch
  `fix/stub-contract-target-conflict`, clean HEAD
  `e58623967899e51f9716bdb1d76b8d5bf7f80944`.
- Sole parent/base: `0997d11c14cb2da0824efc34e2c4001e53ac0faf`.
  Five changed files, 74 insertions; author and committer are
  `Tiramisu-Cake <igkharin@gmail.com>`.
- Approved #5204 head inspected:
  `b3019ab3f9c83a25cd4d870e49e49121b3327bb1`.
- Author package: sibling `issue5206-fix/{HANDOFF.md,PR-DRAFT.md}`.
  Review performed directly in this separately assigned review session;
  no helper or nested delegation was used.

## Findings

### R1 — P2: complete the positive regression coverage

`tests/expected/function-contract/ordinary_stub_different_target.rs:18`
tests only `proof_for_contract(caller)` with `stub(f, g)`. Neither new test
exercises `stub_verified(h)` with `h != f`, or the allowed reverse direction
`stub(g, f)` when the contract target is `f`. A future regression that rejects
every ordinary stub on a verified-stub harness, or checks replacement values
as well as original keys, would pass the current tests.

Add compact positive harnesses for a different verified-stub target and for
the reverse direction under both contract attributes. Reuse the positive
fixture where practical, keep corresponding contract-proof harnesses, and
update its successful completion count. Make the different-target verified
case assert a result that requires the ordinary replacement to take effect;
calling only the abstracted contract target would hide a dropped stub.
The reverse-direction cases should guard acceptance without accidentally
making this issue's main-alone control depend on the separate #5204 fix.
Retain the current discriminating `caller` control.

### R2 — P3, optional: repeated verified targets repeat the conflict message

`kani-compiler/src/kani_middle/stubbing/mod.rs:55` iterates the interpreter's
`Vec` without deduplication. For a harness with two `stub_verified(f)`
annotations and `stub(f, g)`, the new diagnostic is emitted twice at the same
harness span. `attributes.rs:708` treats duplicate verified annotations as a
warning, so this input can reach grouping. This is distinct from repeated
calls per codegen unit and does not affect rejection correctness. Consider
deduplicating resolved verified target IDs before reporting conflicts.
Existing duplicate-attribute warning behavior need not be changed here.

## Answers to the requested code checks

1. **Correctness.** `stubbing/mod.rs:35` resolves ordinary stubs into an
   original-to-replacement `DefId` map. The new test at line 42 checks keys
   against the resolved target of this harness's contract attributes. Thus
   `stub(f, g)` conflicts with either contract attribute targeting `f`,
   including `crate::f` and aliases resolving to the same identity. A
   different contract target, a different verified-stub target, and
   `stub(g, f)` targeting `f` do not satisfy the predicate. Unrelated
   harnesses do not share their attribute sets. Transitive stubbing preserves
   original keys, so checking before transitivity does not miss a replaced
   contract target. The returned stub map is unchanged. Existing errors for
   invalid configurations remain possible; this conclusion concerns the new
   conflict diagnostic.

2. **Call count and recipients.** The sole caller of `harness_stub_map` is
   `codegen_units.rs:251`, once per selected manual harness in the HashMap,
   before grouping. `CodegenUnits::new` invokes grouping once in the selected
   reachability branch, not once per output unit. The CPROVER backend calls
   it once at `compiler_interface.rs:395`; LLBC calls it once at line 201 of
   its backend. Neither backend's per-unit/per-harness transform loop calls
   it again. Non-harness items do not enter this map; automatically generated
   harnesses are appended separately without stubs. Ordinary one-occurrence
   conflicts therefore produce one new error each in a compiler invocation.
   Separate compiler invocations can naturally report again; R2 describes
   the duplicate-annotation exception.

3. **Interpreter diagnostics.** Both interpreters emit their own errors:
   `attributes.rs:294` resolves every verified target; line 315 also checks
   proof-for-contract multiplicity. They are invoked again immediately by
   `extract_contracts` at `codegen_units.rs:286,289`. However,
   `kani_compiler.rs:267` runs `check_crate_items` after analysis;
   `kani_middle/mod.rs:94,128` validates attributes and aborts on errors before
   codegen/grouping. Normal malformed/unresolved free-function attributes
   therefore cannot acquire additional diagnostics from this new call.
   Re-parsing is redundant work, not an established duplicate-error defect
   for those invalid inputs. Existing validation can itself repeat errors
   (e.g. `check_stub_verified` parses the whole vector for each attribute);
   that behavior predates the patch.

4. **Placement and style.** `attributes.rs:389` handles attribute syntax,
   harness restrictions and attribute-only conflicts. In particular the
   `proof`/`proof_for_contract` conflict in the `Proof` and `ProofForContract`
   match arms is reported at
   an attribute span. The proposed check instead uses the final resolved
   ordinary map, including `use_stub_set` entries extracted into metadata, beside
   duplicate mapping and cycle validation. That is a reasonable placement:
   `validate_units` aborts at `codegen_units.rs:325`, before
   `BodyTransformation::new` in both backends. Moving it into early attribute
   validation would require preserving the same resolved/set-expanded
   semantics; there is no correctness reason to require that refactor.
   One consequence is that this conflict is checked for selected harnesses,
   while early attribute misuse is checked crate-wide. That matches the
   existing resolved-stub validation phase and the issue's selected-harness
   reproducer.

5. **Spans and messages.** The harness definition span matches
   `stubbing/annotations.rs` resolution/duplicate errors and
   `codegen_units.rs:316` compatibility diagnostics. The message names the
   target and both conflicting public attributes; crate-prefix stripping
   preserves useful module qualification. It replaces the internal closure
   lookup wording with an actionable configuration error. Attribute spans
   and a suggestion to remove one replacement could improve precision, but
   are optional given the surrounding style. The current tests do not check
   span quality.

6. **Tests and oracle.** `tools/compiletest/src/runtest.rs:488,528,564,590`
   reads the sibling `.expected`, combines stdout/stderr, and checks trimmed
   literal substrings in output lines. Trailing backslashes join consecutive
   groups; neither new expected file uses them. Each line is consequently
   an independent unordered requirement, not a regex or an exact transcript.
   Both complete conflict texts and the two-error abort line are required.
   Replacing either with an unrelated/wrong message, or omitting either,
   fails matching. Extra lines and suffixes are allowed; occurrences are not
   counted. A genuine four-error abort fails the two-error requirement, but
   the matcher alone is not a duplicate-diagnostic counter. Expected mode
   checks exit success only with `--require-success`, which the standard
   suite loop does not supply. The positive file's success and one-harness
   completion lines still require successful verification output.

   The negative fixture includes a proof-for-contract harness for `f`, so
   its verified case avoids the independent missing-proof error. The
   qualified `crate::f` path adds useful identity coverage. The positive
   control is meaningful: uncontracted `f` returns false, replacement `g`
   returns true, and `caller` promises true. Dropping ordinary stubbing
   violates that postcondition. The files are small, use standard flags and
   source licenses, and contain no redundant explanatory boilerplate. R1
   is the remaining coverage gap. Expected runtime behavior remains unrun.

7. **#5204 compatibility.** Both `git merge-tree --write-tree` checks exited
   zero without conflicts. Main plus #5204 produced tree
   `ff09d83ed7a12a04458f91cbcd7a76410011a9f5`; candidate plus #5204 produced
   `0ab16585785ea831d572c48530c5614d0df4b33f`. The difference is exactly the
   candidate's five files/74 insertions. All `kani_middle/transform/*` files
   are byte-identical between those merge results, and all five candidate
   files are byte-identical between candidate and combined tree. Source
   inspection confirms the new abort precedes #5204's body-source selection
   logic. This establishes textual/static compatibility, not a runtime
   regression result. No checkout, merge, cherry-pick or branch update was
   performed; merge-tree only created local Git objects.

## PR draft review

The title and two substance paragraphs are concise and accurately describe
the same-harness identity check, both conflicts, qualified paths and the
pre-transformation diagnostic. `Resolves #5206` is appropriate. The Testing
TODO accurately records the offline limit and must be replaced with actual
authorized results before publication. No unsupported test/CI success or
unrelated #5204 claim appears. No prose rewrite is required.

These lines each occur exactly once, byte-for-byte matching the existing
PR body snapshot at `open-pr-slop-inputs-20261119/pr-5195/PR-BODY.snapshot.md`;
the license also matches Kani's `.github/PULL_REQUEST_TEMPLATE.md`:

> By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

> *Disclosure: this change and description were prepared with the help of AI assistants.*

## Static validation and boundary

- Candidate and combined-delta `git diff --check`: PASS.
- Candidate identities, clean status, scope, merge-tree results and exact
  file preservation: PASS.
- Ten small Python checks of the inspected matcher semantics: PASS
  (complete/reordered texts, wrong/missing messages, changed abort count,
  extra output, duplicate occurrences and suffix behavior). These evaluated
  literal containment for the actual non-continuation expectations; native
  compiletest was not executed.
- Exact license/disclosure comparisons: PASS.
- Author package SHA-256 preserved:
  HANDOFF `e45448fc3c1599daa786baadc1868864dff07b8e48becb766695e3932b4c4784`;
  PR draft `bce6d1a9bbe1f820227a7d6021ad4de219c78d164f4757e02c6e4b876455b4d2`.

Cargo/rustc/Kani/CBMC, formatter/native regressions, push and CI: **NOT_RUN**.
No build, coordinator, ledger, historical evidence, upstream issue/PR or
author-package changes were made. Only this review artifact is committed,
with `[skip ci]`, as `Tiramisu-Cake <igkharin@gmail.com>`.

Next owner action: add R1 controls, optionally deduplicate R2, then obtain
authorized native validation on main/fix and with #5204 and update the PR
Testing paragraph. This HANDOFF grants no execution or publication authority.
