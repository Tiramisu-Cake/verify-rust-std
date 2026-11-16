# U-02 preparation review

## Identity

- Candidate: `952ea771be3827a495a9c9f29ad6a015bd796fc7` (tree `6635864584be3049f96e146cb548b348101b0064`), baseline: `b4edbb18bc8a490197420aac0964a7d55b284380`.
- Source replacement: `09a6d1cb2cba63e67e60aeefbd909d1f64849b76` on PR02 `932fb8395a58f8c86c0d702ba2cae835823b2962`.
- Packet `review-packet`: SHA256 `fa5bd929ab2823ed61a22a661dd84d8a7bc2abe739fb323b78cfec66652dee2c`; packet `spec.json`: SHA256 `433a361a102bd9eb74e63e214b79be6879738f2c74e1d374c751b32622bd3885`.
- `/usr/local/bin/smallsort-session review check` returned `PACKET_VALID_NOT_REVIEWED`, 26 files, `proof_credit: NONE`. This establishes packet identity only.

## Review

No blocker found for the pinned U-02 preparation scope.

- The seven fixtures are now top-level `script-based-pre/autoharness_entry_reset_<case>` directories, each with the expected four files. Independently compared all 28 old/new file contents and Git modes: identical. The updated patch digest, PR02/SEL1 patch application trees, and request pins agree with the compatibility manifest. Independently recomputed the base-to-source compiler diff SHA256 for both U-01 and U-02: `f7beb5f9fc63e3a0a63536c44b922f07937d91829ecb551a3cbea3d517f232da` in both cases.
- Workflow remains A-only, push-triggered on the dedicated branch pattern, repository-gated, first-attempt/same-tree gated, sequential (`max-parallel: 1`), capped at 120 minutes, with two Cargo jobs/test threads and no retry. Source checkout and patch application bind commit, tree, patch digest, and resulting tree.
- Gate wrappers keep a 16 KiB output tail per gate, persist the child exit code/status, and represent timeout/error distinctly. Finalization carries workflow step outcomes, source/patch/target request identities, and `proof_credit: NONE`; unstarted gates are `NOT_RUN`, in-progress gates remain distinguishable, and malformed/null/wrong-typed or mismatched receipts become `MALFORMED`. Finalize and artifact upload use `always()`. The artifact path contains bounded tails/receipts, not complete child logs. Existing B arm is removed from the matrix and retained as task-reported U-01 context, not rerun or new proof credit.

## Checks and limits

Passed offline `check_package.py`, `check_source_structure.py --repo /root/kani-fix-ch8-pr02-reset-u02-source`, five existing synthetic runner tests, and two isolated receipt tests covering child success/nonzero/missing command/timeout/output bound, setup failure, missing/in-progress/malformed/null/wrong-type receipts, and source-pin/proof-credit fields. No Rust build, rustc/Kani/CBMC execution, CI, push, publication, or raw-log audit was performed. U-01 B success remains coordinator/task-reported. Receipts and request pins are execution metadata, not independently observed compiler/model bindings or proof evidence. GitHub `always()` cannot recover if initial control checkout fails or the runner is lost.

## Recommendation

**GO for this one U-02 preparation stage only.** This review grants no runtime, verifier, or proof credit and does not authorize dispatch or publication.
