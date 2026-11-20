# HANDOFF — #5206 slop review

**Verdict: EDITS RECOMMENDED — PR text only. Keep the code and tests as is.**

Reviewed `a65ffdbdccfe5c3620b50c416870f1085a987d30`, its sole parent
`0997d11c14cb2da0824efc34e2c4001e53ac0faf`, all five changed files, and
`PR-TEXT.snapshot.md` below the separator. The assigned g0 starting commit was
`8b1802a697fa0d016fb1df96bf0ea253ab7928da`; both worktrees started clean.
The style snapshot and the two earlier correctness reviews were read. Those
reviews supplied context; this stage did not repeat their correctness audit.

## Numbered findings

1. **`PR-TEXT.snapshot.md:11` — text: shorten Testing to supported CI results.**
   The linked run's second attempt has eight successful jobs, but its overall
   conclusion is `failure`, with `regression (macos-15)` cancelled. State that
   result explicitly. The first attempt's failed step is named only
   `Execute Kani regression`; job metadata cannot establish `codegen_cache`,
   a flake, or an unrelated cause. Remove that explanation. Format, Clippy
   and Cargo Deny are not separately identified in the inspected job/step
   metadata; omit their individual pass claims rather than infer them from a
   broader job. This does not establish that those checks were absent or failed.

   Exact replacement for the entire Testing paragraph:

   ```markdown
   Testing: the new tests check both conflict diagnostics and the allowed different-target and reverse-direction stubs under each contract attribute. In [fork CI](https://github.com/Tiramisu-Cake/kani/actions/runs/44616139446/attempts/2), regression passed on Ubuntu 22.04, Ubuntu 24.04, Ubuntu 24.04 ARM and macOS 15 Intel; documentation, perf, benchcomp and LLBC also passed. The overall conclusion is `failure`, with `regression (macos-15)` cancelled without an assigned runner. Ubuntu 22.04 passed on the second attempt after failing on the first.
   ```

   **New CI run worth doing for this edit: no.** This corrects the description
   of existing results and changes no code or tests.

2. **`PR-TEXT.snapshot.md:7` — style: make the main/fix comparison explicit
   and use the required two substance paragraphs.** The current paragraph
   combines the symptom, mechanism, classification, fix and retained behavior.
   The style snapshot requests two substance paragraphs and an explicit
   main-versus-fix statement. The issue supplies the main behavior; the diff
   supplies the new diagnostic. No new technical claim is needed.

   Exact replacement for line 7, including the paragraph break:

   ```markdown
   On main, combining `#[kani::stub(f, g)]` with `#[kani::proof_for_contract(f)]` or `#[kani::stub_verified(f)]` in the same harness fails with `Failed to find contract closure __kani_recursion_check_f`. The ordinary stub replaces the body containing `f`'s contract instrumentation.

   Kani now rejects these combinations while resolving the harness's stubs, with an error naming the function and conflicting attributes. Ordinary stubs of other functions and reverse-direction stubs remain supported.
   ```

   **New CI run worth doing for this edit: no.** Text only.

## Code, tests and comments: keep

- `kani-compiler/src/kani_middle/stubbing/mod.rs:39`: the local
  `check_conflict` closure shares the same check and diagnostic across two
  attribute kinds. Neighbouring `stubbing/annotations.rs:19` uses a local
  closure for shared resolution, and `attributes.rs:397` shares diagnostic
  emission through a closure. Extracting another helper would add structure
  without a concrete benefit. The deduplication at line 58 addresses repeated
  resolved verified targets, as explained in the earlier review; retain it.
  The diagnostic's function name, attribute names, backticks and harness span
  fit nearby `span_err` calls (`stubbing/annotations.rs:28,51` and
  `attributes.rs:400,437,450`). No new narrative comments or dead code were found.
- `tests/expected/function-contract/ordinary_stub_different_target.rs:18,29,37,43`:
  the four harnesses cover different-target and reverse-direction stubs for
  each of the two contract attributes. The different-target cases require
  the ordinary replacement; the reverse cases guard acceptance when the
  contract target is a replacement value. They are not duplicate controls.
  Keep the two negative harnesses at
  `tests/ui/function-contracts/ordinary_stub_target_conflict.rs:14,20` for the
  two diagnostics, including the qualified `crate::f` spelling.
- Both `.rs` headers match main's `simple_replace_pass.rs` and
  `multiple_replace_pass.rs`. There are no added explanatory comments to trim.
  The three negative expectations require the two messages and error total;
  the six positive expectations identify all four harnesses and their success
  total. Main's `resolution_errors.expected` uses an abort total, and
  `valid_ptr.expected` uses harness announcements and a completion total.
  No unstable transcript or unrelated output needs removal.

**Suggested code/test edits: none. No new CI run is recommended for this review.**

## CI metadata checked

Read [issue #5206](https://github.com/model-checking/kani/issues/5206) with
`gh issue view`. Read only run/job/step metadata for run `44616139446`,
attempts 1 and 2, with `gh run view --attempt` and `gh api`. Both attempts
identify the reviewed SHA and branch `fix/stub-contract-target-conflict-v2`.

| Job | Attempt 1 | Attempt 2 |
| --- | --- | --- |
| regression (ubuntu-22.04) | failure | success |
| regression (ubuntu-24.04) | cancelled | success |
| regression (ubuntu-24.04-arm) | cancelled | success |
| regression (macos-15-intel) | cancelled | success |
| regression (macos-15) | cancelled | cancelled |
| documentation | success | success |
| perf | success | success |
| benchcomp-tests | success | success |
| llbc-regression | success | success |
| Overall run conclusion | failure | failure |

Attempt 1's failed Ubuntu 22.04 job is `135885222974`, with failure at
`Execute Kani regression`. Attempt 2's successful Ubuntu 22.04 job is
`135916496115`. Its cancelled macOS 15 job, `135916495432`, has empty
`runner_name`, empty `runner_group_name`, and no steps. This supports the
unassigned-runner wording for attempt 2, without diagnosing why it was
cancelled. Documentation, perf, benchcomp and LLBC retain their first-attempt
execution times in attempt 2's metadata; they are successful carried results,
not four freshly rerun jobs. No logs were read and no failure cause was inferred.

## Full suggested PR text

Title: Reject ordinary stubs of contract targets

On main, combining `#[kani::stub(f, g)]` with `#[kani::proof_for_contract(f)]` or `#[kani::stub_verified(f)]` in the same harness fails with `Failed to find contract closure __kani_recursion_check_f`. The ordinary stub replaces the body containing `f`'s contract instrumentation.

Kani now rejects these combinations while resolving the harness's stubs, with an error naming the function and conflicting attributes. Ordinary stubs of other functions and reverse-direction stubs remain supported.

Resolves #5206.

Testing: the new tests check both conflict diagnostics and the allowed different-target and reverse-direction stubs under each contract attribute. In [fork CI](https://github.com/Tiramisu-Cake/kani/actions/runs/44616139446/attempts/2), regression passed on Ubuntu 22.04, Ubuntu 24.04, Ubuntu 24.04 ARM and macOS 15 Intel; documentation, perf, benchcomp and LLBC also passed. The overall conclusion is `failure`, with `regression (macos-15)` cancelled without an assigned runner. Ubuntu 22.04 passed on the second attempt after failing on the first.

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*

## Validation and boundary

Candidate `git diff --check 0997d11c14 a65ffdbdcc`: PASS. Surrounding source
and neighbouring tests were read at the pinned main commit. License and
disclosure sentences above are preserved verbatim. Only this `HANDOFF.md`
was written; the PR snapshot and Kani worktree were left unchanged.
Cargo, rustc, rustfmt, Kani, CBMC, native tests and new CI: **NOT_RUN**.
No upstream post, Kani commit/push, build submission or evidence/ledger
change was made. One read-only review stage complete; publish only this
artifact to g0 with `[skip ci]` as instructed, then stop.
