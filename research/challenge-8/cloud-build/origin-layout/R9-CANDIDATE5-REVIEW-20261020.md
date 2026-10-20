# R9 candidate 5 independent review — GO for concrete owner close

The candidate-5 delta against source baseline `995855a6` is limited to one
checked source command in the existing recursive lemma and its marker-service
expectation. It inserts `close u64_own(t, v);` immediately before
`close own::<u64>(t)(v);`. The lemma still has `req true`, the same recursive
body structure, and the same `foreach(vs, own::<u64>(t))` postcondition.

The pinned model defines `u64_own(t, v)` as `true` and maps `<u64>.own` to
`u64_own`; generic `own<T>` is the existing constructor around `<T>.own`.
Explicitly closing that concrete predicate supplies the representation needed
before closing the generic constructor. This is an ordinary, checked predicate
close under the existing type-predicate definition, not a new rule, axiom,
permission, or trusted declaration. The tool worktree and profile digest are
unchanged from the reviewed candidate; no tool or model change is part of this
patch.

The marker service test passed, and `git diff --check` passed for the source
and service-test files. No compiler, preparation, proof, or Cloud Build was
run for this review. **GO for this localized candidate only.** It grants no
proof credit or profile acceptance; the next hosted build must verify the
lemma and resource rejoin.
