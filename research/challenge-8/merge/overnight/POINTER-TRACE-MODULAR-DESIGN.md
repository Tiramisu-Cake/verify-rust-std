# Modular G2 pointer trace diagnostic

## Hypothesis and scope

The full G2 trace proof originally motivated a split because one loop
simultaneously carries the forward and reverse cursor/count invariants. The
attempted Z3 diagnostics are now classified as unsupported: they stop at
`pointer_ctor` before reaching the proof body, so they provide no evidence
about Z3 resource use. This diagnostic instead isolates whether two checked
cursor loops compose under the default Redux profile. It changes only the
proof adapter: the original request domain, all
twelve terminal postconditions, source and choice-buffer permissions, positive
stride restriction, and tuple3-of-tuple4 return shape remain unchanged. It
does not replace or weaken the existing quartet case.

The adapter contains three ordinary runtime functions, each with a checked
body: a forward helper, a reverse helper, and the terminal compositor. The
forward helper reads only the `up_choices` Boolean array and returns
`(left, right, dst, up_count)`. The reverse helper reads only `down_choices`
and returns `(left_rev, right_rev, dst_rev, down_count)`. Each helper requires
and returns both original read-only array fractions with their exact unchanged
lists. Neither helper reads a `T`, invokes a callback, or creates a source or
destination permission. The compositor calls both bodies, calculates the
terminal wrapping increments, performs the odd-length pointer comparison and
advance, checks the same residual guard, and returns the original twelve
coordinates.

Each helper keeps a manual `loop { ... }` and the original `k <= m`, prefix
count, pointer association, lifetime, and Boolean-fraction invariant for its
own direction. It uses the same checked pointer/count lemmas, including the
full checked helper prefix. The forward loop updates only `left`, `right`,
`dst`, `a`, and `k`; the reverse loop updates only `left_rev`, `right_rev`,
`dst_rev`, `d`, and `k`. Reverse source cursor steps retain the modular
`wrapping_sub` bridge; destination reverse steps retain ordinary `sub`.
The destination reverse step also calls a checked pure interval lemma: stock
`pointer_within_limits` is the provenance min/max address condition, so an
interior `base + index` is proved in bounds from the original bounded start
and one-past endpoints. The loop invariant retains those original endpoint
bounds and the checked numeric span needed by that interpolation. This
addresses the observed out-of-bounds proof
obligation for `dst_rev.sub(1)` without changing its runtime operation or
adding an endpoint premise.

The split is justified for this trace-only adapter because both choice arrays
are read-only, all their values are fixed for the whole call, and the two
cursor/count transition groups share no mutable runtime state other than the
common number of completed iterations. Reordering the interleaved up/down
reads therefore preserves their two prefix counts and final tuple; it claims
nothing about an actual `FnMut`, memory copies, or source/destination
ownership. The same original input domain and exact output equations remain
the test oracle.

## Evidence and decision

The positive requires body execution, helper returns, all twelve posts,
unchanged full fractions/lists, return/leak/source/refinement gates, and strict
dead-code checks. It is an alternate proof adapter only; it does not prove the
actual merge implementation. Any function helper precondition, dead body,
partial post, missing array fraction, frontend/Z3 setup failure, or unsupported
operation is inconclusive. A same-shape first-body `assert false` is kept in a
separate case with the same full domain, return type, and posts. Fresh Cloud60fdb811 reached its exact first-body assertion at670cols16–21
and classified EXPECTED_FALSE_ASSERTION under the unchanged full domain. No local runner,
extraction, or solver execution is part of this design.


Cloud cf07b549 (c06d684186e394a2ef21d078f37289208a1022db) and60fdb811
(e2453336c0a6eb1c2b2d30a624cd066599bbb505) checked the modular positive:
17declared bodies,36return/40leak records, all12terminal relations, source/
refinement/zero-dead gates. The concrete reverse dst_rev.sub(1) is in the
checked g2_trace_reverse body; its bounds follow the endpoint/interior interval
lemma, not an added endpoint or ownership premise. cf07 entry false was only
calibration;60f provides the separately calibrated exact670cols16–21 gate.
Full archived evidence and tool profile are recorded in EXPERIMENT-LOG/ledger;
archivesd54b4168cc4a1c7074ed8947fa1172628b7b916a6af6cccecdcd3cc2e8b1c522
andf82c51e91a7fa54c428da97e4dcbab6d50d4da336afd263e01aae6ca4dd791cf.
No unchanged matrix rerun is required by this documentation update. This is a
conditional trace adapter, with fixed readonly choice-buffer lists and positive
T stride. Actual callback answers/current source values, copies and ownership
are separate; SWO/immutable-key/faithful-answer assumptions belong only to the
functional G2/A/B composition, never unrestricted memory-safety premises.
