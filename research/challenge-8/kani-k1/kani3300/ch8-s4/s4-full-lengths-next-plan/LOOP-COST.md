# Loop obligations and cost risk

Source `8faf8e62af8f82b5c46af020086f8df591b6757e`; kernel path
`library/core/src/slice/sort/shared/smallsort.rs`, oracle path
`.../verify/sorting_model.rs`. These are **source body-iteration upper bounds**,
not measured native iterations, lowered loop IDs or a new unwind configuration.
Preserve unwind36 for proposed positives/Cell16 and34/34/34/36 for the controls.

| Work | Network8 | Network9 | Network13 | Network17 | Later Cell fallback16 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Full outside-frame loop | 34 | 34 | 34 | 34 | 34 |
| Explicit Cell initialization | 0 | 0 | 0 | 0 | 34 |
| Snapshot element copies | 8 | 9 | 13 | 17 | 16 |
| Adjacent-order post loop | 7 | 8 | 12 | 16 | 15 |
| Count outer queries | 8 | 9 | 13 | 17 | 16 |
| Count inner bodies per query | 8 | 9 | 13 | 17 | 16 |
| Total count inner bodies | 64 | 81 | 169 | 289 | 256 |
| Descending cover helper | 7 | 8 | 12 | 16 | 15 |
| Actual network region loop | 1 | 1 | 1 | 1 | 0 |
| sort9 / sort13 fixed swap calls | 0 | 25 | 45 | 45 | 0 |
| Shift insertion calls | 7 | 0 | 0 | 4 | 15 |
| Largest sift loop for one tail | 7 | 0 | 0 | 16 | 15 |
| Total sift bodies upper bound | 28 | 0 | 0 | 58 | 120 |
| Total comparator calls upper bound in actual algorithm | 28 | 25 | 45 | 103 | 120 |
| Final merge bodies / output-copy elements | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |

Network17 tails p13,14,15,16 have respective sift upper bounds13,14,15,16;
58 is their sum. The last tail spans17 elements. Cell16 uses p1..15, not p16.
N8 uses p1..7. Each insert initially compares the tail/predecessor, then moves
left and stops at begin or a lawful position (667–702); comparator bound p
includes that initial comparison. N9/N13 do call shift with offset==len: its
loop has zero bodies, but the function and safety plumbing are not skipped.
sort9/13 contain fixed straight-line25/45 swap sites (494–610), not loops.
Each swap calls the exact comparator once; memory/spec lowering can add work.

The frame loop alone has34 bodies for every root; a global unwind N+1 is not
justified for these smaller lengths. Nested count work totals N squared but
does not need a single N-squared unwind depth: each explicit inner loop has N
bodies. Existing source36 covers these stated maxima at source level only;
off-by-one, compiler transformations, memory intrinsics/predicates, spec/contract
plumbing, arbitrary-array construction, fixed Snapshot32 initialization and
lowered residual/unreachable paths still need their actual inventory and
unwinding results. No new flags, unwinding disable, `--unwindset`, oracle
replacement or provider assumption is proposed. A source bound cannot establish
that an unexported check was run or removed safely.

For all remaining lengths (COVERAGE.json records exact tails/halves):

- F n>=2: n-1 shift bodies, per-tail maximum n-1, total sift<=n(n-1)/2,
  max120 at16. n<2 returns with no shift.
- N n2..17: one region L=n. N n18..32: two regions L=h,r. For each region
  a=13 if L>=13, else9 if L>=9, else1; shift bodies L-a and total
  sift<=sum(p for p=a..L-1). Merge has h bodies, two merge-step comparisons
  and writes each body, plus one center copy if odd; copy-back writes n.
  N18 has0 insertions; N19 has one right tail p9; N25 has left tails9..11
  and a zero-tail right sort13; N32 has tails13..15 in both regions. The
  first package deliberately avoids all second-region/merge/copy-back costs.
- G n>=2: two fixed half-iteration bodies, h,r; a=8 if n>=16 and size<=16,
  else4 if n>=8, else1. Each half has L-a extensions/copies and
  sift<=sum(a..L-1), then final merge h bodies plus odd center. For sort8
  there are two internal merge8 loops of4 bodies each and four sort4 seeds
  (5 comparisons per sort4). At32: size<=16 gives16 extensions and184
  maximum sift bodies; size>16 gives24 extensions and228 sift bodies.
  Stable scratch capacity may exceed the finite48 fixture and has no bound
  inferred from these algorithm counts.
- Full-value oracle through32: snapshot<=32, order<=31, outer count<=32,
  inner<=32, total inner<=1024. Proposed V34 frames still34. Any new scratch
  frame/initialization loop must be inventoried separately: for example48
  explicit bodies would not be justified by unwind36 without lowered evidence.

## Existing costs and unchanged envelope

Read the committed structured `run-44548842328/COST-INTERPRETATION.json`,
not raw logs. Run44548842328/attempt1 completed campaign in359.38134s:

| Admitted network case | Native verification seconds | Whole child including compile seconds | Initial-export compile upper seconds |
| --- | ---: | ---: | ---: |
| N2 | 3.061224 | 41.716 | 36.719 |
| N3 | 3.846285 | 43.751 | 37.915 |
| N4 | 4.692469 | 44.183 | 37.542 |
| N0..1 | 33.427759 | 72.998 | 37.661 |

The earlier four600s whole-child timeouts are censored; their completed native
verification times are UNKNOWN. There is no exact speedup factor or established
MIR/compiler causal explanation. Even N0..1 costs more than N4; do not extrapolate
linearly from N or fixed swap counts. New N8/N9/N13/N17 cost and fit are UNKNOWN.
Full-byte comparisons, duplicate/count formulas, non-Copy Cell movement,
contract expansion, symbolic pointer paths, repeated compilation and25/45 actual
swaps may grow solver cost. N17 combines45 swaps with up to58 insertion
comparisons; Cell16 has120 comparisons and an additional34-cell construction.
Merge/general add uninitialized scratch, two bases, odd centers and copies.

Use the complete unchanged resource/flag snapshot in NEXT-PACKAGE.json,
copied from `network-r2-impl/RESOURCE.json`. Principal caps:

| Scope | Existing cap |
| --- | ---: |
| Whole child (compile included) | 600s |
| Initial compile subcap | 180s |
| Per slot | 720s |
| Controller / cleanup | 180s / 240s |
| Campaign / outer / phase / step | 6900s / 7500s / 8100s / 7560s |
| Local / outer RSS / headroom | 6291456 / 12582912 / 2097152 KiB |
| stdout / stderr / export / artifact | 16777216 / 1048576 / 8388608 / 268435456 bytes |
| jobs / max parallel | 1 / 1 |

Serial eight-root planning envelope:8*720+180+240=6180s; reserve6900-6180=720s.
Serial five-root Cell16 package:5*720+180+240=4020s; reserve2880s. Per-child
compile180 is inside600, which is inside slot720, not additive. Workflow setup
budget1800 and workflow limit180min remain separate unchanged scopes; this is
not a new timing grant, registration, run count or accounting entry. The baseline
also has a distinct compile budget900 and default_unwind50 at resource level;
positive row attribute/resolved unwind36 and controls34/36 must be checked in
their actual argv. Do not silently replace either setting. Sampled RSS is a
non-atomic PGID/owned census, not a strict kernel/cgroup/full-tree peak.

Future execution should stop at an incomplete/timed-out row's actual boundary
and retain native status/properties/elapsed/compile/export/sampled RSS separately.
Do not label timeout as a negative detection or retry an identical failed
configuration automatically. If a source-direct refinement is needed, retain
the exact domain, oracle, controls and caps and request its later implementation
stage. An assumed consumer is diagnostic until independently proved providers
and consumer bridges exist. This PLAN ONLY task performs no measurement/run.
