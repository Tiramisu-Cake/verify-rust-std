# TASK — slop review of the #5206 fix PR (code, tests, comments, text), 2026-11-20

One stage. Read-only on Kani: do not edit, commit, push, run cargo/rustc/rustfmt/Kani/CBMC, start CI or post anything. Write only `HANDOFF.md` in this directory, commit it to g0 with `[skip ci]` as Tiramisu-Cake <igkharin@gmail.com>, push origin, stop.

## What is reviewed
- Kani commit `a65ffdbdcc` (branch `fix/stub-contract-target-conflict-v2`, single commit on main `0997d11c14`). Read it with `git -C /root/kani-fix-5206-w13 show a65ffdbdcc` (do not switch branches or edit that worktree). Five files: `kani-compiler/src/kani_middle/stubbing/mod.rs` and four test files under `tests/ui/function-contracts/` and `tests/expected/function-contract/`.
- The PR text to be published: `PR-TEXT.snapshot.md` in this directory (everything below the `---` line). It will close issue model-checking/kani#5206 (read the issue with `gh issue view 5206 -R model-checking/kani`).
- Style rules: `../open-pr-slop-inputs-20261119/STYLE-UPSTREAM-RULES.snapshot.md`, plus the style of surrounding code and of neighbouring tests in the same directories on main.
- Earlier correctness reviews (do not redo them, use only as context): `../issue5206-fix-review/HANDOFF.md`, `../issue5206-fix-r2-review/HANDOFF.md`.

## Look for "AI slop"
- Code: anything beyond what the fix needs; needless closures/abstractions, naming unlike neighbours, dead code, redundant checks, diagnostic wording unlike other Kani errors (compare with existing `span_err` messages in `kani_middle`).
- Tests: are all harnesses needed, or do some duplicate each other? Comment density and wording vs neighbouring tests; header lines; whether `.expected` files check only what matters.
- Comments: narration, restating code, over-explaining, comment density unlike the file.
- PR text: filler, overlong sentences, claims not backed by the diff or CI, wrong references, anything a maintainer would find padded. Check the CI claims against GitHub metadata for runs 44616139446 (attempts 1 and 2) only via `gh run view` / `gh api` job metadata, no logs. The license sentence and disclosure line are mandatory, keep them.
- Verify each finding against the actual code before reporting. A false finding is worse than none. Prefer few concrete edits; do not propose rewrites for taste.

## Output
`HANDOFF.md`: verdict (KEEP AS IS / EDITS RECOMMENDED), numbered findings with file:line, classification (correctness / style / text), exact suggested replacement for each, whether each code/test edit is worth a new CI run, and a full suggested PR text if you change it.
