# PR5183 cleanup independent review — HANDOFF

**Verdict: APPROVE. No blocking findings or required changes.**

Reviewed the actual committed diff and relevant source independently; the author's findings and static-check receipts were comparison material, not proof of correctness. This is the coordinator's single review stage and stops at HANDOFF. No candidate or PR-draft edits were made.

## Identities and preservation

- Candidate: `/root/kani-pr5183-cleanup-w11`, branch `cleanup/pr5183-20261119`, HEAD `d1f1bca80e46f9abe53958147af74de057e6847f`.
- Sole parent / pinned PR head: `19a42e1a21ae6f079cf68637782b4f16c345816b`; exactly one commit ahead.
- Candidate tree: `436debfa7b08fc04fe108f07a6bcdbded8cb0d9f`; candidate worktree clean.
- Whole-tree diff: only `tests/script-based-pre/autoharness_uninit_reset/expected`, exactly two insertions and no deletions. All six original lines, statuses, summaries, bytes and relative order remain intact.
- Entire `kani-compiler` subtree identical to parent: tree `dec9f884977fc63efca13d39587cdae2a7eaba9f`.
- Unchanged test blobs: `main.rs` = `6a9087c99ab97c3b0ac181df9bb198e26c7a14ea`; `run.sh` = `a2d05d065cac1a625b2c936ce8ddd9fad194e755`; `config.yml` = `ce281b6409055714a8a9832e86688cc6dcab79f9`. Script mode remains `100755`.
- Expected SHA256: `2dc6bdf4442e47067573e4ea6a81642f0d95e73541ed61340820102b37ea257c`.

All Kani source references below are to the candidate checkout at the exact HEAD above. T = `tests/script-based-pre/autoharness_uninit_reset/`.

## Both targets and invocations retained

T/main.rs:4 defines the shared repr(C) layout. `uninit_read` at line 10 reads padding at offset 1; `initialized_read` at line 17 writes byte 7 in place before the same-pointer read. Neither has parameters or contract/proof attributes. Both bodies are byte-identical to the pinned PR head.

T/run.sh:5 enables `set -euo pipefail`. Line 7 invokes `kani autoharness` with the uninit-checks/autoharness flags, `--include-pattern uninit_read` and explicit regular output; line 8 requires exactly exit 1. Line 9 separately invokes the initialized target, whose failure would terminate the script unsuccessfully. `kani-compiler/src/kani_middle/codegen_units.rs:440` implements regex include/exclude filtering and line 1217 constructs the candidate names passed to that filter. These two patterns are disjoint for the two functions in this fixture. No invocation was merged, removed or weakened.

The original oracle still requires adjacent FAILURE/uninitialized-pointer-description lines, `VERIFICATION:- FAILED` and the 0-success/1-failure/1-total function summary, plus `VERIFICATION:- SUCCESSFUL` and the 1-success/0-failure/1-total summary. The automatic summary renderer remains `kani-driver/src/autoharness/mod.rs:345`; non-success results cause exit 1 at `kani-driver/src/harness_runner.rs:380`.

## Exact banner derivation

The two added standalone lines are:

```text
Autoharness: Checking function uninit_read against all possible inputs...
Autoharness: Checking function initialized_read against all possible inputs...
```

`kani-driver/src/harness_runner.rs:250` checks non-quiet output; line 252 selects automatic harnesses. Lines 256–260 choose `all possible inputs` when unbounded; lines 261–265 select ordinary Proof and format exactly `Autoharness: Checking function {} against {inputs}...`. Line 280 emits that message, and `emit_line` at line 204 prints the unchanged line to stdout at line 210 when no log-file option is supplied. These retained shell commands set neither quiet nor log-file.

`kani-compiler/src/kani_middle/metadata.rs:133` gets `pretty_name` from the function under verification; lines 147–155 choose Proof for functions without contracts, and lines 158–173 store the name, kind, automatic flag and boundedness. `kani-compiler/src/kani_middle/mod.rs:36` and line 62 strip the local crate prefix, yielding exactly the two top-level names above. `kani_middle/codegen_units.rs:1277` starts empty argument caveat lists, line 1279 iterates arguments, and line 1347 returns whether bounded arguments exist: both zero-argument functions are unbounded. The caveat reaches metadata at `kani_middle/codegen_units.rs:417`.

`kani-driver/src/args/mod.rs:547` preserves explicit regular output and therefore does not install parallel defaults here; line 557 selects no multithreading without jobs, and line 453 builds a one-thread pool. Thus the conditional `Thread N:` prefix at `harness_runner.rs:276` is absent for these commands. This is a source-derived exact rendering conclusion; actual Kani output was not executed or observed in this review.

## Expected matcher and positioning

`scripts/kani-regression.sh:60` registers script-based-pre in exec mode. `tools/compiletest/src/main.rs:464` discovers immediate test directories through config.yml. T/config.yml:3–4 selects run.sh and expected. `tools/compiletest/src/runtest.rs:422` loads that config, lines 457–460 run the script in its directory, lines 462–464 verify expected output, and lines 467–475 independently require script exit 0 by default.

`verify_output` at `runtest.rs:528` concatenates stdout then stderr and calls `contains_lines`. Lines 564–586 collect backslash-linked consecutive groups. `contains` at lines 591–597 searches any output window and requires each output line to contain the trimmed expected substring. An absent required substring reaches the fatal failure at lines 548–556; fix-expected mode also fails after updating at lines 538–546.

The new lines at T/expected:1 and :6 have no trailing backslash and are not continuations of a preceding group. They are accepted as two separate required substring groups. They appear before the corresponding semantic groups in the file, matching the intended script flow; neither insertion alters the existing FAILURE/description adjacency. A wrong banner substring absent from actual output would fail the regression in CI, even if every status/summary and shell exit were otherwise correct. The lines are requirements, not inert labels or comments.

The matcher does **not** enforce order between separate groups, whole-line equality, counts of occurrences, or per-process/property attribution. The added names strengthen the existing oracle without establishing those stronger bindings. Two separate Kani processes also do not exercise stale state transferred between harnesses in one process. These limitations are preserved and do not require a cleanup change.

## PR draft

Reviewed `../pr5183-cleanup/PROPOSED-PR.md`, 977 bytes, SHA256 `cb5190b5be2fe5255f9af335bc15b4b250d4d5340bd0c17c6b927f9e56603319`.

The two substance paragraphs are accurate and concise. They describe missing setup and initialization of memory tracking at automatic harness entry, recognition through the automatic-harness marker, both padding-byte controls and separate failure/success invocations. They do not claim to initialize the target's padding or prove same-process state reset. The testing paragraph correctly distinguishes this cleanup's static checks from unrun native regression and CI; no pending-link placeholder or unsupported current CI success claim remains.

Source support: `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/mod.rs:61` calls setup for recognized entries; lines 82–104 recognize the automatic intrinsic and retain manual proof/proof_for_contract recognition. Lines 112–116 choose the first entry instruction and lines 129–145 insert InitializeMemoryInitializationState before it. `kani_middle/transform/automatic.rs:2389` recognizes the intrinsic definition and line 2400 replaces its body; `kani_middle/transform/mod.rs:116` orders that pass before UninitPass at line 136. `library/kani_core/src/mem_init.rs:193` initializes tracked object and offset nondeterministically, with tracking value false. This supports entry-initialization wording. The reported prior false success remains source-supported problem context, not a new native reproduction.

The following full lines match the pinned original PR-body snapshot byte-for-byte, including punctuation and Markdown:

```text
By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
```

Reference: `../open-pr-slop-next-inputs-20261119/pr-5183/PR-BODY.snapshot.md`, independently checked SHA256 `6a0b490894fd74637f58256eee3b4a77834c45eb4277b262cbc7346021f025d1`. Exact suffix comparison passed.

## Validation and stop

PASS: Git HEAD/branch/parent/count/tree/scope/mode checks, direct blob/tree equality, exact reconstruction of expected from all six parent lines plus the two substitutions of the actual emitter template, draft/snapshot SHA256 and exact legal/disclosure comparison, `git diff --check`, and `bash -n` on the unchanged script. No shell fixture execution or synthetic substitute for native output was used.

NOT_RUN: cargo, rustc, Kani, CBMC, native regressions, compiletest execution, base/fixed native comparison, CI and push. No live PR access/update, build submission, raw evidence/log access, settings/accounting changes, or proof credit. Author package and original recommendation were read as documents; historical CI and author receipts were not promoted to current runtime evidence.

Only this review HANDOFF is added to the documentation repository, with a local `[skip ci]` commit as Tiramisu-Cake <igkharin@gmail.com>. Unrelated concurrent untracked S4 work is preserved and excluded. No subagents were used. Task complete; stop with HANDOFF. Publication or native validation requires its own authorized stage.
