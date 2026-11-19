# HANDOFF — PR5172 cleanup, one stage complete

The authorized offline implementation stage is complete. **Stop at HANDOFF.** No push, CI, native tool execution or live PR/body update occurred. This is a committed cleanup candidate with static validation; native regression outcomes remain unverified.

- PR: model-checking/kani#5172, published branch Tiramisu-Cake:fix/kani-uninit-unresolved-call-v3.
- Pinned parent: `80e5d6fabc0103b0b3117440007ad2d9475f9a9c`.
- New worktree: `/root/kani-pr5172-cleanup-w11`.
- New local branch: `cleanup/pr5172-20261119`.
- Cleanup commit: `fef46d2d9d65bf3eb91a282da004043ecd26a208`.
- Cleanup tree: `2e6c41da31c3e5a96a9a7d39efa8eb93e6c973e7`.
- Exactly one commit above the pinned parent; author and committer: Tiramisu-Cake <igkharin@gmail.com>.
- Commit message: `Share unresolved-call regression fixtures and correct transfer comment` (no skip-ci or Co-Authored-By).
- The g0 packaging commit includes [skip ci]; its full SHA is reported externally to avoid a circular self-pin.

[FINDINGS.md](FINDINGS.md) records STEP 1 dispositions and pinned source evidence. All 50 changed-file hashes/byte lengths were checked before editing, along with 22 source roots, 24 proof harnesses, 11 identical helpers and eight identical expected files; [STEP1.json](STEP1.json) preserves that receipt. The actual compiletest collector, per-source runner, expected-file fallback, output matcher, codegen grouping and delayed-target collection were inspected. The recommendations were not treated as native evidence.

The coordinator explicitly resolved the original task's compiler-byte conflict: apply **only** the return-state comment correction in kani-compiler. The single-use adapter is **DEFERRED**, with exact reason **'avoid code churn in a PR under review'**. Both adapters and their call sites remain unchanged. Other optional comment trims and formatter deduplication are WITHDRAWN from this implementation. The missing generated-shim guard negatives remain a confirmed source coverage gap assigned to the separate SOUNDNESS-FOLLOWUP.md, not implemented here and not an established unsound execution.

## Implemented cleanup

The 11 seeded sources now include `auxiliary/analysis_target.rs` by explicit path. Its public `check_byte_copy` preserves the exact helper operations, `#[inline(never)]`, copy intrinsic, equality assertion, explanatory comment and standard license header. All 12 old helper call positions remain, including both generated-positive harnesses. Only seeded files import it.

The eight identical expected files for erased-pointer, fn-pointer, global-escaped and wrapped-pointer, in both modes, now use the exact common bytes in directory `expected`. All other 14 named expected files retain precedence and their original bytes. Git represents one removed named oracle as a 100% rename to `expected`; no oracle text was weakened.

All 24 harnesses remain in the same 22 source roots. Plain and seeded variants still have separate source invocations, with every original compile/Kani flag retained. No harness, assertion, custom MIR, initialization distinction, generated-positive companion or fail-closed control was removed. No new test framework, compiler logic, negative shim fixture or build flag was added.

The sole compiler edit replaces the two inaccurate Item|Shim comment lines with:

```rust
// Foreign allocation calls use the models below; other calls store
// initialization state for union arguments.
```

Reversing precisely this comment substitution reproduces `uninit_visitor.rs` byte-for-byte. All other compiler bytes are identical to the parent. This retains both shim guards, recursive classifier and conservative unknown case, fallible resolver, initial-target `.ok()` behavior, common terminator epilogue and unsupported diagnostic strings. No compiler code tokens changed.

## Static validation and limits

[static_checks.py](static_checks.py) produced [STATIC-CHECKS.json](STATIC-CHECKS.json) against the committed cleanup SHA. PASS:

- Reversing module/helper call edits reproduces every seeded source exactly; all plain source files are byte-identical. Thus harness bodies, flags and retained custom MIR are preserved apart from helper relocation and qualification.
- The inspected discovery rules, mirrored in a bounded Python collector, still discover the exact same 22 roots, excluding the auxiliary helper. There are 24 retained harnesses and 12 copy-helper calls.
- Every root's effective expected file is byte-identical to its own previous expected file. There are 14 named oracles and eight fallback users. Safety property status/description adjacency, unsupported diagnostics, verdicts and completed harness summaries are unchanged.
- The compiler file matches its parent after the exact two-line comment reversal; the other five compiler files changed by the original PR match their parent bytes directly. Whole-diff scope checks establish no other compiler-file changes. Driver, library and compiletest sources are unchanged.
- `git diff --check` passes. Candidate parent, single-commit count, author/committer, message, committed file bytes and clean worktree were checked after committing.
- The PR body snapshot hash matches its pin. License and AI disclosure lines in [PROPOSED-PR.md](PROPOSED-PR.md) match the original exactly.

An initial static-check run after staging encountered Git rename detection: `--name-only` listed only the renamed oracle destination. The scope check was corrected to use `--no-renames`, explicitly accounting for both removed source path and added destination, and passed without any candidate change. An absolute-path `hash-object` invocation also emitted attribute warnings; raw blob hashing now uses relative paths with `--no-filters`. These were inspection-script issues, not Rust or regression outcomes.

NOT_RUN: Cargo, rustc, rustfmt, Kani, CBMC, native base/fixed comparison, compiletest execution, CI and independent review. No new native PASS, performance or proof credit is claimed. Static preservation does not establish post-relocation native outcomes. Historical CI statements in the original body were not promoted into evidence for this candidate.

[PROPOSED-PR.md](PROPOSED-PR.md) is the concise, unpublished PR body draft. It retains #3300, the observable failure/fix, generated-shim limitation and exact disclosures, and states that native regressions and CI have not run for this cleanup revision.

## Preserved state and next-stage boundary

The cleanup worktree is clean. `/root/kani-5172-fixup-w11` remains clean at `5d5035f5afcaf90902772bf68f56bae253ac2f99`; it was not edited or checked out. The original read-only checkout remains clean at the pinned published head. No PR branch/ref was changed by this stage; only the new cleanup branch was created and committed.

The g0 commit contains only this new `research/challenge-8/kani-k1/kani3300/wave0/pr5172-cleanup/` directory. Other workers' files and historical recommendation/evidence records were preserved. No sessions, phases, owners, budgets, ledgers, CI dispatch, raw evidence access, settings or subagents were used or changed.

Any further adapter cleanup, shim negative coverage, review, native validation, push, CI or PR-body publication requires a separate assignment. This one-stage task stops here with HANDOFF.
