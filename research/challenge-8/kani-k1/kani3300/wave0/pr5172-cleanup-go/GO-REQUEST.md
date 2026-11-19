# PR5172 cleanup — one full standard fork CI

**ROOT AGREE** for one push-triggered full standard campaign on new fork branch `Tiramisu-Cake/kani:cleanup/pr5172-20261119`.

- Exact source: `fef46d2d9d65bf3eb91a282da004043ecd26a208`
- Tree: `2e6c41da31c3e5a96a9a7d39efa8eb93e6c973e7`
- Sole parent / unchanged original PR head: `80e5d6fabc0103b0b3117440007ad2d9475f9a9c`
- Independent APPROVE: `2a5d5af7503c1812a1f8b9319b28dbd6c391ea42`

Push the exact reviewed NONSKIP source commit once; a sibling and the g0 packaging commit are not needed. Immediately before push, confirm the identities and new-ref absence. If the branch or campaign already exists, inspect it and do not create a duplicate. Root does not push, launch or account; coordinator records the item-1 ledger row and actual run IDs.

Run the unchanged full Kani workflow (all five OS regressions, docs, LLBC, benchcomp and perf), both Format jobs and Deny: twelve expected native instances across three workflows. **No manual rerun authorized.** Existing internal workflow behavior remains unchanged.

24 harnesses in identical 22 independent root sources; helper operations and all effective oracles preserved. Compiler code unchanged except exact corrected comment; shim-negative follow-up and adapter refactor remain outside scope. Native post-relocation behavior remains NOT_RUN.

This GO authorizes no update to `fix/kani-uninit-unresolved-call-v3`, PR body or comments. Those need the owner's later command and current review/CI/head gates. Native results must be assessed on this exact revision; static preservation and older CI do not establish PASS. Historical fork-perf failures are not an advance waiver. After all workflows terminate, hand off a bounded factual intake.
