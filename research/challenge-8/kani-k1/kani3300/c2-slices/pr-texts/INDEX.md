# C2 stack — PR drafts and submission order

Prepared from g0 `82c6926dd6`. Drafts only: no fork branches, push, CI dispatch or publication is performed here.
The seven commits reconstruct the accepted source tree exactly. Each PR body is English; `Title:` is the proposed PR title, not part of the body.

## Fixed inputs

- Upstream base: `0aac16ef62da9e9d5645782d458593e5d78143ba`.
- Existing dependency: #5172, `6fe484b30043b3696b5f1ccc4bea0e42891ad012`. It is in review, not merged; do not submit it again.
- Final source: `8e299aa6243bc5f06a29c51e98aafa9564478220`.
- Final tree: `9829702c1aa0ecb73c860fc0ad5451757917d6cb`, identical to the accepted export `ad499e41dd2db9ccd432f89721638a1f3a0bbd44`.
- Source/qualification authority: [final acceptance](../slice-07/ci-43723531871/ACCEPTANCE.md). Earlier local SLICE/REVIEW metadata marked NOT_RUN is superseded by the coordinator's per-head acceptances.

## Order and exact-head evidence

| Draft | Source commit | Immediate parent | Fork qualification | What that run establishes |
|---|---|---|---|---|
| [PR-01](PR-01.md) — selected-body analysis | `d82752c8bc878398e672bffaa631ca6a28430acc` | B1 `6fe484b300` | [43696666260](https://github.com/Tiramisu-Cake/kani/actions/runs/43696666260) | Regression suites and ActiveCalls units only; integration follows at 4/5 |
| [PR-02](PR-02.md) — immutable masks | `932fb8395a58f8c86c0d702ba2cae835823b2962` | PR-01 | [43701587141](https://github.com/Tiramisu-Cake/kani/actions/runs/43701587141) | Registry units, descriptor/coalescing cases and cumulative regressions |
| [PR-03](PR-03.md) — raw equality/layout | `5ca51679e3f433718807a2e44add0d5abac128e7` | PR-02 | [43706759714](https://github.com/Tiramisu-Cake/kani/actions/runs/43706759714) | Regression only; raw-equality and nested-layout integration follows at 4 |
| [PR-04](PR-04.md) — storage and transfer protocol | `345cedfd67df679e326474385308349d609fc43d` | PR-03 | [43710024495](https://github.com/Tiramisu-Cake/kani/actions/runs/43710024495) | Storage/transfer, Copy/Move, masks, resets and hook controls; closes deferred 1/3 cases runnable here |
| [PR-05](PR-05.md) — closure masks | `96f5d5dc8dedd369c6986a4f1dd5e698b6167f0f` | PR-04 | [43715788377](https://github.com/Tiramisu-Cake/kani/actions/runs/43715788377) | Capture/contract/mode cases close remaining obligations; 4/4 sensitivity with one manual review |
| [PR-06](PR-06.md) — edge tests and documentation | `3f5242bb1539fb88196d7e503b722f0905f2b46c` | PR-05 | [43720042056](https://github.com/Tiramisu-Cake/kani/actions/runs/43720042056) | Eleven edge fixtures, docs, cumulative regressions and automated 4/4 sensitivity; no production-code delta |
| [PR-07](PR-07.md) — delayed-body isolation | `8e299aa6243bc5f06a29c51e98aafa9564478220` | PR-06 | [43723531871](https://github.com/Tiramisu-Cake/kani/actions/runs/43723531871) | Cache/scope units, 18 structural comparisons, LLBC build, cumulative regressions and 4/4 sensitivity |

The runs above use CI-only overlays bound to the listed source commits; those overlays are not PR content.
The first six are bounded Linux qualification, not the full three-platform regression run.
All deferred obligations are now closed for the tested cumulative stack. Their attribution stays explicit: the tests did not execute on the earlier PR-01/PR-03 source heads.

## Submission triggers

1. Check the actual status/head of #5172 and current upstream before publication. Keep the validated U+B1 stack immutable; do not silently rebase it or change the submitted dependency.
2. Default order: #5172 → PR-01 → PR-02 → PR-03 → PR-04 → PR-05 → PR-06 → PR-07. After each parent merges, compare its actual merged patch with the pinned dependency, then prepare the next PR against the fixed current upstream. A squash changes commit ancestry, so compare changes and resulting trees as well as SHAs.
3. The owner may instead request stacked Drafts while parents are still pending. Their descriptions must retain the dependency and cumulative-diff notice; this preparation does not create those branches or PRs. Before publication replace literal `PR-01`…`PR-06` placeholders with actual PR numbers. Do not invent numbers or leave a ready-for-review body implying a single-commit diff when parents are still included against `main`.
4. Ready-for-review requires the intended parent/diff, its exact-head qualification and the recorded deferred-integration evidence to remain applicable. For PR-01 cite the successful dependent runs at PR-04/05; for PR-03 cite PR-04. Do not relabel their own regression runs as integration tests.
5. On rebase, maintainer-requested source/test changes or a changed parent patch, record the new SHA/tree and review the semantic diff. Coordinate the affected Quick/replay/platform checks before reusing readiness claims; prior run URLs are historical evidence for their exact source, not receipts for a new tree. A history-only rewrite preserving the exact tree does not change that tree's regression evidence.
6. After publication, update each remaining draft's dependency number and diff notice. Refs #3300 remains appropriate: no individual PR, nor the combined stack, closes the full issue. Do not replace it with Resolves #3300.

PR-07 is a separate restoration change; it was not folded into the storage PR. The select-unpredictable extension is outside this stack and needs its own reviewed candidate and validation. It is not a reason to expand these drafts' claims.

## Final-tree evidence and scope

The source tree after PR-07 exactly matches the previously accepted export:

- [43665002636](https://github.com/Tiramisu-Cake/kani/actions/runs/43665002636): full `scripts/kani-regression.sh`, 33 ordered stages on each of ubuntu-24.04, ubuntu-24.04-arm and macos-15; all exit zero.
- [43683557088](https://github.com/Tiramisu-Cake/kani/actions/runs/43683557088): bounded closure-comparator replay, two merge SUCCESS rows and sort4 at the expected `select_unpredictable` boundary. This does not qualify the generic function-pointer profile or the whole SmallSort module.

These results apply to the final tree, not automatically to the individual intermediate PRs. They are regression/bounded verification evidence, not completion of #3300.

The combined experimental domain covers a `MaybeUninit<T>` slot, flat `[MaybeUninit<T>; N]` / `[MaybeUninit<T>]`, and `MaybeUninit<[T; N]>` where Kani can compute payload masks. It distinguishes raw copies from typed payload-byte transfers and supports paired direct MIR-body calls. Whole immutable origins use qualified exact byte masks.
Indirect/function-pointer/trait-object calls, by-value nested union/MaybeUninit aggregates, shadow transfer under `stub_verified` or `kani::recursion`, delayed-analysis call cycles, and intrinsics without an initialization model remain unsupported or documented limitations. In particular, `select_unpredictable` still prevents the whole SmallSort module from being verifiable under `-Z uninit-checks`.

Every PR retains the license confirmation and the required disclosure. No coauthor trailer is added. Owner publication is a separate action.
