# Independent design review (2026-10-10)

The main agent obtained independent GPT-6 Sol review of the proposed narrow
native-entry/c1 composition before implementation. Verdict:
**PASS_WITH_CONDITIONS** for a bounded internal c1 path. This is approval to
prepare the scoped experiment, not proof or acceptance of a semantic patch.

Review conditions carried into the implementation:

1. Native caller reconstruction must join the four **CURRENT** values and
   owners from the verified helper with the unchanged source tail. It must
   retain the current comparator value/owner. No assertion that the first
   four values or comparator equal their entry values may cross `FnMut`.
2. Native diagnostic must discharge complete generated normal and unwind
   posts and leak checks, with the original opaque `MaybeUninit<T>` scratch
   resources restored intact.
3. Any new exact-source lifetime relocation/projection needs a second,
   independent targeted semantic review before implementation. The first
   design review does not admit a concrete tool patch.
4. The exact source c1 is SmallSort line 620. There are no pre-c1 `a/b/c/d`
   pointer declarations; those occur only after c2. The helper may not
   introduce a false source prerequisite from them.
5. The real caller CFG and inline-const path remain a separate claim. For a
   later len8..15 route, the `len>=16` conjunction is false regardless of the
   opaque const lhs; no equivalence of duplicate const expressions is needed.

Immediate implementation therefore starts with proof-source generation and
exact source binding only. The tool profile stays unchanged until a specific
frontend blocker is recorded and the second review completes.
