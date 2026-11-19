# PR 5159 offline review READY

Task `98784e2ade6135d3177b0ad14c9ab88777ab6aa2`. Review is complete and recommendation-only. The containing g0 commit returned externally binds MANIFEST.json; implementation, CI and owner publication remain separate.

- Published merge head: `78f745bb696c85095a9582f959d4854ec494c4f5`; tree `b9c008a20c87cb3cffd93605da184d592fc49daa`.
- Parents: `70d9288513f4d19fdfb4ca0e19a4f73ec203cd46` and `faffcee3bca2770c03bd21c3bde89cc8f6f7a14e`; the latter is the exact base/merge-base.
- Head ref/repository: `fix/volatile-zst-5072` in `Tiramisu-Cake/kani`; target `model-checking/kani#5159`.
- Read-only source `/root/kani-pr5159-slop-readonly-20261119` remains detached, clean and exact. All6 changed blob SHAs, SHA256/bytes and the full source diff match.
- PR body SHA256 `9c9f09520c537f20ca55154cbc5352c7e7900d79fca579c5f78bea67b4e3167d`; diff SHA256 `18724fc6d87d49afe49418c8e49c48e78d50b457974dac35c11e28e9355e83da`.

Retain the implementation structure and all8 proof harnesses (6positive/2negative). REPORT.md traces the typed inhabited-ZST result, retained operand/alignment path, unchanged non-ZST dereference and separate SafetyCheck generation for uninhabited results with/without a MIR return target. No correctness defect or native main-fail/head-pass result is established by this offline review.

The main useful edit is to strengthen both negative expected files with their named harness and completed0success/1failure/1total summary while preserving the exact reason/FAILURE clusters. STATIC-CHECKS.json records a bounded port of the actual expected matcher accepting synthetic incomplete failure output under the current patterns; this is an oracle weakness, not a reproduced compiler crash. A completed summary improves the output requirement; later authorized native validation still needs to confirm the normal verification failure outcome.

COVERAGE-EDITS.md/JSON names every current harness, its assertions, local Z/Empty types and expected oracle. FILE-DISPOSITIONS.json covers every changed file. The positive cases are already grouped in one ordinary-success source file, and the two safety failures belong in separate expected-output cases. No source/harness removal, test framework or generated matrix is recommended. CODE-COMMENT-EDITS.md contains exact optional new-comment edits; keep all base comments/licenses and supported diagnostics.

PR-BODY.suggested.md preserves #5072, the concrete user behavior, license and exact AI disclosure. Historical body CI and the Copilot COMMENTED review refer to pre-merge70d9288; they were not rechecked and do not establish current merge-head validation. The proposed public text uses one pending standard-workflow CI placeholder. It exists only in this review packet, with no live PR or owner-draft changes.

Native/compiler/Cargo/rustc/rustfmt/Kani/CBMC/expansion/verifier/fullrunner/CI, push/publication, source/test edits, live PR/body/comments/external-draft writes, raw logs/GCS, ledger/accounting, subagents or model/settings changes were not performed. High/FastOFF preserved. Return this exact commit/manifest to root and await any separately scoped implementation/validation task. Do not auto-start another PR; independent S4 fresh14 intake remains untouched.
