# KANI3300 A3R — final independent static review

## Identity

- Baseline: `585c93b2ff366f5723611a7ca944328ef62f40b5`
- Candidate: `a0a2386001a15fecfe2facc2f6cd87f3dee13b60` (parent: `c57314d4cf8aed4721c3170827827c6c9b9cd429`)
- Candidate tree: `72baa2f044301ce104ab9cffa52553339f51c4c4`
- Diff SHA-256: `40378b4517d13a9449c31bfe3b3da9819e195f0c8d84b6495b095ddec593cd61`
- Spec SHA-256: `ef041959f4ef9f55d05de5301813069a77fae67155d02aea3a209ff99d0b908c`
- Final packet SHA-256 supplied with the handoff: `fd43a75f92a9a66102d51eb5e37ad2d943dce274aa557b15fafe28004ec0215b`
- Initial review SHA-256: `f91b65f4aff5856ff05416413f99c447c7496687c24f923ecb606963c9361dce` (matches the packet reference).
- The candidate, tree, baseline, spec and diff identities match. All 27 file hashes in the final packet inventory match.

## Verdict: PASS — static review

**Initial finding: closed.** In `uninit_visitor.rs:532-545`, `Intrinsic::Forget` is handled explicitly before the new shadow-value guard. Every other intrinsic with a shadow-carrying argument or return now receives `Unsupported` before `can_skip_intrinsic` or pointer-effect handling. This closes the `BlackBox` gap: its by-value identity copy cannot silently bypass shadow-state transfer. Nonshadow BlackBox still reaches the safe skip arm; explicit pointer models remain reachable when the value types themselves are not shadow-carrying. Unknown intrinsics continue to fail closed through the existing unsupported arm.

The ordinary-call protocol guard remains restricted to non-intrinsics. Non-Item, shim, foreign, and bodyless ordinary shadow transfers therefore remain unsupported. The return `LoadArgument` is still limited to paired ordinary calls. No signature/count/index/layout/mandatory-return or leftover-protocol assertion was removed or weakened; the changed written-count checks still require exactly one write for return zero and exactly `argument_count` writes for positive argument selection.

The final delta is confined to `uninit_visitor.rs`; the earlier reviewed `mem_init.rs` protocol changes and custom MIR fixture edits are unchanged. Snapshot-before-reset ordering and exact-place `Call(Move)` clearing remain as reviewed initially. Pinned custom MIR accepts `UnwindUnreachable` on `Call`, and the fixture still uses the Kani abort panic strategy. Assertions, harnesses, and expected goldens remain unchanged by the final delta.

The delta adds the `shadow_return` local; it introduces no imports, API signatures, or enum variants. No changed-line source issue was identified for clippy/`-D warnings`; this is source inspection, not a compiler result.

## Limits

Static review only. Compilation, formatting/clippy execution, Kani, CBMC, Miri, and CI were not run. The original extra-uninitialized-read reports and their resolution are not established by this review; coordinator validation remains required. No proof credit is claimed; Cloud spend is `$0`.
