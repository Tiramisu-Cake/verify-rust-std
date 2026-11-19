# PR 5176 — independent finding verification, 2026-11-19

Recorded before candidate edits. Source: new worktree `/root/kani-pr5176-cleanup-w13`,
branch `cleanup/pr5176-20261119`, exact initial HEAD
`3d9a1809388f74c62ea9fb7320e123db0b8b37fa`, tree
`cf797fd1fd0ebf0ae35d58e06da5624ee00ae1ab`. Connected GitHub read also confirms
that open PR model-checking/kani#5176 still has this head in
`Tiramisu-Cake:fix/zst-union-codegen-v4`; base is
`0aac16ef62da9e9d5645782d458593e5d78143ba`.

Read HANDOFF, REPORT, COVERAGE-EDITS, CODE-COMMENT-EDITS and PR-EDITS in
`wave0/open-pr-slop-review/pr-5176/`, plus the pr-9487 correction. The conclusions
below come from reading this Kani revision, not adopting the earlier runner model.
All line references in this file refer to the initial head.

| Finding / proposed edit | Decision | Independently checked code evidence and disposition |
| --- | --- | --- |
| Consolidate five edge-shape fixtures into main | CONFIRMED | All five `tests/expected/zst-union-edge-*/main.rs` have identical default runner settings: no compile/kani/cbmc flags, cfg, ignore or harness filter. Each has its own concrete `Edge`, one typed-copy harness, full byte comparison, shape assertions and one cover. Their colliding type names require five distinct inline modules. Preserve imports, declarations, bodies and covers; remove only the repeated field-order comment and indentation changes. |
| Expected mode discovers multiple source files in one directory independently | CONFIRMED | `tools/compiletest/src/main.rs:372` routes Expected through `collect_rs_tests_from_dir`; :487-520 discovers every eligible `.rs`, recurses, and excludes only temp-prefixed sources/auxiliary directories. `runtest.rs:349-373` invokes Kani once on the selected source with its file-local flags. `common.rs:186-195` uses each file stem for its output directory. Thus three sources with distinct stems remain three invocations, without importing the recursive sources into main. |
| Replace legacy main oracle with same-stem `main.expected`; give recursive sources same-stem oracles | CONFIRMED | `runtest.rs:488-505` first selects `file.with_extension("expected")`, then falls back to sibling `expected`. This is ordinary Expected mode, not CargoExpected discovery. Same-stem files prevent sibling fallback ambiguity. |
| Keep complete 12/0/12 main summary, five cover blocks, and successful-verification text | CONFIRMED | Existing main has seven proof functions; edge sources add five. `runtest.rs:528-598` searches independent substring blocks; trailing backslash joins consecutive lines. `common.rs:156` and `main.rs:189` make process-success checking opt-in; `run_expected_test` checks it only when requested. A bare per-harness SUCCESSFUL line would not require all twelve successes. Preserve each adjacent SATISFIED/Description pair and require the exact complete-summary text. This is stronger output checking, not a new process-exit guarantee. |
| Keep both recursive controls as separate compilations, colocated with main | CONFIRMED | Recursive sources contain `Node -> *const U -> Node` and `Node2 -> *const Link -> [Node2; 0]`, inferred null casts, black_box and null assertions/covers. `context/goto_ctx.rs:304-355` inserts incomplete structs/unions before generating components. `typ.rs:1296-1336` uses rustc sizes and codegens logical fields while building a union. Isolation preserves the two distinct first-visit setups. Static reading supports their purpose; actual traversal order is not a new runtime result. |
| Add 1/0/1 summaries to recursive oracles | CONFIRMED | `kani-driver/src/harness_runner.rs:308-341` prints the manual summary whenever total > 0, including one harness; `kani-driver/src/main.rs:223-225` calls it unless quiet. These fixtures have no quiet flag. Preserve original cover blocks and SUCCESSFUL text, add one-success/zero-failure/one-total. |
| Retain all fourteen cases, rather than delete apparent duplicates | CONFIRMED | Main's seven cover array typed-copy/projection, C and Rust layout padded payloads, scalar alignment, offset/prefix frame, all-ZST no-padding path, and bounded nondeterministic array indexing. Five edges separately cover declaration order, nested units, nested empty bytes, aligned arrays and a struct wrapping an array. Two pointer-recursive shapes cover different incomplete logical arm types. All checks and the sole `kani::assume(index < 2)` stay intact. Existing Array/Unit/union_transmute baselines lack the same typed padded-union array-copy plus full-byte/projection checks; uninit/unions and valid-value-checks/maybe_uninit use distinct flags and oracles. |
| Change the small compiler fix | WITHDRAWN | No code change was recommended or justified. `typ.rs:1298-1336` derives union/field size from rustc in bits; within padding > 0, padding == union_size selects a zero-size payload, uses `codegen_ty_unit` (:557), and retains the original logical type in unionfield. `cprover_bindings/src/goto_program/typ.rs:102-162,212` preserves logical field types, while `irep/to_irep.rs:142` serializes padded_typ. The user's explicit byte-identical constraint applies to the whole compiler file. |
| Shorten the new typ.rs comment | WITHDRAWN | The comment exists at :1319-1324, but editing it would violate the byte-identical compiler-file constraint. Preserve it exactly. |
| Remove five repeated edge comments | CONFIRMED | Each edge source says `The ZST arm is deliberately first, including for the nested shapes.` Each local Edge declaration directly shows its order, and four of the five harness names identify other shape distinctions. Remove the five identical comments; preserve the initialized-byte explanation. |
| Shorten recursive union-reachability comments | CONFIRMED | Both sources have the same historical `Only the pointer graph ... change the root` comment above their union. The next field is a pointer in the enclosing struct in both sources. Replace it with the proposed concrete pointer/incomplete-struct explanation. |
| Rename recursive cover labels and rewrite comments inside proof bodies | WITHDRAWN | These are optional wording edits. Preserve all fourteen harness bodies (including original cover labels) modulo indentation in moved modules. Original labels already uniquely describe the two null-pointer checks and match their expected files. |
| Rephrase original main's byte-span and padded-payload comments | WITHDRAWN | These are optional rewrites, not repeated-comment removal. Preserve the complete original main source as a byte-identical prefix, including the primary array_typed_copy reproducer. |
| Correct universal-cover claim and shorten PR draft | CONFIRMED | Actual source contains 14 proof attributes but only 7 covers: five edge and two recursive, zero in the original main. Live PR says `Each new harness includes a kani::cover!`; that universal reading is false. Retain the scope, issue, nonzero-width limitation and one historical CI reference; omit the claim, platform/rerun/perf detail, speculative removal advice and stale uninit observations. Preserve license and AI disclosure lines exactly from the live body. No live PR edit. |
| Treat earlier base/fixed/CI/performance claims as newly verified | WITHDRAWN | Source files and expected output are not execution evidence. No cargo, rustc, Kani, CBMC, CI, log retrieval, base/fixed replay or performance measurement is authorized. The draft marks final cleanup validation pending and labels the old CI reference as historical. |

Kani module harness discovery was also checked directly:
`library/kani_macros/src/lib.rs:568-599` retains the function visibility and adds
`kanitool::proof`; `kani_middle/codegen_units.rs:357-370` collects proof-marked
crate items through `reachability.rs:79-98`, which has no public-only predicate.
`tests/expected/MemPredicates/thin_ptr_validity.rs` demonstrates inline proof
modules. Moving private concrete harnesses into inline modules preserves their
discovery according to source; no native discovery run is claimed.

The CBMC pr-9487 descriptor bug allegation was explicitly withdrawn by its
coordinator because the runner reinserts the fourth line. That Perl behavior is
not transferred to Kani. The Kani branch, oracle fallback, exit gate, consecutive
matching, summary emission and all-local-item discovery above were each read.
