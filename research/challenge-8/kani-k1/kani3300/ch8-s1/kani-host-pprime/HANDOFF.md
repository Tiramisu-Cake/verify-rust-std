# Worker13 — P-prime handoff

Task `TASK-CH8-PPRIME-REBASE.md` item 13, g0 input `34fb6ac87607be8e27634245c68331853142ed02`.

S′ `f22f84f316ad8ef6f3fccce86424bad927b09f78`, tree `e0dc89592926571e823797f8618cd6b4a7e11ff6`, branch `work/ch8-s1-pprime-w13`, worktree `/root/verify-rust-std-ch8-s1-pprime-w13`. Three commits above P′ `c5ff36ff433692140605891f646043f991db05de`: the two requested cherry-picks and the extra-`>` fix. The sole conflict was the Kani pin, resolved to stock `0aac`. All nine S′ payload files match original S except the one corrected generic call. Toolchain is `nightly-2026-10-23` from P′. Full source diff read; no further analogous typo found. Compilation remains unverified.

Control `8c8ac10d675fff41d5ec1b2684c6f673cd6bfaf2`, tree `f0a7d1d51f9d57f1c0f859f632741066a6e5c11f`, branch `uninit-ci/ch8-s1k-pprime-w13`, worktree `/root/kani-ch8-s1k-pprime-w13`, sole parent `0aac16ef62da9e9d5645782d458593e5d78143ba`. Relative to old control `36db70978a`, only three files differ: std bindings and derived hashes in request, STD_SHA/STD_TREE in runner, and workflow upload exclusion for all `target/` subtrees. Runner behavior is preserved. Historical patch/model provenance fields retain their original meaning.

23 literal row records, selectors, oracles, budgets, flags, activation patches and tests are preserved. Static source/control identities, runtime-body comparison, activation patch result hashes, YAML/actionlint and 16 synthetic error-path tests pass. Exact identities and manifest are in `CI-REQUEST.json`; validation records and independent `REVIEW.md` accompany both review packets.

New commits carry `[skip ci]` and author `Tiramisu-Cake <igkharin@gmail.com>`. No push, CI, publication, ledger, compiler or verifier operation. All 23 proof rows NOT_RUN; proof obligations closed: 0; proof credit: NONE.

Next coordinator action in a later authorized stage: publish exact S′/control and authorize dispatch. This local control is suppressed by `[skip ci]`. Any separately authorized same-tree activation sibling must keep the exact single tool parent; an activation child violates the binding guard. Preparation completes after independent review and static checks.
