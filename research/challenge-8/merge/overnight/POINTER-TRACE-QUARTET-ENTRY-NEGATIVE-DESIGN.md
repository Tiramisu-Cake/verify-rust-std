# Full-shape G2 quartet entry negative

This isolated negative pairs with `g2_pointer_trace_quartets` under the same
full request domain, tuple3-of-tuple4 return type, all twelve terminal
postconditions, checked helper bodies, and runtime trace body. Its only proof
body difference is a marked `assert false` as the first statement; its
function and CASE names are distinct so the runner checks it independently.
The expected-error metadata uses the repository's established `false` /
`TARGET` source columns (16–21), but this row remains uncalibrated until a fresh
hosted run reaches that exact assertion. A setup, parser, helper, return-place,
or earlier body failure is inconclusive.

The negative tests reachability under the exact full G2 domain and return
shape. It does not weaken or replace the positive case, remove its posts or
helpers, change the loop, or establish the pointer trace. Future acceptance of
the tuple-quartet diagnostic requires the separate positive full-body gates and
this same-shape/domain negative reaching its intended assertion, along with
source admission, exporter, decoder, refinement, return/leak, and strict
dead-code checks. The existing nested-tuple positive remains untouched.
