# Proposed commit consolidation

Base: `bf9c58e662fd65c64381ef2ac97a6397ffc0693a`.
Final tree: `d5f072f2bcf61a04d84bb0e8b54115f3011252fc`.

Prefer two commits so implementation and regression coverage can be reviewed separately:

1. **Preserve memory initialization checks at unresolved calls**
   Combine the production changes from `751603f96fde4e7d2b9462331380f6204ffe9ce4` and `500eae8aa28b373fd9a6ff7827257002a039fa5a`: retain the current target on resolution errors, classify instance kinds explicitly, follow MIR-backed shims, and make the local visitor own unsupported-call checks. This commit contains the four changed files under `kani-compiler/`.
2. **Add regression coverage for unresolved call instrumentation**
   Combine the final test changes from `835cb4a09c4e94ac6b531d20e68f9deee7262ce1`, `29bde289d60d9f6f36c16310f6bce697338f7641`, and `d5f072f2bcf61a04d84bb0e8b54115f3011252fc`: all 20 Rust fixtures and 20 final expected-output files under `tests/expected/uninit/unresolved-calls/`. Include the corrected editions, raw-byte pending-operand fixtures, and bodyless-shim expectations directly, without intermediate expectations.

A single commit named **Preserve memory initialization checks at unresolved calls** is also suitable: combine all five commits and retain the same final tree. Neither option includes the fork's separate CI-only workflow commit.

This is a proposal only. No history has been rewritten, and no Kani commit has been created or pushed during this drafting stage.
