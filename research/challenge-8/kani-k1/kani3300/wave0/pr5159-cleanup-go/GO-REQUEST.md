# PR5159 cleanup — one full standard fork CI

**ROOT AGREE** for one push-triggered full standard campaign on new fork branch `Tiramisu-Cake/kani:cleanup/pr5159-20261119`.

- Exact reviewed NONSKIP source: `282d007d06a2fc45ca6e6dc719a305f333b63a7c`
- Tree: `7a7103421211001791f2b01a5d06f3f5846e0b42`
- Sole parent / unchanged original PR head: `78f745bb696c85095a9582f959d4854ec494c4f5`
- Author package: `88948daa1d268da8915f6a870c984859afe551f4`
- Independent committed APPROVE: `b26412da5c883db53a86eb85b7ae0fa5ead67ecb`

Root verified the clean worktree, exact one-commit ancestry and five-file boundary. Both original semantic-negative reason bodies are intact; the new named headers and complete 0/1/1 summaries strengthen them. Only three file-level comments change in Rust; all eight proofs and the whole compiler, library, workflow, runner and script trees remain unchanged.

Push this exact source commit once to the new ref. No sibling is needed; do not push the skip-ci g0 packaging commit. Immediately before push, recheck exact source/tree/parent and new-ref absence. If the branch or campaign already exists, inspect it and do not duplicate. The coordinator handles dispatch and the item-1 ledger row; root performs neither. Actual future run IDs are UNKNOWN until dispatch.

The authorization covers the unchanged full Kani workflow (all five OS regressions, docs, LLBC, benchcomp and perf), both Format jobs and Deny: twelve expected native instances across three workflows. **No manual rerun authorized.** Existing internal workflow behavior stays unchanged.

This grants no push to `fix/volatile-zst-5072`, live PR/body/comment update or publication. Those require the owner's later command and current review/CI/head gates. After all three workflows terminate, retain actual suite conclusions and the specific negative-oracle evidence in a bounded intake. Historical perf instability is not an advance waiver.

Native validation remains NOT_RUN before this campaign. The inherited substring oracle still does not prove crash freedom or enforce an exact exit/transcript; source/static preservation and synthetic review checks establish no new native PASS. PR5183 requires its own final review and GO.
