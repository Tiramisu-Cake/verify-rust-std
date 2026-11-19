# HANDOFF — independent review of PR #5176 cleanup

**Verdict: APPROVE.** No concrete defect or required change found in the scoped cleanup or local PR body. This approves the source/static review stage only; native validation remains NOT_RUN. One stage complete; stop with HANDOFF.

## Reviewed identities and scope

- PR: `model-checking/kani#5176`.
- Candidate worktree: `/root/kani-pr5176-cleanup-w13`, branch `cleanup/pr5176-20261119`.
- Parent/published PR head: `3d9a1809388f74c62ea9fb7320e123db0b8b37fa`.
- Candidate: `06e1533360605f52f82c69764dc4940b7afcc21b`.
- Candidate tree: `71a429da6e114fb4fd34f20605b47590d60a62c8`.
- Verified HEAD, branch, exact parent and exactly one candidate commit. Author and committer are `Tiramisu-Cake <igkharin@gmail.com>`. Candidate worktree clean.

Read the actual parent-to-candidate changes, fixtures, compiletest discovery/matching, Kani harness collection, summary and property emitters, and type-name generation. Read `../pr5176-cleanup/{HANDOFF,FINDINGS,PR-BODY}.md`, the original `../open-pr-slop-review/pr-5176/{HANDOFF,REPORT,COVERAGE-EDITS,CODE-COMMENT-EDITS,PR-EDITS}.md`, and the original input body snapshot. Conclusions below were checked against source and independent byte comparisons; the author's static audit was read but not executed or adopted as independent evidence.

All Kani source references below refer to the candidate. Fixture paths in tables are relative to `tests/expected/`.

## 1. Change boundary and exact preservation — PASS

With rename detection disabled, exactly 21 paths differ, all within the eight original `zst-union-*` fixture directories and the consolidated `zst-union-arm` directory: the seven old satellite source/oracle pairs disappear, their five edge cases move into main, two recursive source/oracle pairs appear beside main, and main's legacy oracle is replaced. No compiler, runner, library, flags, configuration or other regression changes occur.

The complete `kani-compiler/src/codegen_cprover_gotoc/codegen/typ.rs` is byte-identical between parent, candidate and working tree, including comments. SHA256: `0613ee6cf6140699d5e88dd5c9b43620e9f93bdd557b4a2c586f092b575c84be`.

Independent whole-file reconstruction reproduces candidate `main.rs` exactly:

1. Start with the entire parent `zst-union-arm/main.rs`, unchanged (172 lines; SHA256 `152372c88000ecddd7ecdb5e60f265a385f791b0658306fb5a8484dc7c97ae12`). This includes the original primary reproducer and all seven original proof bodies, comments and declarations.
2. Append the five original edge sources in the table's order, each inside its concrete named module. Remove each satellite's redundant file license header when embedding it under main's existing license, remove its one repeated field-order comment, and add four spaces to each nonempty embedded line. Everything else, including imports, concrete types, attributes, proof signatures/bodies and comments inside them, is identical.
3. Each recursive source equals its parent source with exactly one comment replacement above its union declaration. Its proof body and all declarations/attributes retain exact bytes.

Thus preservation is stronger than a whitespace-normalized body check: the entire reconstructed sources match. No assertion, initialization, typed read/write, projection, field order, size/alignment/offset check, prefix canary, nondeterministic domain, inferred cast, black_box call, cover predicate or label was dropped or rewritten. The sole assumption remains `kani::assume(index < 2)` in `zst_array_indexing`.

## 2. Complete old-to-new harness map — PASS

Every old harness maps once to the following candidate location. Bodies are identical; only the five embedded edge bodies acquire module indentation. Candidate line numbers identify function declarations.

| Old source | Old harness | New source:line | New harness path |
| --- | --- | --- | --- |
| zst-union-arm/main.rs | array_typed_copy | zst-union-arm/main.rs:57 | array_typed_copy |
| zst-union-arm/main.rs | padded_typed_copy_c | zst-union-arm/main.rs:71 | padded_typed_copy_c |
| zst-union-arm/main.rs | padded_typed_copy_rust | zst-union-arm/main.rs:88 | padded_typed_copy_rust |
| zst-union-arm/main.rs | aligned_zst_typed_copy | zst-union-arm/main.rs:105 | aligned_zst_typed_copy |
| zst-union-arm/main.rs | zst_arm_at_nonzero_offset | zst-union-arm/main.rs:123 | zst_arm_at_nonzero_offset |
| zst-union-arm/main.rs | all_zst_union | zst-union-arm/main.rs:143 | all_zst_union |
| zst-union-arm/main.rs | zst_array_indexing | zst-union-arm/main.rs:160 | zst_array_indexing |
| zst-union-edge-array-first/main.rs | copy_array_first | zst-union-arm/main.rs:185 | array_first::copy_array_first |
| zst-union-edge-nested-unit-array/main.rs | copy_nested_unit_array | zst-union-arm/main.rs:217 | nested_unit_array::copy_nested_unit_array |
| zst-union-edge-nested-empty-byte-array/main.rs | copy_nested_empty_byte_array | zst-union-arm/main.rs:249 | nested_empty_byte_array::copy_nested_empty_byte_array |
| zst-union-edge-aligned-array/main.rs | copy_aligned_array | zst-union-arm/main.rs:285 | aligned_array::copy_aligned_array |
| zst-union-edge-struct-array/main.rs | copy_struct_array | zst-union-arm/main.rs:323 | struct_array::copy_struct_array |
| zst-union-recursive-arm/main.rs | recursive_arm | zst-union-arm/recursive-arm.rs:17 | recursive_arm |
| zst-union-recursive-zst-arm/main.rs | recursive_zst_arm | zst-union-arm/recursive-zst-arm.rs:19 | recursive_zst_arm |

The fourteen distinct obligations remain: primary byte8 union copy/projection; padded C and Rust-layout payloads; aligned scalar ZST; offset8 union with prefix preservation; all-ZST padding-zero path; bounded nondeterministic indexing; array-first declaration order; nested unit arrays; nested empty byte arrays; aligned ZST arrays; struct-wrapped arrays; nonzero recursive logical arm; zero-width recursive array arm. There is no case deletion disguised as consolidation.

## 3. Expected matching and complete oracles — PASS

The actual Expected-mode behavior is established by `tools/compiletest/src/runtest.rs:488–505,528–598`:

- Execute Kani on the selected source. Choose its same-stem `.expected` first, falling back to sibling `expected` only if absent.
- Match against stdout concatenated with stderr. Each independent expected line/block is searched as a substring anywhere in output; independent blocks have no ordering requirement and do not consume matched lines.
- A trailing backslash joins the next expected line into the same consecutive-output-lines block. Expected fragments are trimmed, so the emitted `\t - ` prefix is compatible with these patterns.
- Process success is checked only with `require_success`; it is opt-in (`common.rs:156`, `main.rs:189`). The cleanup does not add an exit-code guarantee.

`zst-union-arm/main.expected` is complete for this runner. Its five original adjacent SATISFIED/Description pairs are preserved exactly, for labels:

- `copy_array_first post-copy data and projection`
- `copy_nested_unit_array post-copy data and projection`
- `copy_nested_empty_byte_array post-copy data and projection`
- `copy_aligned_array post-copy data and projection`
- `copy_struct_array post-copy data and projection`

It also requires `VERIFICATION:- SUCCESSFUL` and `Complete - 12 successfully verified harnesses, 0 failures, 12 total.` Independent reconstruction from the five old edge oracles, the successful-verification line and the updated summary matches the entire file exactly. SHA256: `70e9e7c2cdd4ce5dadd17609923664bf7abc4eca0c37cbf15e17ee0e86108796`.

The one SUCCESSFUL pattern is intentionally not a count of twelve success lines. Repeating that pattern twelve times would still match the same one output line twelve times. All twelve successes are required by the full 12/0/12 summary: `kani-driver/src/harness_runner.rs:308–340` partitions the actual manual harness results by VerificationStatus::Success and prints successes, failures and their total. `kani-driver/src/main.rs:223–225` calls this emitter when not quiet; these fixtures have no quiet flag. A run with one failed or omitted result cannot emit the required summary through this code path. Per-harness SUCCESSFUL text is emitted at `cbmc_property_renderer.rs:415–433`; cover status and description are emitted on adjacent lines at :333–340. No original main cover was lost: its seven original harnesses have assertions and no cover calls.

Each recursive `.expected` equals its entire old oracle followed by `Complete - 1 successfully verified harnesses, 0 failures, 1 total.` Its original adjacent SATISFIED/Description pair and SUCCESSFUL requirement remain. This accounts for all seven original cover predicates and labels, with five in main and one in each recursive source. Each of the three sources has exactly its own same-stem oracle; no legacy fallback file remains.

An independent Python transcription of the inspected matcher, applied only to synthetic text, passed four positive checks (including reordered cover blocks and the explicit single-SUCCESSFUL-match behavior) and rejected 39 negative variants across the three goldens: absent/wrong/partial summaries, absent/all-failed success text, absent or unsatisfied covers, and broken status/description adjacency. This verifies these concrete output requirements, not arbitrary-output authenticity. The inherited substring matcher does not enforce uniqueness, count SUCCESSFUL occurrences, bind a summary to named harnesses, exclude unrelated extra output or independently check exit status. The exact source inventory and actual summary-emission path provide the corresponding source-based reasoning; no stronger oracle guarantee is claimed.

## 4. Separate recursive compilations, discovery and collisions — PASS

`tools/compiletest/src/main.rs:372–379,487–537` routes Expected mode through recursive `.rs` discovery, with each eligible source becoming a test. All three candidate source names qualify; none has cfg/ignore, file-local compile/Kani/CBMC flags, harness filters or external module/include directives. `run_kani` passes only the selected source and its flags (`runtest.rs:349–373`). Neither recursive source is imported by main or by the other recursive source. They therefore remain separate Kani invocations/compilations according to the runner source, with expected inventories **12 + 1 + 1**. This is not a native discovery result.

`common.rs:186–200` separates compiletest output paths by file stem. Kani also derives distinct artifact/crate names `main`, `recursive_arm`, `recursive_zst_arm` (`kani-driver/src/util.rs:23–27`, `project.rs:285–325`); hyphens are normalized. Colocation introduces no same-stem artifact collision.

The five `Edge` types live in five distinct modules, each with explicit local imports. `aligned_array::Z` remains distinct from root `Z`; `struct_array::Wrapped` is local. Harness names and module names are unique. Default Rust ADT names use the type identity hash (`typ.rs:485–518`); the special C-FFI path is feature-gated and is not enabled here. Distinct module-local nominal types are not merged merely because each is named Edge.

Private inline proof functions remain eligible: `library/kani_macros/src/lib.rs:568–595` preserves visibility and attaches kanitool::proof; `kani_middle/codegen_units.rs:357–381` collects marked functions and keeps all when no filters are supplied; `reachability.rs:79–98` examines all local monomorphic function items without a public-only gate. Existing inline proof modules also occur in `tests/expected/MemPredicates/thin_ptr_validity.rs`.

The recursive source graphs remain `Node -> *const U -> Node` and `Node2 -> *const Link -> [Node2; 0]`. Incomplete symbol insertion remains in `context/goto_ctx.rs:304–351`. Their independent source setup and inferred pointer casts are preserved; no new claim about observed first-visit order, MIR reachability or backend execution is made.

## 5. Withdrawn edits and PR body — justified

The author's departures from the optional original wording proposals preserve the requested invariants:

- Withdraw compiler/comment editing: the whole typ.rs must remain byte-identical.
- Withdraw original-main prose changes and recursive in-body comment/cover-label rewrites: all proof-body bytes must remain identical modulo moved indentation, and the original main remains an exact prefix. Existing recursive labels are unique and match their oracles.
- Withdraw adoption of historical base/fixed/CI/performance statements as new validation: source/oracles establish no execution result. The draft explicitly marks cleanup native validation pending.

Removing five repeated edge comments is justified by the directly visible concrete declarations; initialized-byte explanations remain. Replacing the two union-adjacent recursive comments states their existing pointer/incomplete-struct purpose without changing setup. Consolidation does not introduce generic helpers or collapse nominal types.

`../pr5176-cleanup/PR-BODY.md` is accurate and concise: it describes the padded-wrapper unit payload and retained logical type, rustc layout, retained regression scope, #5175 and the nonzero-width limitation (#5085 / diffblue/cbmc#9487). It removes the erroneous universal-cover reading and speculative/stale performance, workaround-removal and uninit observations. Its single standard-CI link is explicitly historical on the original PR head, matching the original snapshot's label; this review did not authenticate that run or its logs. Static preservation/oracle checks are now independently supported; native cleanup validation remains explicitly pending. No body edit is requested.

Reviewed draft SHA256: `a502a79934436e58ebc83721a6b440c93bcea40110993eb590aedfe867fc23d3`. Compared directly with `../open-pr-slop-inputs-20261119/pr-5176/PR-BODY.snapshot.md`; each protected line is preserved exactly once, unchanged:

> By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.
>
> *Disclosure: this change and description were prepared with the help of AI assistants.*

## Validation and stopping boundary

Independent static checks passed: exact candidate/parent/tree/branch/cleanliness and changed-path checks; compiler and working-fixture byte/mode comparisons; whole-source and whole-oracle reconstruction; fourteen-case map and 12+1+1 proof / 5+1+1 cover counts; protected PR-line equality; the bounded synthetic matcher checks above; `git diff --check` on the actual reviewed parent-to-candidate diff. The independent Python checks used Git reads, bytes/text and synthetic output only. No author audit was run and no candidate/package file was written.

Cargo, rustc, Kani, CBMC, native compilation/discovery, base/fixed replay, format/clippy, CI, push, live PR/external draft mutation, log/archive retrieval, coordinator/ledger changes and subagents: **NOT_RUN / NOT_PERFORMED**. No runtime PASS, measured speedup, portability result or proof credit is claimed. Native final-candidate validation belongs to a separately authorized stage; approval here does not authorize it.

Only this review HANDOFF is to be committed in g0 as `Tiramisu-Cake <igkharin@gmail.com>`, with `[skip ci]`. Unrelated concurrent g0 changes are excluded. The containing commit's SHA is reported externally to avoid a circular self-pin. **HANDOFF; stop.**
