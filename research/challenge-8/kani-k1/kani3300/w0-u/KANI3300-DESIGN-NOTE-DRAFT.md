# RFC draft: initialization tracking for MaybeUninit storage and selected MIR bodies

Owner-only [#3300](https://github.com/model-checking/kani/issues/3300) draft, 2026-11-16; not upstream acceptance.

---

## Problem

SmallSort needs `-Z uninit-checks` to preserve scratch holes across calls and analyze selected contract/closure bodies.

## Goals and non-goals

Support `MaybeUninit<T>`, flat arrays/slices of it and `MaybeUninit<[T; N]>` with computable layouts. No new alias/provenance model or #3300 completion, permissions, general validity, all-T/N, panic/unwind or sorting proof is claimed.

## Source decomposition and dependencies

Base: upstream `0aac16ef62da9e9d5645782d458593e5d78143ba` plus existing [#5172](https://github.com/model-checking/kani/pull/5172), `6fe484b30043b3696b5f1ccc4bea0e42891ad012` (unresolved-call checks).

| Slice | Scope | Source head |
|---|---|---|
| PR-01 | Selected bodies, cycles, entry slots | `d82752c8bc878398e672bffaa631ca6a28430acc` |
| PR-02 | Immutable masks, automatic-harness entry reset | `05da1a7a8ce7921d3f685d9595eab797870ca629` |
| PR-03 | Nested layouts/raw equality | `5ca51679e3f433718807a2e44add0d5abac128e7` (historical) |
| PR-04 | Storage/direct-call transfers | `345cedfd67df679e326474385308349d609fc43d` (historical) |
| PR-05 | Closure capture masks | `96f5d5dc8dedd369c6986a4f1dd5e698b6167f0f` (historical) |
| PR-06 | Fixtures/documentation | `3f5242bb1539fb88196d7e503b722f0905f2b46c` (historical) |
| PR-07 | Delayed-body restoration | `8e299aa6243bc5f06a29c51e98aafa9564478220` (historical) |

PR-02 adds one reset-fix commit to `932fb8395a58f8c86c0d702ba2cae835823b2962`. PR-03–07 await rebuilding/revalidation over it; listed heads are historical. Review/merge order: #5172 → PR-01 → … → PR-07; stacked diffs include unmerged parents.

Separate `select_unpredictable` Rust-fallback source `14bc57fdb99960240c4944845a3d985c8af4dcf7` has historical PR-07 as parent; its results do not qualify the seven slices or revised PR-02.

## Proposed architecture and actual behavior

### One witness, distinct masks

The model tracks one nondeterministic object/byte witness. Initialization masks distinguish holes from initialized zeros; layout masks select payload, excluding padding. Typed transfers initialize payload; raw copies preserve full byte state, deinitialization clears the full extent, and `raw_eq` checks padding. Copy snapshots precede Move deinitialization. Layout never establishes initialization.

### Direct calls and selected bodies

Ordinary non-foreign MIR calls, excluding Kani hooks, pair signature/argument-index/return-slot transfers on normal returns. Reject unsized storage before partial transfer; retain supported conservative resets on unpaired paths.

Selected contract/discarded-closure analysis retains provenance, root-local snapshots, fallible resolution and operand checks. Cycles abort the root and discard incomplete graphs. Ordinary sized scalar/reference entry slots, not pointees/unions, are initialized. Closure masks use actual capture layouts, including empty zero-byte masks.

### Immutable origins and permissions

Seeding requires whole emitted storage, offset zero, matching extent, no relocations, supported `Freeze` origin and exact mask. Aliases require matching storage/layout/mask; conflicts are rejected. Reset precedes seeding, including automatic argument/contract harnesses; false bits survive, empty masks need no query. Other origins gain no initialization or permission.

### Delayed mutation and per-root isolation

A journal restores delayed replacements on model exit/failure, apart from regular/stub changes/provenance. Both backends guard reachability/global passes/codegen. Six cache/two scope units and 11 invocations/18 mixed-versus-isolated comparisons support tested restoration, not universal isolation or semantic equivalence.

## Alternatives and open design choices

All-true masks erase holes; all-false seeds reject constants. This retains one witness rather than per-allocation shadow memory. Indirect/recursive/Replace/loop-havoc summaries need further rules and controls.

## Evaluation and evidence

Fork runs use source-specific CI overlays; no organizer integration or independent proof credit.

PR-01 [run](https://github.com/Tiramisu-Cake/kani/actions/runs/43696666260): build/format/Clippy, 9 cycle units, 302 regressions/9 ignores; new end-to-end analysis tests deferred. Original PR-02 [run](https://github.com/Tiramisu-Cake/kani/actions/runs/43701587141): 9 registry units, 308 regressions/9 ignores, six descriptor cases.

Reset-fix [run 43783429976](https://github.com/Tiramisu-Cake/kani/actions/runs/43783429976), tested source `f7e89f1942fa6f671f20ec45fde98d9d736dc122`: build/format/Clippy, 66 compiler units, 56 uninit and 134 contract tests passed (2/4 ignored). Six retained reset cases passed; three seeded cases failed on old PR-02 with missing reset. Autoharness: 54 passed/1 failed (padding-read fixture unexpectedly verified). That fixture was removed; compiler/retained fixtures are byte/mode-identical. Final head was not rerun; no complete-suite pass is claimed.

Deferred analysis/layout/storage: historical PR-04 ([43710024495](https://github.com/Tiramisu-Cake/kani/actions/runs/43710024495)); closure/contracts: PR-05 ([43715788377](https://github.com/Tiramisu-Cake/kani/actions/runs/43715788377)); restoration/LLBC/regressions: PR-07 ([43723531871](https://github.com/Tiramisu-Cake/kani/actions/runs/43723531871)).

Historical seven-slice [run](https://github.com/Tiramisu-Cake/kani/actions/runs/43665002636): 33 stages per Linux x86/Arm and macOS platform. Bounded sort4 stopped at `select_unpredictable`, return unreachable.

Separate fallback [regressions](https://github.com/Tiramisu-Cake/kani/actions/runs/43744142824) 33 stages/platform; rounded time 41/40/76 minutes, RSS unknown. Bounded [replay](https://github.com/Tiramisu-Cake/kani/actions/runs/43751703000) used std `70ba5befc617627073738e26cb1466bd4fb76e41` plus test overlay `6075e7ce17179f45642c9ffe8fe09e3ec9395726`, uninit ON/value checks OFF, object-bits12, controls ON, `--no-assert-contracts`. Merge u64 len8/scratch48/src32/dst0, merge-closure u8 N9/scratch48, sort4 u64 and swap u64/backing4 reached return/all covers (unwind34/34/16/8). Raw sort4 passed initialized; source[1] hole retained exactly the intended uninitialized-u64-read failure, exit1/return covers (unwind16). Replay timing/RSS unknown; no sorting theorem.

## Independent sorting contracts and integration

Stock-upstream sorting uses primitive/default ordering, uninit/value OFF, checked trait methods, thresholds16/32 and proposed symbolic lengths/six-body coverage. [#752](https://github.com/model-checking/verify-rust-std/pull/752) remains separate; its older std head needs upstream toolchain updates before using `0aac`. Arbitrary-bool closure safety and functional results require compatible sources/targets/comparators/modes/flags before combination.

## Limitations

Unsupported here: struct-held arrays of `MaybeUninit` (`PolymorphicIter`), `array_assume_init` transmute; other boundaries: nested by-value union aggregates, function-pointer/vtable calls, Replace/recursion shadow transfers, delayed cycles and unmodeled intrinsics. Loop-havoc/shadow remains open; see [#5179](https://github.com/model-checking/kani/issues/5179), [#5181](https://github.com/model-checking/kani/issues/5181) and the separate [valid-value copy limitation](https://github.com/model-checking/kani/issues/3762#issuecomment-6911595935). #5104, general validity and organizer time/RSS fit remain open.

## Questions for maintainers

1. Is this model and review decomposition acceptable?
2. Which body/origin/isolation controls are missing?
3. What Replace/recursion or loop-havoc shadow summary could preserve every hole witness?
4. How should fixes/integration accompany stock-upstream sorting?

*Disclosure: this note was prepared with the help of AI assistants.*
