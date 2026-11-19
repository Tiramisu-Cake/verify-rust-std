# HANDOFF — PR 5159 cleanup implemented, 2026-11-19

Stage complete; stop here. No push, CI or native execution in this stage.
The published PR branch and live PR body were not changed.

Cleanup commit: **`282d007d06a2fc45ca6e6dc719a305f333b63a7c`**.
Worktree: `/root/kani-pr5159-cleanup-w13`.
Local branch: `cleanup/pr5159-20261119`.
Parent: `78f745bb696c85095a9582f959d4854ec494c4f5` (exact published PR head).
Tree: `7a7103421211001791f2b01a5d06f3f5846e0b42`.
Exactly one candidate commit, authored and committed by
`Tiramisu-Cake <igkharin@gmail.com>`, subject
`Strengthen volatile ZST failure expectations`, no skip-ci or Co-Authored-By.

The g0 documentation commit containing this HANDOFF uses `[skip ci]`; its full
SHA is reported alongside the cleanup SHA in the final response. This file
cannot embed its own containing commit's SHA.

[FINDINGS.md](FINDINGS.md) records STEP 1, written before any candidate edit,
with CONFIRMED/WITHDRAWN decisions and source file:line evidence for every
finding and optional edit. Connected GitHub read confirmed the supplied head
and exact PR body; [PR-SNAPSHOT.json](PR-SNAPSHOT.json) records those fields.

- Both negative `.expected` files now require their named `Checking harness`
  header and `Complete - 0 successfully verified harnesses, 1 failures, 1 total.`
  They retain their original four-line bodies byte-for-byte: adjacent
  FAILURE/concrete description, concrete Failed Checks, and FAILED verdict.
- The exact headers come from `kani-driver/src/harness_runner.rs:273` and
  crate-relative pretty names from `kani-compiler/src/kani_middle/mod.rs:36-37`.
  The completion string comes from `harness_runner.rs:308-340`; it applies to
  one completed failing manual harness and prints before the failure exit
  (`kani-driver/src/main.rs:223-226`). FINDINGS traces both compiler reasons
  through the status/description/failure-message/verdict renderers.
- Three file-level comments were shortened. The entire compiler file and all
  eight proof functions, including internal comments and whitespace, are
  byte-identical to the PR head. The optional compiler and in-harness comment
  edits and argument counter were withdrawn to honor that constraint.
- The entire `kani-compiler/src/codegen_cprover_gotoc/codegen/intrinsic.rs`
  SHA256 remains
  `09a6e3f017471549fc5c7a45471a321157339409c42a29471f0bd3f8f035bed7`.
  Alignment, typed ZST construction, both uninhabited dispatch paths,
  non-ZST behavior, initialization TODO, and all flags/types/assertions remain.
- All six positive proofs remain in their original source and success mode;
  both negatives retain separate sources and same-stem expected files.

[PR-BODY.md](PR-BODY.md) is the concise local draft. It retains #5072 and the
license and AI disclosure lines exactly, removes historical platform/CI
bookkeeping, and states that native tests and current-candidate standard CI
are pending. No external draft or PR mutation occurred.

Static validation: **PASS**. [STATIC-CHECK.json](STATIC-CHECK.json) records
all eight byte-identical proof-function hashes, unchanged compiler hash,
the exact five-file diff boundary and preservation of both original oracle
bodies. [validate_static.py](validate_static.py) reproduces the bounded audit
with Python/Git only. The matcher port follows
`tools/compiletest/src/runtest.rs:528-598`: independent substring blocks and
backslash-consecutive lines, not exact transcript matching. It accepts eight
synthetic variants and rejects 22 missing/wrong-header, missing/wrong-summary,
wrong-reason, wrong-verdict, wrong-status and broken-adjacency variants.
`git diff --check` and staged whitespace checks pass.

The stronger oracle rejects intended-diagnostic output missing completion;
it cannot enforce an exit code or reject arbitrary extra trailing errors.
Complete intended output plus a synthetic error tail still matches. No real
compiler crash, native outcome, MIR return-target route or proof credit is
claimed from these checks.

Cargo/rustc/Kani/CBMC, native tests/discovery, base/fixed replay, format/clippy,
and CI: **NOT_RUN**. No build, push, raw evidence/log retrieval, PR/comment
write, ledger/coordinator change or subagent. Source worktree is clean after
its one commit. Unrelated g0 work is excluded from this documentation commit.

Future work requires a separate stage: validate the exact cleanup commit on
authorized infrastructure, including six positive harnesses, both completed
specific negative outcomes and the original reproducer. Update the draft's
validation statement with actual candidate results before publication.
This HANDOFF grants no build or publication authority.
