# G1R5 independent static review — final candidate

- Baseline: `5b2265c41d6e06472cbc448c2a6f2df4389261a2`
- Candidate: `4914c6c2d737e068c5a30547120d15dfb56e7a15` (tree `8f38753e0b9403a4e766e1663eb7f855ba0533b0`)
- Review packet SHA256: `14a174d9181e58da8fbc67a9c966748709f98af7f1f5371c77e4e6dac68c3bfc`
- Diff SHA256: `2f5b23c33f46fa5c1e75500f92469cbb26798b21786a15636593afbf6d00f095`
- Normalized spec SHA256: `3b4b9e12ce822a87df47d72f30a5509effc5aa653d545b925d7290addbe3a112`

## Findings

No unresolved static blocker found in the final packet. The stale-golden finding from review of candidate `bdd46381220994e06e90c5a15d30b1db564abc63` is resolved in this candidate: the four whole/argument moved-source harnesses were moved to the positive suite, and their negative expected failures were removed. Their four harness bodies are preserved and exercise the documented no-source-invalidation policy. Negative expected count is now 60; positive expected count is 67.

## Scope reviewed

- Confirmed the original positive suite source is preserved byte-for-byte as a prefix (17,414 original bytes); only the four moved harnesses and their small helper/comment block are appended. No existing positive harness was weakened.
- The negative-suite diff removes only the four moved source-read cases and six task-named move-source cases, their failure entries, and the resulting count. The other negative harnesses and expected diagnostics remain intact.
- Emitter/model arities agree statically after removal of moved-source state: `StoreArgument(from, selected_argument)` and `CopyInitStateSingle(from, to, preserve)` match model signatures. Union shadow transfer/masks and the paired argument/return protocol remain. `Forget` retains its no-effect handling; its prior source-clear instrumentation is gone. No orphan argument store or remaining reference to removed move-tracking state was found. `MirVisitor` remains used by `CheckUninitVisitor`; no obvious unused-item `-D warnings` hazard was found by inspection.
- The unresolved-callee branch emits `Unsupported` only if an argument or destination touches tracked union shadow. The delayed-UB source and golden are unchanged dependencies, so unrelated function-pointer calls retain their delayed-UB diagnostic path.
- The forget-array fixture uses `[U; 1]`; the unchanged expected text matches the `UnionAsField` guard reached for the nonempty array.
- The unexecuted padding reduction remains a plausible four-way reduction (typed copy vs argument/return, C vs Rust union) that writes bytes before transfer and reads the `repr(C) Padded` interior padding byte. Static review cannot establish why the original four harnesses abort with CBMC status 134. Plausible discriminators remain typed-copy goto/byte-update generation, paired argument-buffer ABI instrumentation, and padding-byte pointer/read lowering. The candidate makes no speculative production fix and retains all four original padded failures.

## Limits

Read-only review. No rustfmt, `-D warnings`, compilation, Kani, CBMC, or CI was run; runtime remains **NOT_RUN** and this review gives no proof credit or GO decision. The required research NOTES/RESULT artifacts are outside this packet and were not assessed as committed inputs.
