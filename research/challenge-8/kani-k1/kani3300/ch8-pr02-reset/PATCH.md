# PR-02 automatic-harness entry reset

Одна стадия TASK-CH8-PR02-RESET-W15; g0 input ea3cec4078a2b1598d4d4f5d3bd62db9c1a13dde.

Defect: seeded automatic models reach PR-02 fail-closed immutable finalizer without an executable memory-initialization reset. The entry pass recognized only proof/proof_for_contract attributes.

The fix adds exactly `KaniFunction::Intrinsic(KaniIntrinsic::AutomaticHarness)` recognition through the existing `try_from`. Both attribute paths, reset insertion, finalizer and memory model remain intact. `AutomaticHarnessPass` precedes `UninitPass`; its early return returns the generated body to the next pass. Entry injection splits bb0 before statement 0 or its terminator, so the single added reset precedes argument generation and contract setup. Pass enablement remains `ExtraChecks::Uninit`; target/callee recognition is unchanged. The reset still selects object and offset with `super::any()` and sets the witness state false.

Source commit: f695f653efaa1f7ac6774a079104de8cc0ff81fc, tree ae00c4f05316e1129d7ce911417c627fda1dc9ea, parent 932fb8395a58f8c86c0d702ba2cae835823b2962. Branch `work/ch8-pr02-reset-w15`, worktree `/root/kani-fix-ch8-pr02-reset-w15`.

Seven upstream-style `tests/script-based-pre/autoharness_entry_reset/*/{main.rs,run.sh,config.yml,expected}` fixtures cover zero-arg typed immutable return, argument+seed, no seed, contract+seed, uninitialized tail read, initialized companion, Uninit OFF. Autoharness is a CLI subcommand; compiletest's ordinary expected mode puts the source first, so the established script-based-pre expected-file style is used. The negative uses a union's uninitialized byte at offset 3, without MaybeUninit/storage extensions. Its initialized companion uses the same layout and read.

Full source patch applies with `git apply --cached --check` to C2 final 8e299aa6243bc5f06a29c51e98aafa9564478220 and SEL1 14bc57fdb99960240c4944845a3d985c8af4dcf7 using isolated temporary indexes. No existing stack/worktree was rewritten. Both have an additional `tcx` argument to `UninitInstrumenter::run`, outside the changed hunks; see APPLY-CHECK.json for resulting trees.

Validation here: Git diff whitespace, shell syntax, apply checks and static package checks only. Compilation, emitted model ordering/count/OFF absence, regression outcomes and proof are NOT_RUN until coordinator CI. Prior A1 results are source-reported context, not new proof credit. No push, CI, PR text or ledger changes.
