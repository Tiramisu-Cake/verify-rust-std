# Static validation

PASS, with full identities in `VALIDATION.json`:

- Python AST, YAML, shell syntax, Git whitespace; profile hashes and source-copy bytes/modes.
- Existing process management and workflow-context checks reused from historical control; synthetic success/failure, timeout, spawn, native signal, missing/null/type/partial/NOT_RUN, unsupported status, source/selection/target/configuration mismatches.
- Complete collection and finalization of consistent and contaminated seven-invocation runs; all six F4 records preserved after native build/control failure; paired aggregate exit deliberately identical across consistent/contaminated cases.
- Per-harness exact check inventory and partitions, count/identity inconsistencies, inventory composition changes, missing assertion admission, lost delayed check and initialized-control false failure.
- Real depth-three shallow checkout of the candidate, using shared reference Git objects; source preflight passes. Isolated synthetic control/same-tree trigger ancestry passes and depth-two/mutated/untracked-source variants fail.
- Binary patch applied in an isolated Git index over exact main produces control tree `34a402bd4ebbabf3ec611327097475c8cb46cfba`.
- Main compiler/driver/library/config/toolchain unchanged; old confirm-main worktree clean. Temporary validation checkouts were removed; no target/build copies were made.

No local cargo/rustc/Kani/CBMC/rustfmt/full-runner execution. New native build, proof probes, actual generated check inventories, actual compiler order, reproduction and future CI are **NOT_RUN**. Synthetic results establish service handling, not the runtime F4 defect. Independent review14 is pending.
