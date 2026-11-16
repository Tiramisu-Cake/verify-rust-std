# C-01 — source + CI-only preparation

Task: TASK-CH8-C-CONTROLS-W14.md; input g0 `0a57f9f52b184c27bb3c14d86f48a0b5a2401551`.
Updated under TASK-CH8-PPRIME-REBASE.md point14: the previous
source/control pair is superseded for dispatch; its review records remain historical.
Current source `d073585946093071b696eada41b8c8cac18362a7`;
control `cdd3c6d04112cc1b1e1a80a850389236647bc849`.
One stage only. No push, CI, publication, ledger operations, local Rust/compiler/verifier
execution, B-01 intake or alias-model development. All eight roots remain **NOT_RUN**;
proof credit **NONE**. Existing STOP C on broader claims remains in force.

Source worktree `/root/verify-rust-std-ch8-c-ctl-w14-pprime`, branch `work/ch8-c-ctl-w14-pprime`.
Campaign base P′ `c5ff36ff433692140605891f646043f991db05de`
(tree `1302063846873aa300f8bac64fe09e8a3ed1280f`); production 872d remains unchanged. Only the opt-in
`verify/c_controls.rs` and its registration in `verify.rs` change. `smallsort.rs`,
models and tool pin files remain unchanged. This is the explicitly authorized A1
source exception outside S; no patch is proposed for S/13/11.

The runner invokes stock upstream tool `0aac16ef62da9e9d5645782d458593e5d78143ba`
directly against the separate source checkout, overriding no tracked source files.
The inherited P′ tool_config pin remains upstream c5e65fdfc3; it is not
the execution selector. Organizer flags, `--no-assert-contracts`, controls cfg, uninit OFF.

Exact named source assertions and reachability labels: [ORACLES.md](ORACLES.md).

Controls:

| Root suffix in `verify::c_controls` | Target | Expected diagnostic |
| --- | --- | --- |
| `c_merge_source_write_restore` | PFC real `bidirectional_merge`, dst-only frame | FAIL assigns/frame at retained volatile source writes; other failures are separate |
| `c_merge_source_read_only` | Same helper/geometry without writes | PASS legal companion |
| `c_callback_live_shared_in_outer_frame` | PFC `callback_outer`, frame exactly v | Stock PASS classified ALIAS_GAP, never Rust permission or C PASS |
| `c_callback_read_only_in_outer_frame` | Same wrapper/geometry without writes | PASS legal companion |
| `c_external_mut_state` | PFC `external_mut`, v + separate counter | PASS legal effectful callback |
| `c_external_cell_state` | PFC `external_cell`, v + counter.as_ptr() | PASS legal UnsafeCell callback |
| `c_insert_tail_local_lifetime` | Real insert_tail then successive real insertion loops | PASS local MD comparison, gap shift/copy-back, next iteration, full-value output and suffix |
| `c_local_storage_reuse` | Scoped read of initialized MU/MD, reuse, fresh read | PASS, no stale-reference access |

N1 writes and restores source slot1 at each of the two comparisons; both arguments
are read and the same live `a` is read after restore. Its closure has no counter or
mutable captured state. N2 uses fixed reversed N2, a pre-reborrow tail raw alias,
and no external state. L1/L2 companions remove only their respective writes.
L3 separates counter and input allocations; the outer wrappers explicitly authorize
counter storage and execute all inner helper bodies. L4 starts descending N3,
executes the real first insert_tail and next tail2 iteration, observes tmp comparison,
checks copy-back, and executes an additional tail3 iteration before checking suffix.
No assertions or summaries instrument production helper bodies.

Exact std/control commits and trees, branch names and manifest hash are in
[CI-REQUEST.json](CI-REQUEST.json). [REVIEW.md](REVIEW.md) records independent review
and fixed findings. [VALIDATION.json](VALIDATION.json) distinguishes synthetic/static
checks from proof. [MANIFEST.sha256](MANIFEST.sha256) binds the frozen control payload.

Future coordinator work, **not performed here**: push the exact std/control commits
under the recorded branch names with `[skip ci]` commit messages; inspect frozen
request/review and grant a separate C-01 dispatch. A skip-ci control commit does not
activate its push workflow. For activation use a separately recorded same-tree sibling
commit without `[skip ci]`, with the same sole tool parent on a new branch such as
`uninit-ci/ch8-c-ctl-w14-pprime-c01`; preserve the skip-ci upload branch. A child violates parent
binding. At most one host/attempt1; no retry authorization is conveyed by preparation.
The C cap 1–2 and reservations are coordinator responsibilities, not ledger entries here.

On actual execution retain original verdict/property IDs, target/wrapper identities,
flags and exact source bytes. Export cover IDs lack descriptions; mapping to source
cover labels, successful assertion descriptions, and retained writes needs runtime
review. Unknown binding is INCONCLUSIVE, never a qualified alias gap or C PASS.
A N1 PASS requires binding/write/reachability review before documenting a transient
source-confinement gap. A stock N2 FAIL requires its actual named property, and
frame/setup/pointer failures do not prove temporal enforcement. Rejecting a legal
L3/L4 route requires diagnosis before any new model claim. B1/B2 remain distinct;
these fixtures do not establish generic verification or unwinding.

P′ compatibility is the coordinator-supplied reason for this rebase; compilation
and every proof root remain NOT_RUN in this stage. Source controls and actual
smallsort helper bytes are identical to the prior reviewed C candidate. The runner
removes generated target directories before artifact-size accounting; upload also
excludes `**/target/**`, including when cleanup fails. Adjacent original receipts,
list JSON and outputs are preserved. Synthetic coverage includes cleanup OSError.
