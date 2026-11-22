# Planner task: does kani#5196 make SmallSort checkable under `-Z uninit-checks`?

Context. Challenge 8 item 1 (absence of UB) includes reads of uninitialized memory. Stock Kani at the organizer pin `9834c96ce9` reports SmallSort's `MaybeUninit` scratch patterns as unsupported under `-Z uninit-checks` (kani#5151). Maintainer PR kani#5196 ("Uninit checks: support unions nested in other types and raw pointers to unions", head `bcdc1a0f8dc566654da1f18b4e502f0f4e7ad40a`, branch `feliperodri:uninit-nested-unions`) resolves #5151. Auto-merge is enabled, but the PR currently conflicts with main (15 commits behind, including our merged kani#5172), so the final merged commit will differ. Known limits from its description: unions nested in unions and transmutes into a union stay unsupported; contract harnesses passing unions by value across calls need 10–25 GB (kani#5199). Owner GO for an experimental check: 2026-11-22.

Questions to answer with native evidence:
1. Which SmallSort harnesses (our submission #752, candidate `152f11556a` and the current PR head) now run under `-Z uninit-checks` with no unsupported-construct check, and which still hit one (with the exact construct)?
2. Any uninitialized-read failure: real finding or tool imprecision? Keep both open until a minimal reproducer exists.
3. Time and peak RSS versus the same harness without `-Z uninit-checks`, especially contract (Check/Replace) roots, to see whether #5199 hits us (our scratch is passed by reference/raw pointer, not union by value).
4. What would remain before item 1 could claim uninit coverage for the covered fixtures (pin bump, harness changes, scope limits).

Plan, do not implement:
- Choose the Kani revision (5196 head as is vs. a local merge with current main, if conflict-free; justify), the std revision, a small representative roster (a few plain proofs touching scratch, a few Check/Replace contract roots, at least one per SmallSort entry family), flags (organizer flags + `-Z uninit-checks`), and per-root time/RSS bounds (8 GiB child cap lane).
- Choose the route by cost: the fork control lane (zero GCB, one job at a time; it is shared with the pending #752 binding check, which goes first) or GCB via k1g.sh (item-2 ceiling $10 shared; say expected spend).
- Write `PLAN.md` and, if needed, a worker implementation task in this directory; commit with `[skip ci]`, push g0, report the SHA. The coordinator dispatches.

Out of scope: any public text, changes to the candidate tree, comments on #5196.
