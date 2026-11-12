# Kani B1 and B3 — combined external audit brief

Snapshot: 12 November 2026. These are two independent upstream bug-fix candidates on clean Kani `bf9c58e662fd65c64381ef2ac97a6397ffc0693a`, not on the experimental MaybeUninit Part 1 or G1 patches.
The purpose is to decide whether each is ready for an upstream PR, which claims need correction, and how to package the changes. Part 1 remains paused pending its separate audit.
Research links refer to verify-rust-std branch `experiment/kani-k1-kani3300t0-20261111` @ `950fe1f288c4c56e961a7c40bf240a826bd36cbc`. Compiler/test links point to the B1 or B3 candidate head named in the table. Diffs: [B1](https://github.com/Tiramisu-Cake/kani/compare/bf9c58e662...d5f072f2bcf61a04d84bb0e8b54115f3011252fc), [B3](https://github.com/Tiramisu-Cake/kani/compare/bf9c58e662...6db3c4dabd4a368314eb8e2b71d21d1eee721593).
Evidence below combines saved stage records, source inspection and coordinator-supplied CI facts. No CI, compiler, verifier or build was run for this brief; no raw logs or archives were accessed.

| Candidate | Fork branch / exact head | Scope |
|---|---|---|
| B1 | `fix/kani-uninit-unresolved-call` @ `d5f072f2bcf61a04d84bb0e8b54115f3011252fc` | Preserve initialization instrumentation around unresolved calls; classify unsupported calls explicitly. |
| B3 | `fix/zst-union-codegen` @ `6db3c4dabd4a368314eb8e2b71d21d1eee721593` | Avoid a CBMC abort when a padded union wrapper contains a zero-width array payload. |

## 1. B1 — unresolved-call instrumentation

### Upstream defect and manifestation

With `-Z uninit-checks`, `CheckUninitVisitor::visit_terminator` visits call operands and collects operations into a current target. In the base error path, `try_resolve_instance` returning Err causes another operand visit and an early return before the shared epilogue publishes that target.
This drops the unsupported-call diagnostic and previously collected operations. When the call is the terminator of a statement-free entry block, union argument entry `LoadArgument` operations can be lost with it; operand read checks can also disappear.
Separately, `Virtual`, `Shim` and `LlvmIntrinsic` instances fell through a catch-all branch. Function-item resolution could unwrap an error. Delayed-UB checks did not provide a context-independent replacement for the lost local checks.
The PR draft includes a runtime/optimized custom-MIR example: a partially initialized `Word { byte: 42 }` is passed to a helper whose empty entry block calls a function pointer with `value.word` as the operand. This fixes the placement of the union read and entry loads in the affected target.
This is a source-backed candidate reproducer. The available records do **not** establish an observed clean-base `VERIFICATION SUCCESSFUL` for that exact example; a reachable false-success claim needs a matched baseline result. The fixed fixtures require the read check and Unsupported diagnostic to remain present.
Source: [local visitor](https://github.com/Tiramisu-Cake/kani/blob/d5f072f2bcf61a04d84bb0e8b54115f3011252fc/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs) @ base and `d5f072f2b`; [PR draft](https://github.com/Tiramisu-Cake/verify-rust-std/blob/950fe1f288c4c56e961a7c40bf240a826bd36cbc/research/challenge-8/kani-k1/kani3300/b1pr/PR-DRAFT.md).

### Fix, commits and exclusions

- `751603f96`: visit operands once; retain the target on resolution failure and use the common publishing epilogue; explicit call classification and diagnostic ownership.
- `835cb4a09`: add 20 regression fixtures, paired with and without delayed-UB analysis seeds.
- `500eae8aa`: follow MIR-backed shims like ordinary callees, including union argument transfer; reject bodyless Shim, Virtual and LlvmIntrinsic paths explicitly.
- `29bde289d`: correct custom-MIR editions and shim-call coverage; `d5f072f2b`: repair four fixture/expected-output files, without another production change.
The local visitor now owns function-pointer/virtual Unsupported checks; the delayed visitor no longer duplicates them. Function-item resolution errors become diagnostics rather than unwrap panics.
The final diff is four production files plus 20 Rust fixtures and 20 expected-output files, +767/−26. It does not implement general function-pointer/vtable effects, arbitrary shim models, Part 1 storage support, realloc effects or G1.
The affected production files are [points_to/mod.rs](https://github.com/Tiramisu-Cake/kani/blob/d5f072f2bcf61a04d84bb0e8b54115f3011252fc/kani-compiler/src/kani_middle/points_to/mod.rs), [points_to_analysis.rs](https://github.com/Tiramisu-Cake/kani/blob/d5f072f2bcf61a04d84bb0e8b54115f3011252fc/kani-compiler/src/kani_middle/points_to/points_to_analysis.rs), [delayed visitor](https://github.com/Tiramisu-Cake/kani/blob/d5f072f2bcf61a04d84bb0e8b54115f3011252fc/kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/instrumentation_visitor.rs), and the local visitor above.

### Tests and execution evidence

Ten cases have plain/seeded variants: direct positive call, function pointer, erased pointer, wrapped pointer, escaped global pointer, trait-object call, shim call, pending operand read, initialized union entry argument and partially initialized entry argument.
The seed is a safe `copy_nonoverlapping` operation. The pairs check that rejection/retained operations do not depend on delayed-UB targets. New fixtures declare `-D warnings`.
Pending-operand controls use a raw two-byte allocation with only one byte initialized. Entry controls place the union read in the custom-MIR call terminator. Named expectations distinguish an initialized read that succeeds from a partial read that fails, while both indirect cases retain Unsupported.
References: [B1 notes](https://github.com/Tiramisu-Cake/verify-rust-std/blob/950fe1f288c4c56e961a7c40bf240a826bd36cbc/research/challenge-8/kani-k1/kani3300/b1/NOTES.md), [B1R notes](https://github.com/Tiramisu-Cake/verify-rust-std/blob/950fe1f288c4c56e961a7c40bf240a826bd36cbc/research/challenge-8/kani-k1/kani3300/b1r/NOTES.md), [B1R2 result](https://github.com/Tiramisu-Cake/verify-rust-std/blob/950fe1f288c4c56e961a7c40bf240a826bd36cbc/research/challenge-8/kani-k1/kani3300/b1r2/RESULT-KANI3300-B1R2.md), [entry partial fixture](https://github.com/Tiramisu-Cake/kani/blob/d5f072f2bcf61a04d84bb0e8b54115f3011252fc/tests/expected/uninit/unresolved-calls/entry-partial-plain.rs), [initialized companion](https://github.com/Tiramisu-Cake/kani/blob/d5f072f2bcf61a04d84bb0e8b54115f3011252fc/tests/expected/uninit/unresolved-calls/entry-initialized-plain.rs), [pending operand](https://github.com/Tiramisu-Cake/kani/blob/d5f072f2bcf61a04d84bb0e8b54115f3011252fc/tests/expected/uninit/unresolved-calls/pending-ops-plain.rs).

| Run | Recorded result |
|---|---|
| `43104793815` | Initial B1 exposed regressions from rejecting all shims and missing Rust 2021 flags in custom-MIR fixtures. |
| `43108072253` | B1R restored the production regressions; four fixture/golden problems remained. |
| [43110714635](https://github.com/Tiramisu-Cake/kani/actions/runs/43110714635) | Focused gate passed: kani 22, expected 83, ui 14, script 1; format/build/Clippy passed. Workflow-only head `0e83acc6823d…` has candidate `d5f072f2b` as parent. |
| [43112332778](https://github.com/Tiramisu-Cake/kani/actions/runs/43112332778) | Full CI at `d5f072f2b`: Ubuntu 22.04/24.04/24.04-arm and macOS-15-intel regression jobs, perf/LLBC/docs/benchcomp passed. macOS-14 did not execute; the overall workflow is cancelled. |

The focused counts and cancellation explanation are coordinator facts; the saved text review checked available job metadata, not raw logs. No paired execution of the exact base example is recorded here. No dedicated LlvmIntrinsic fixture is present.

### PR-draft accuracy and packaging

The [draft](https://github.com/Tiramisu-Cake/verify-rust-std/blob/950fe1f288c4c56e961a7c40bf240a826bd36cbc/research/challenge-8/kani-k1/kani3300/b1pr/PR-DRAFT.md) matches the final target-retention/classification changes and correctly says function-pointer/vtable effects remain unsupported. It refers to tracking issue #3300 without claiming to close it.
The illustrative example and fixed expected outputs support the proposed mechanism; they must not be described as a measured base false-success result without that evidence.
A remaining precision issue is the shim route: [shim-plain.rs](https://github.com/Tiramisu-Cake/kani/blob/d5f072f2bcf61a04d84bb0e8b54115f3011252fc/tests/expected/uninit/unresolved-calls/shim-plain.rs) says it follows a bodyful FnPtrShim to an inner function-pointer call, while its golden reports a **bodyless Shim**. The draft cautiously describes the encountered chain, but actual InstanceKind/has_body provenance is needed to settle the comment and coverage claim.
The [existing text review](https://github.com/Tiramisu-Cake/verify-rust-std/blob/950fe1f288c4c56e961a7c40bf240a826bd36cbc/research/challenge-8/kani-k1/kani3300/b1pr/REVIEW.md) found the draft accurate within its stated evidence limits; this brief highlights the baseline and shim questions for the independent auditor.
The [commit proposal](https://github.com/Tiramisu-Cake/verify-rust-std/blob/950fe1f288c4c56e961a7c40bf240a826bd36cbc/research/challenge-8/kani-k1/kani3300/b1pr/COMMITS.md) suggests two logical commits: all four production-file changes, then all final fixtures/goldens. One cohesive squash is also reasonable. Neither should retain intermediate incorrect expectations or include the CI-only workflow.

## 2. B3 — zero-sized union backend payload

### Upstream defect and manifestation

This reproduces on clean upstream with default checks, **without** `-Z uninit-checks`: a union such as `union U { bytes: [u8; 8], zst: [(); 2] }` is copied through `ptr::read`/`ptr::write` after initializing its bytes, and CBMC aborts with status 134.
The backend wraps a smaller union arm in a struct padded to the union width. A zero-sized array arm creates a nonzero-width wrapper containing a zero-width array member; byte-operation lowering cannot reconstruct that array from the wrapper bitvector.
The regression is independent of experimental MU/G1 instrumentation. The recorded base-versus-fix runs below establish the default-check abort and successful repair for the tested cases.

### Fix, commits and exclusions

`dc590936c` adds the initial paired tests; `9dddcb113` changes the physical payload of a zero-sized arm inside a padded wrapper to the registered empty-unit struct; `6db3c4dab` places the seven default-check tests in `tests/expected/zst-union-arm`.
Only the `padding > 0` wrapper branch changes. The logical `UnionField` type is retained by `DatatypeComponent::unionfield`; the padded physical type retains the existing width. Nonzero payloads and no-padding/all-ZST unions follow their existing paths.
The final diff is three files, +184/−2: one production hunk in [codegen/typ.rs](https://github.com/Tiramisu-Cake/kani/blob/6db3c4dabd4a368314eb8e2b71d21d1eee721593/kani-compiler/src/codegen_cprover_gotoc/codegen/typ.rs), [main.rs](https://github.com/Tiramisu-Cake/kani/blob/6db3c4dabd4a368314eb8e2b71d21d1eee721593/tests/expected/zst-union-arm/main.rs), and [expected](https://github.com/Tiramisu-Cake/kani/blob/6db3c4dabd4a368314eb8e2b71d21d1eee721593/tests/expected/zst-union-arm/expected).
No cprover_bindings, general field/index lowering, uninit shadow model or validity policy is changed. Logical/physical type compatibility across projections, serialization and ABI remains an audit obligation, not something inferred solely from the small diff.

### Tests and execution evidence

The seven harnesses cover byte-array typed copy, padded C/Rust payloads, an align(8) ZST, a containing struct placing the union at offset 8, an all-ZST union, and nondeterministic `[();2]` indexing/read/write/reference operations.
The padded examples assert data fields, not unguaranteed padding bytes. The byte-arm example covers the full extent with initialized data. Current expected output requires seven successful harnesses and zero failures.

| Run | Recorded result |
|---|---|
| [43115481098](https://github.com/Tiramisu-Cake/kani/actions/runs/43115481098) | Tests on clean base, default checks: four of seven cases abort 134 — array copy, padded C, padded Rust, nonzero-offset copy. Three controls pass. |
| [43115485052](https://github.com/Tiramisu-Cake/kani/actions/runs/43115485052) | With the backend fix, default checks: all seven pass. |
| [43117729467](https://github.com/Tiramisu-Cake/kani/actions/runs/43117729467) | Subsequent full CI reported Ubuntu 22.04/24.04/24.04-arm, perf/LLBC/docs/benchcomp PASS. macOS-15-intel was cancelled at the reported repository-invocation block; there is no macOS test result from that job. |

Sources: [B3 static audit](https://github.com/Tiramisu-Cake/verify-rust-std/blob/950fe1f288c4c56e961a7c40bf240a826bd36cbc/research/challenge-8/kani-k1/kani3300/b3/STATIC-AUDIT.md), [B3 result](https://github.com/Tiramisu-Cake/verify-rust-std/blob/950fe1f288c4c56e961a7c40bf240a826bd36cbc/research/challenge-8/kani-k1/kani3300/b3/RESULT-KANI3300-B3.md), [B3R result](https://github.com/Tiramisu-Cake/verify-rust-std/blob/950fe1f288c4c56e961a7c40bf240a826bd36cbc/research/challenge-8/kani-k1/kani3300/b3r/RESULT-KANI3300-B3R.md). Their initial NOT_RUN status predates the coordinator runs. Bind the later full run to its exact head/current test placement when finalizing the submission.

### Separate uninit-checks panic

With `-Z uninit-checks`, the seven-case variant hits a **kani-compiler panic before CBMC** at [relevant_instruction.rs](https://github.com/Tiramisu-Cake/kani/blob/6db3c4dabd4a368314eb8e2b71d21d1eee721593/kani-compiler/src/kani_middle/transform/check_uninit/relevant_instruction.rs):136, on both base and backend-fixed code. The source match arm rejects `Constant(_) | RuntimeChecks(_)` through `unreachable!()`; the triggering MIR was not inspected in the saved note.
This is distinct from the default-check CBMC abort. B3 does not fix it and must not claim working uninit instrumentation for these unions.
The [PANIC-NOTE](https://github.com/Tiramisu-Cake/verify-rust-std/blob/950fe1f288c4c56e961a7c40bf240a826bd36cbc/research/challenge-8/kani-k1/kani3300/b3r/PANIC-NOTE.md) retains the observed input at `dc590936c`, `tests/expected/uninit/zst-union-arm-uninit-checks/main.rs`. Its shorter proposed input was not executed and is not an established minimal reproducer.
The final B3R submission removes the flag-on test variant and keeps the default-check regression in the general suite. This is an explicit scope separation, not evidence that the panic disappeared. It needs separate upstream triage and a decision about Unsupported versus supported constant-operand handling.

### PR-draft accuracy and packaging

The [B3R draft](https://github.com/Tiramisu-Cake/verify-rust-std/blob/950fe1f288c4c56e961a7c40bf240a826bd36cbc/research/challenge-8/kani-k1/kani3300/b3r/PR-DRAFT.md) accurately describes the backend change, default-check reproducer and independent instrumentation panic. The seven-test coverage description matches the source.
Its statement that full CI for the relocated tests is pending is stale relative to the coordinator's later Ubuntu results. Update it with exact head, completed jobs and macOS cancellation; do not call the whole matrix green. Add the standard Apache-2.0/MIT submission confirmation line.
The targeted run supports the tested base-versus-fix contrast; it does not prove every zero-sized type, ABI or target is covered. A single clean fix-plus-tests commit is a natural upstream shape; two logical commits are also possible if tests use their final placement from the outset.
The coordinator's dated search found no dedicated upstream issue for B3. A separate issue documenting the clean-base abort may help tracking; whether it should precede the PR is an explicit question below. No issue or PR is opened by this brief.

## 3. Shared risks and readiness boundaries

- Both fixes are standalone; combining them in this audit does not imply a combined PR or that either completes #3300.
- CI job status, workflow status, test output and source explanation are different evidence. A cancelled runner is not a passing platform; an expected-output test passing does not by itself exclude every extra property failure.
- Before any history cleanup, retain exact base/candidate/test identities. A squash may preserve the final tree, but an old run must not be relabeled as a run on a new SHA. Exclude workflow-only and diagnostic iteration commits from upstream exports.
- B1's custom-MIR base verdict, shim route and untested LlvmIntrinsic branch need explicit treatment. B3's uninit panic and missing macOS execution must remain visible.
- Source-model gaps in other tracks, including Part 1, realloc and the shared-transformer cache, are not repaired by these candidates. Any dependency needed for a stated supported path must be established rather than assumed.
- Fork Actions may be blocked since 12 November 00:17 UTC according to the coordinator. No new CI is to run until the owner checks; local compiler/verifier execution is unavailable in the current workflow. Publication remains an owner decision.

## 4. Questions for the auditor, in priority order

1. **B1 completeness:** Does every unresolved-call exit now retain all previously collected operand/entry operations exactly once, with the correct insertion order and block association? Are there other early exits that still lose targets?
2. **B1 classification:** Is treating a MIR-backed Shim like Item correct for its argument ABI, union shadow transfer and body effects? Are bodyless Shim, Virtual, LlvmIntrinsic and function-item resolution errors handled comprehensively without claiming unsupported effects are modeled?
3. **Diagnostic ownership:** Is removing the delayed visitor's function-pointer/virtual guard safe whenever local instrumentation runs, including plain/seeded roots, erased pointers, wrappers, globals and calls reached inside shims?
4. **Base false-success claim:** Does the custom-MIR entry-partial example actually verify successfully on clean base, or does another guard reject it? What exact paired result is needed before claiming a measured false SUCCESS rather than a demonstrated source-level loss of checks?
5. **B1 test precision:** Which shim InstanceKind/has_body path do shim-plain/seeded actually exercise, and how should comments/draft/goldens be reconciled? Is a positive bodyful-shim case or a dedicated LlvmIntrinsic case needed?
6. **B1 matrix and scope:** Are twenty plain/seeded fixtures sufficient for preserving prior operations and rejecting unknown effects? Can redundant cases be reduced without losing the no-delayed-target and statement-free-entry distinctions?
7. **B3 correctness:** Does replacing only the zero-sized physical payload with empty-unit preserve layout width, alignment, logical field typing, projection/index behavior, serialization and call/return ABI across supported targets?
8. **B3 test sufficiency:** Do the seven cases distinguish the original zero-width-array failure from general ZST behavior? Are zero-length non-ZST arrays, additional alignments, noinline argument/return copies or other zero-sized arm forms essential before merge?
9. **B3 claim boundary:** Are all post-copy assertions valid data reads, including padded Rust-layout payloads, and do the recorded base/fix runs establish the intended backend regression independently of uninit instrumentation?
10. **B3 issue first:** Should the owner first open a focused upstream issue containing the default-check base reproducer and abort result, or submit the narrowly scoped PR directly? How should the independent uninit panic be cross-referenced without implying B3 fixes it?
11. **Panic at relevant_instruction.rs:136:** Should this become a separate issue/patch restoring a truthful Unsupported diagnostic or supporting the operand shape? Is its pre-existing flag-on behavior a blocker for the default-check backend fix, and what MIR/input evidence is required to decide?
12. **Draft and evidence wording:** Do the PR descriptions accurately separate source findings, fixed-code expectations, observed base/fix outcomes and completed platforms? Which remaining sentences require narrower wording or an additional exact-head result?
13. **Commit structure:** For B1, keep two logical production/tests commits, squash to one, or split any semantic changes into separate PRs? For B3, should the three-stage test/fix/relocation history become one or two commits while preserving the tested final tree?
14. **Readiness:** What minimum remaining source, test, issue-tracking and CI evidence is required for each candidate independently before ready-for-review, given the blocked runner and the explicitly excluded instrumentation panic?
