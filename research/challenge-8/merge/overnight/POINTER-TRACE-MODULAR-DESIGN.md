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
separate case with the same full domain, return type, and posts. It remains
uncalibrated until a fresh hosted run reaches that exact assertion. No local runner,
extraction, or solver execution is part of this design.
