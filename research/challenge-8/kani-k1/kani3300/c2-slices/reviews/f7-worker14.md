# Worker14 — F7 integration/recomposition review

PASS bounded static review; no actionable findings. Source
`8e299aa6243bc5f06a29c51e98aafa9564478220`, parent
`3f5242bb1539fb88196d7e503b722f0905f2b46c`. No delegation or source edits.

The five-file delta equals all14 historical zero-context F7 hunks byte for byte,
with the hashes and headers pinned by `f7/F7-RESIDUAL.json`. All three pre-F7
import/writer snippets are present in the parent and removed by this commit; both
delayed writes now use `replace_delayed_body`. Full diff to F is empty. The actual
tree is exactly `9829702c1aa0ecb73c860fc0ad5451757917d6cb`, including modes,
submodules and dependency pins. B1 remains an ancestor and the seven source commits
follow the accepted order. Source worktree is clean; `git diff --check` passes.

The first-write journal moves the complete original `TransformationResult`, including
its modified flag, and retains it across repeated delayed writes. Restore reinstates
the original or removes a formerly absent entry. Untouched entries and bodies first
regular-transformed during the scope stay cached. The normal and failed-root paths
obtain regular bodies before replacing them through the same journal. Regular/stub
passes, loop metadata and override provenance are unchanged.

The RAII guard's explicit lifetime, constructor, field, Deref/DerefMut and Drop
implementations agree. Begin rejects an active scope. Drop restores on normal return,
recoverable early return and Rust unwind; no Drop behavior on process abort is claimed.
The cprover guard starts before reachability and remains through global passes,
re-collection, codegen, contracts, quantifiers, immutable finalization and materializing
owned export data. Both harness and PubFns paths enter this common function. The LLBC
guard likewise covers its common codegen function, reachability, global passes and
translation/export, including PubFns. Immutable lifecycle hooks remain intact.

The existing checker was run read-only in memory with48 inherited contracts plus7
explicit F7 contracts. It passed:5 changed Rust files,55 contracts,111 bound calls,
zero findings. The JSON records checker/input hashes and the added contracts. Import
provenance and generic/lifetime impl seams match F. This is bounded source-token and
identity checking, not symbol/trait/borrow resolution, macro expansion, MIR binding
or compilation.

Six journal tests and two scope tests remain exact F. Their source controls cover
first snapshots/flags, untouched/warm/new regular entries, absent failed roots,
repeated/empty scopes, misuse, normal/early exit and unwind reuse. They were not run.
Split root fixtures do not independently establish shared-cache isolation or producer
order; historical mixed/singleton captures retain their stated binding/order limits.

Native fmt/build/clippy/units/Quick/LLBC and push/CI: NOT_RUN. No new runtime,
structural end-to-end isolation or formal proof credit. Exact-head CI overlay was
not provided at source review and is not covered by this verdict. Coordinator Quick,
nonzero6+2 structural units alongside the prior20 units, and fresh affected LLBC
compilation remain pending. Writes are confined to this report and its JSON sibling.
