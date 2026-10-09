# Exact CopyOnDrop explicit-contract diagnostic

Status: **REJECTED BEFORE IMPLEMENTATION**. No patch or Cloud run was made.
The frozen stock and six-component profiles remain distinct.

The actual repository obligation is `CopyOnDrop<T>::drop` at
`library/core/src/slice/sort/shared/smallsort.rs:301-309`: copy exactly
`self.len` initialized current source elements into a writable destination,
preserve the original existing T owners once, return full count-n current
source/destination bytes and owners, and forbid unwind. The exact strong direct
contract is the unchanged `CONTRACT` byte string in the pinned
`copy-on-drop-prepare.py`; no runtime source, field, signature, generic bound,
post, assertion, or copy summary may be weakened.

The a643 AST shows the generated safe-Drop signature opens FBC and `own=false`,
then discards the resource-bearing explicit return post. This diagnostic asks
whether the exact complete explicit contract can be used as a **conditional
method signature** while the actual method body is still verified against it.
This would be a trusted translator semantic change. It would **not** prove the safe
Drop trait's generated FBC/own contract, generic `drop_in_place` applicability,
compiler drop glue, normal `forget`, or a caller. All invocation sites must
supply the strong method precondition independently. The existing nonvacuous
guard-own and caller construction questions remain separate OPEN gates.

Design decision: replacing the canonical safe-Drop method signature is not an
admissible route to guard/caller credit here. The canonical interface continues
to require FBC/own, and the direct strong body already has conditional PASS
evidence. Removing its prototype obligation would only repeat that conditional
result while leaving the intended bridge unproved. Therefore the proposed
translator special case below is retained solely as a rejected design sketch;
its controls were not implemented or run.

Rejected patch target: only the pinned translator, in the safe-function body translation
branch. Recognize exactly the named `CopyOnDrop<T> as Drop::drop` from the
same-unit private struct with one type parameter and exactly three non-ZST
fields named `src`, `dst`, `len` with pointer-to-T, pointer-to-T, native usize
translation. Require a complete explicit parsed `req`, normal `ens`, literal
`on_unwind_ens false`, no `assume_correct`, no safety proof, no function-type
clause, and the pinned raw annotation bytes. For this exact case, emit the
explicit contract without a generated safe prototype implementation check.
Keep normal body translation and verification. Other Drop methods use the
unchanged path; a malformed CopyOnDrop candidate must refuse at frontend.
The runner must also pin the exact original SmallSort blob and separately
record patch input/output hashes; the patch alone is not a universal rule.

Positive domain: the direct Drop contract's positive-sized T, count-n source
and destination spans, disjoint guard/source/destination geometry, existing
foreach T owner pool, and full normal/unwind posts. Falsifiable hypothesis:
with the exact front-end route, the actual method reaches and verifies the
dynamic count-n `copy_nonoverlapping` call and full return/leak checks under
both pinned tool profiles. A first-body `assert false` must reject at its exact
source line and columns before copy. Missing contract and wrong struct/field
shape must refuse at the frontend; their first Cloud results are calibration
until exact diagnostics are recorded. Export/refinement/source/hash/setup
failures are inconclusive, not intended negatives.

Hypothetical outcome map: if positive and matched body false pass, record only conditional
actual-callee credit for this named experimental profile. If frontend refuses
the exact source or the body fails at an unrelated obligation, preserve full
logs and reassess. No result turns generic safe Drop or the public caller green.

A future proposal should retain the canonical FBC/own pre and separately prove
that an owner-bearing `own` and checked post can account for the actual copy
effect without losing payload through safe-Drop's generated return interface.
It must derive the original self-object geometry from valid resources rather
than insert it into a by-value `own` or assume it. Constructor, `forget`, and
drop glue remain separate gates. That future proposal needs its own semantic
card and review; this rejected sketch authorizes no patch.

Self-review: the change removes an automatic compatibility obligation for one
exact method, which enlarges what the tool can call conditionally. That is a
new trust assumption until an admissibility decision. It leaves the kernel,
memory/alias model, prelude, copy summary, exporter, refiner, unrelated safe
functions, and every other Drop unchanged. The patch must fail closed on
missing/malformed annotations and not use `assume`, suppressed unwind, leak or
dead-code checks. An ordinary call receives only the same strong explicit pre;
the runtime method proof is still required at the same source version.
