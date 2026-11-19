# PR5176 cleanup — one full standard fork CI

**ROOT AGREE** for one push-triggered full standard campaign on new fork branch `Tiramisu-Cake/kani:cleanup/pr5176-20261119`.

- Exact source: `06e1533360605f52f82c69764dc4940b7afcc21b`
- Tree: `71a429da6e114fb4fd34f20605b47590d60a62c8`
- Sole parent / unchanged original PR head: `3d9a1809388f74c62ea9fb7320e123db0b8b37fa`
- Independent APPROVE: `a522e9fa611b462b698c28939cb0025f213f1f19`

Push the exact reviewed NONSKIP source commit once; a sibling and the g0 packaging commit are not needed. Immediately before push, confirm the identities and new-ref absence. If the branch or campaign already exists, inspect it and do not create a duplicate. Root does not push, launch or account; coordinator records the item-1 ledger row and actual run IDs.

Run the unchanged full Kani workflow (all five OS regressions, docs, LLBC, benchcomp and perf), both Format jobs and Deny: twelve expected native instances across three workflows. **No manual rerun authorized.** Existing internal workflow behavior remains unchanged.

14 proof bodies retained, 7 cover sites, source invocations 12+1+1; original main exact prefix; whole compiler/runner/workflows unchanged. Native discovery and oracle execution remain NOT_RUN.

This GO authorizes no update to `fix/zst-union-codegen-v4`, PR body or comments. Those need the owner's later command and current review/CI/head gates. Native results must be assessed on this exact revision; static preservation and older CI do not establish PASS. Historical fork-perf failures are not an advance waiver. After all workflows terminate, hand off a bounded factual intake.
