# S1-04 handoff — one preparation stage complete

Package prepared locally. No push, CI, publication, phase registration, ledger modification or local cargo/rustc/Kani/CBMC invocation. New proof rows NOT_RUN; proof credit NONE; qualified acceptance PENDING.

Exact inputs:

- std `5be85699b8826e3286c0bf89efb9affefac0acb5`, tree `a9caaa953d579641ecc6a4b84b5c16fa1d23563b`, worktree `/root/verify-rust-std-ch8-s1-04-w13`, branch `work/ch8-s1-04-prep-w13`, based on S′ `f22f84f316ad8ef6f3fccce86424bad927b09f78`. Both local source commits use `[skip ci]`; only one verify file changed.
- control `5fd538730869103cb7108cd823f58b1dac924960`, worktree `/root/kani-ch8-s1-04-w13`, branch `uninit-ci/ch8-s1-04-prep-w13`, single parent `40b5d9cf48900ff1e227e1fbba24cb5b2edbf8d5`. Its message permits a future authorized CI publication; its current branch does not match the workflow trigger. No publication was performed.
- tool stock `0aac16ef62da9e9d5645782d458593e5d78143ba`; separate sibling tool checkout; no tool source edits.
- g0 entry point `da863b9b67`. Other concurrent g0 commits/changes were preserved; this package is isolated under `kani3300/ch8-s1/s1-04/` relative to kani-k1. The g0 package identity is the commit containing this HANDOFF, reported in the final READY line.

Changes and checks:

- Four heavy rows become16 exact-N roots; original source roots and full legacy metadata remain. Full union of four cases and all11 meaningful cover messages is required for each replacement. Types, arbitrary bytes/KeyLess, target/PFC, scratch/canaries/post and unwind34 preserved.
- Runner fixes source snapshots/porcelain/oracles/error reporting; explicit14 groups and subset collection; interruption fallback keeps original snapshots/exits and emits collectable UNKNOWN observations.
- 35 synthetic tests passed; the final metadata-only control report change also passed all7 package tests. Offline source/tool/request/payload/YAML/anchor closure and local control preflight passed. Independent Luna HIGH review accepted the frozen semantic candidate with limitations; see REVIEW.md and independent-review.md.
- CI-REQUEST.json mirrors the committed control request. `validate.py` repeats offline closure only. Review packets are committed-source artifacts.

Envelope: selected matrix max-parallel1 is one future authorized workflow dispatch with14 jobs, each capped180min. Full conservative envelope71540s aggregate/elapsed excluding queue, not180min for the whole workflow. Max-parallel2 option42680s elapsed/71540s aggregate, requires a changed/reviewed pin. Single-job-at-a-time alternative needs5 separate authorized dispatches and a workflow variant. See ENVELOPE.md; none of these allocations is authorized by preparation.

Next authorized stage must obtain owner GO/new full budget/window/lane, publish exact reviewed identities on the intended trigger branch, and preserve the existing coordinator/accounting controls. Collect structured receipts with control `collect.py --root JOB_ARTIFACT_DIR` for all14 jobs and `--out collected.json`; absent/invalid rows remain UNKNOWN. No message-count or symbolic/fixed-N subset grants acceptance. Actual attachment-wrapper IDs, named success/cover correlation, exception roles, measured fixed-N cost and R8 remain pending.
