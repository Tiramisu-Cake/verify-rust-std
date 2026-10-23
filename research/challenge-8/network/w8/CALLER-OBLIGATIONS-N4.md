# W8 source-bound caller obligations (N4 preparation)

State: STATIC_PREPARATION_ONLY / UNVERIFIED. No Cloud lane, callee summary,
Rust proof or independent B1/B2 credit. Selected as independent mission work
while the N4 exact mathematical experiment runs; it reduces the later W8
integration ambiguity without changing a tool, source, model or premise.

Source: `cd371e035c7e573760c43bf934d53e8118ee3e7d`,
`library/core/src/slice/sort/shared/smallsort.rs`, blob
`40939f922bcb6fdc7ee0d30427fa861827043827`, SHA256
`85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1`.
The actual `small_sort_network` body is lines311–371. It requires
`T: FreezeMarker`, not a standalone Copy/size/nonzero premise. Dispatch at
lines160–170 also depends on CopyMarker and stack heuristics; that caller
fact must not be silently added to this helper's public contract. Source
comments and the table below are proof obligations, not callee certificates.

## Length branches and insertion interface

The constant scratch length is32 (lines191–192). In each visited region,
`insertion_sort_shift_left(region,presorted_len,is_less)` is called at349.
A future same-source insertion summary must admit each of these offsets,
retain F/current cells on normal and unwind, and consume a sorted prefix
only for its functional sorting post. Safety must remain valid without SWO.

| Original len | Actual route for nonzero-sized T | Region(s), presorted prefix |
| --- | --- | --- |
| 0,1 | early return at319–321 | no helper/insertion/stack access |
| >32 | abort at323–325 | no normal post claimed; preserve all checks before abort |
| 2..8 | no_merge, return after insertion | whole slice; prefix1 |
| 9..12 | no_merge, return after insertion | whole slice; sort9/prefix9 |
| 13..17 | no_merge, return after insertion | whole slice; sort13/prefix13 |
| 18..24 | two-region path | floor(len/2),ceil(len/2); both sort9/prefix9 |
| 25 | two-region path | left12 sort9/prefix9; right13 sort13/prefix13 |
| 26..32 | two-region path | floor(len/2),ceil(len/2); both sort13/prefix13 |

In every actual insertion call, `0 < presorted_len <= region.len()` follows
from the selected branch. Thus its explicit invalid-offset abort (581–583)
is unreachable on this route, subject to checked slice/length binding. This
arithmetic observation is not a verified ownership or functional summary.
Boundary controls must include lengths0,1,2,8,9,12,13,17,18,24,25,26,32,33;
25 is essential because the halves use different networks. Odd and even merge
paths also need their own applicable callee evidence.

## Region loop, ZST and caller reachability

The source uses pointer comparison at355 as its phase test; it does not store
a phase integer. A future ghost invariant may track which logical half is
active but must prove that this agrees with the actual pointer guard when
claiming a two-iteration route. For positive element size, derive distinct
half-start addresses from valid bounds/provenance and positive stride, not
from ownership chunks alone. Frame the other half and callback resources
through every network/insertion normal and unwind edge. Bind each reborrow
and restoration of the original full slice to the actual source/MIR.

For ZST and len18..32, both half-start pointers have the same address and the
actual guard does not reach the break on normally returning callbacks. The
right-region construction repeats; no two-iteration/merge reachability or
normal termination theorem follows. For ZST below18, no_merge returns after
the first region. This agrees with the existing Merge caller audit
(`challenge-8/merge`8444589f, `merge/STATUS.md` and `merge/POINTER-DESIGN.md`);
it is not a new machine proof. Public stable/unstable sort ZST returns
(stable/mod.rs31, unstable/mod.rs27) are a separate caller exclusion: standalone
SmallSort admissibility and any divergence claim still need explicit scope.
Do not silently add size>0, change the loop, or identify logical occurrences
by equal pointers. ZST validity/ownership and unwind remain obligations even
where there is no normal terminating merge path.

## Merge to scratch and copy-back interface

At367–369 the caller creates a scratch pointer from its local
MaybeUninit<[T;32]>, calls the actual `bidirectional_merge`, then copies
scratch back to v. This caller has no CopyOnDrop guard. It must establish:

* Before merge: two sorted halves for the sorting claim; valid initialized
  source/current values and F; at least len writable scratch slots; source
  and scratch provenance and applicable separation. Do not replace
  permission/separation with address inequality, particularly for ZST.
* Normal merge: exactly len initialized destination values and the resource
  relation needed for the subsequent actual copy, plus sorted occurrence
  permutation only under a fixed immutable order and faithful normal
  comparator answers. Both odd/even, ordering-violation and legal comparator
  effects are included in callee applicability.
* Merge unwind (including comparator and final ordering-violation panic):
  enough current source ownership and F for caller unwind. Partially
  initialized scratch is never read by copy-back. Its contents and the
  MaybeUninit local must not create duplicated T ownership/drop obligations.
* Copy-back: the actual count is len, not32. Transfer initialized current
  values/ownership from scratch into the full original slice with the
  framing required by the callee, then release the MaybeUninit stack storage.
  A raw byte equality or permutation theorem alone does not establish this.

Merge's geometric/scalar component claims do not supply these resource posts.
N4 authorizes no W8 Build and supplies no compatible actual insertion or merge
summary. The historical Merge worktree is not a current assignment; its old
remaining budget is not available. Consume only a future published, reviewed,
same-source callee matrix with exact tool/profile/unit/Brief bindings.

## Suggested next bounded W8 candidate

Prepare a source/MIR-bound region invariant for the nonzero two-region path,
with an explicit separate ZST control-flow branch and all standalone/public
scope distinctions above. Preserve runtime/generic signatures and do not
start a proof Build until W7 and applicable W3/W5 summaries and a fresh phase
exist. Negative controls should distinguish wrong-half offset/length, missing
frame/rejoin, missing merge initialization or source unwind resources, wrong
copy count, wrong phase-to-pointer association, and illicit ZST address
injectivity. Before/after call reachability controls prevent vacuous positives.
These are prospective targets; no exact diagnostic site or PASS is claimed.
