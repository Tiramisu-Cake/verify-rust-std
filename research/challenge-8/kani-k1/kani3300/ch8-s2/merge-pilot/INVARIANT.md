# Offline merge invariant, CAP32 / actual99e

Task `task9856043dab21de8346b68196fa91929b96331293`; owner GO for offline
design/diagnostics only. Contract: PLAN-CH8-ITEM2-SORTING-v2.md §§5–6.
Source, tree, blob, SHA256 and 30 exact line anchors: `source-map.json`.
No actual source/attrs/model/control edits. Kani, compiler, CI and S3 qualification
NOT_RUN; proof credit NONE. The arguments below are proposed proof obligations
with a mathematical preservation sketch, not machine-checked induction.

## Chosen bounded form and domain

Use **full multiset invariant for all 256 u8 values**, guarded endpoints, and a
pure snapshot-rank strengthening to handle stale fronts and equal values.
Ranks are ghost formulas over the existing full byte values, not a change of
runtime comparator/model or a trusted summary. No arbitrary query is used as a
substitute for full counts. This is an intentionally concrete, sound candidate;
its Kani instrumentation feasibility and cost remain unmeasured.

`2 <= n <= 32`, `h = floor(n/2)`, left half `[0,h)`, right half `[h,n)`.
Both halves nondecreasing under ordinary byte `<`. Exact pair:
`T=u8`, `F=sorting_model::KeyLess<u8>`; its actual implementation compares the
full byte. The historical `merge::lt_u8` / `profiles::LtU8` uses `x >> 1` and
is a different order: do not substitute it. Other `T/F`, arbitrary FnMut,
arbitrary length, stability qualification and combined extra-UB are outside scope.
`n=0/1` are outside actual merge's precondition; `k=0` is an included loop head.

## State and pointer correspondence

Save immutable, initialized `S[0,n)` from the source before any write, preserve
source allocation/provenance, and retain the original destination pointer `D`.
Counters `i,j` count low selections from left/right; `a,b` count high selections
from left/right (`ip,jp` in Python). At a paired loop head, `i+j=a+b=k`.

| actual local | ghost correspondence |
| --- | --- |
| `len`, `len_div_2`, `src` | `n`, `h`, original source pointer |
| `left`, `right` | `src.add(i)`, `src.add(h+j)` (one-past allowed as pointer) |
| `left_rev` | `src.add(h-1).wrapping_sub(a)` |
| `right_rev` | `src.add(n-1).wrapping_sub(b)` |
| shadowed `dst`, `dst_rev` | `D.add(k)`, `D.add(n-1-k)` |
| `left_end`, `right_end` after loop | reverse fronts `.wrapping_add(1)`, equal to `src.add(h-a)`, `src.add(n-b)` |

Do not rewrite a reverse pointer using unsigned `h-1-a`/`n-1-b` subtraction.
At exhaustion `left_rev` may be `src.wrapping_sub(1)`; it is a pointer sentinel,
not an initialized element. The end recovery uses wrapping addition without
dereferencing it. Mathematical signed offsets in the pilot denote this only;
Python negative indexing is explicitly rejected.

## Clauses at a paired head

These labels are local to this proposal, not a claimed transcription of the
audit's full C1–C6. For bounds in pure predicates, expand over constant 32 slots
and 256 byte values with short-circuit guards. Never evaluate a pointer load,
subtraction, or endpoint expression before its definedness premises.

**G — geometry.** `0<=k<=h`, all counters nonnegative;
`i+j=a+b=k`, `i+a<=h`, `j+b<=n-h`. Define the disjoint source index sets:

```
L = [0,i)       union [h,h+j)          # consumed into low output
H = [h-a,h)     union [n-b,n)          # consumed into high output
R = [i,h-a)     union [h+j,n-b)        # remaining
P = [0,k)                             # initialized low output
Q = [n-k,n)                           # initialized high output
```

Thus `|L|=|H|=k`, `|R|=n-2k`, and `P,Q` are disjoint.

**F — memory/init/frame.** Source remains initialized and equal to `S`; source
`[src,src+n)` and destination `[D,D+n)` are valid, provenance-carrying and disjoint
regions (same allocation is allowed with disjoint ranges). The original
destination region is writable, with initialization established for `P union Q`.
Other destination elements may initially be initialized or uninitialized and
are never read by predicates; no writes have occurred there. Outside the
destination region, every live initialized value and initialization/ownership
state is preserved. Callback is the exact stateless, pure `KeyLess<u8>`, no
external writes, no ghost reads, no panic. Prove its body/frame; do not assume
this for arbitrary `FnMut`. `modifies` alone proves neither ordering nor init.

The pilot uses a separate **write mask**, not an assertion that all original
destination slots were uninitialized. Its integer filler in unwritten slots
models an abstract store/write log, not permission to load `MaybeUninit<u8>`.
Checks stop before output loads when the required write/init mask fails.

**O — order and remaining links.** `D[P]` and `D[Q]` are nondecreasing.
If `k>0`, every `x` in `S[R]` satisfies `D[k-1]<=x<=D[n-k]` and
`D[k-1]<=D[n-k]`. No band endpoint is evaluated at `k=0`. Empty `R` gives
vacuous element comparisons but does not remove the band-to-band inequality.

**E — guarded C5 endpoints.** When `k>0`:

```
((i>0 && D[k-1]==S[i-1]) || (j>0 && D[k-1]==S[h+j-1]))
&&
((a>0 && D[n-k]==S[h-a]) || (b>0 && D[n-k]==S[n-b]))
```

Use short-circuit `&&`/`||`; do not compute these source indexes eagerly.
Each nonzero-counter guard asserts consumption from the **correct** half,
even when the unguarded index happens to be in the global array.

**M — full values.** For every constant byte `q in 0..256`, simultaneously:

```
count(D[P],q) == count(S[L],q)
count(D[Q],q) == count(S[H],q)
count(S[0,n),q) == count(D[P],q)+count(D[Q],q)+count(S[R],q)
```

All counts range over guarded initialized indices only. Counter/count arithmetic
can use usize with proven bounds `<=32`; the loop over byte values must not be
implemented as an overflowing u8 loop. No single-probe claim is used for M.

**A — auxiliary snapshot ranks.** For each initialized source index `p<n`,
define `rank(p) = #{t<n : S[t]<S[p] || (S[t]==S[p] && t<p)}`. This is a
fixed, at-most-32 comparison sum, with no runtime comparator or sorting oracle.
Prove uniqueness/bijection onto `[0,n)` and increasing ranks inside each half.
Then maintain:

```
p in L => rank(p)<k
p in H => rank(p)>=n-k
p in R => k<=rank(p)<n-k
t in P union Q => exists p<n: rank(p)==t && D[t]==S[p]
```

Use constant bounded disjunction for the final witness. This strengthening
prevents the abstraction from losing tie identity, needed for the actual
end-counter/ord-panic obligation even if all byte values are identical.
It implies O/M, but keep the explicit O/M assertions as distinguishing controls
and as the future byte-sorting API. Prove rank properties; do not add axioms.

## Init, up, down, odd, post: preservation sketch

1. **Init:** all counters and k are zero; `L,H,P,Q` empty, `R=[0,n)`.
   G/F/M/A hold from the precondition/rank lemma, O/E are guarded vacuously.
   `h>=1` also establishes the actual pre-existing `assume(h!=0)` at line 921.
2. **Physical reads when k<h:** before up, `i,j,a,b<=k<h`.
   Hence `i<h`, `h+j<n`, `h-1-a>=0`, `n-1-b>=0`; all four actual candidates
   are valid within their respective halves even if a half's logical R is empty.
   Do **not** guard away or change these actual comparisons. After up, reverse
   counters are unchanged, so down's two reads are still valid. At least two
   live tokens exist before up, and at least one before down.
3. **Up:** a nonempty half's forward candidate has its smallest live rank.
   If a half is empty, its forward candidate is the first high-consumed token,
   so its rank is `>=n-k`; it cannot beat the live minimum rank k. Such a
   candidate exists in the half since `i<h` at the active head. Comparisons
   between halves agree with rank order: equal bytes select left, whose source
   index is smaller. Up selects rank k, writes only D[k], and increments i or j.
   Intermediate invariant: use low count `x=k+1`, high count `y=k`, low rank
   cut `<x`, high rank cut `>=n-y`, R ranks `[x,n-y)`, output bands `[0,x)`,
   `[n-y,n)`. Re-establish F/O/M/A; E's low endpoint uses x-1, not old k-1.
4. **Down:** a nonempty half's reverse candidate is its largest live rank.
   For a half empty after up, its reverse candidate is low-consumed, rank
   `<=k`, including a token just consumed by up. The live maximum has rank
   `n-k-1>=k+1` when `k<h`; it wins. Equal bytes select right, the larger
   source index. Down writes D[n-k-1], increments a or b, then the loop
   advances k. Both output writes are distinct since `2*k<n-1` at the old
   head. Restore the symmetric invariant, guarded E, and no double consumption.
5. **Exit:** k=h, `|R|=n-2h`. Even n has empty R and full initialized output;
   A gives full rank order, M full permutation, and G gives `i=h-a`, `j=n-h-b`.
6. **Odd leftover:** exactly one live token, rank h. Actual `left<left_end`
   means `i<h-a` within the same source allocation; otherwise right is the
   singleton. Copy to D[h], mark initialized, increment the corresponding low
   counter. Use the asymmetric invariant with x=h+1,y=h. All slots are now
   initialized/ordered, full counts hold, both remaining halves are empty.
   `dst` need not advance after the odd copy: actual code does not advance it.
7. **Normal post/panic:** in both parity cases, end pointer equalities follow
   from empty halves and wrapping end recovery. Therefore line 958 is
   unreachable on lawful inputs. Do not stub, assume false, or drop the check.

At intermediate/odd states `pilot.checks` checks F/O/M/A with x,y and omits
its pair-only E check; E for the generalized bands follows from the selected
extremum. A future checker must prove it or expand E with x,y explicitly.

## The exact §6 C5/query-count trap

Take n4,h2,k1,i1,j0,a0,b1; `S=[1,9,2,10]`, D[0]=9,D[3]=2.
Source-only lower/upper frontier cuts are true (1<=2 and 10>=9);
each output band has length one and is sorted. All counts of probe0 are zero.
An unguarded endpoint OR uses `S[h+j-1]=S[1]=9` and `S[h-a]=S[2]=2`, both
unconsumed values. `negative_controls.C5_len4_probe0` reproduces that acceptance.
Guarded E rejects both alternatives; full M rejects mismatched counts for
1,2,9,10; O/A independently reject the false order link. This is not a
counterexample to universal/full C6, nor an actual reachable bad merge trace.

If a future cost optimization uses a single arbitrary ghost probe, it proves
only that probe's count theorem per invocation. Recovering universal counts
requires runtime/control-flow independence from the probe, arbitrary choice
without postselection, unchanged same probe through all callee summaries,
and proof of each summary for the same source version, T, F, order and geometry.
The ghost cannot change comparison results or the admitted domain. No hidden
probe reassignment or switch to `LtU8` is allowed. Order must retain an
independent sound argument (e.g. A/O/guarded E), not follow from probe0 equality.
This pilot chooses full M and does not rely on that optimization.

## Open machine-proof obligations

| ID | obligation for future actual Kani integration | status here |
| --- | --- | --- |
| K0 | source/CFG/call binding on exact99e or explicitly reviewed delta; exact default KeyLess activation | source text pins checked only |
| K1 | rank bijection, per-half monotonicity, min/max stale-front dominance including duplicate ties, over all abstract bounded states | mathematical sketch + reachable diagnostics |
| K2 | base and inductive up/asymmetric/down invariants; ghosts synchronized with actual choices; safe invariant extraction/havoc | NOT_RUN |
| K3 | validity, initialization, provenance, same/separate allocation disjointness, callback/frame and each actual ptr operation incl. wrapping sentinel/end recovery | NOT_RUN; integer geometry only |
| K4 | odd copy, end equalities, actual ord-panic unreachable, sorted/full-count normal post | NOT_RUN; diagnostic coverage only |
| K5 | predicate definedness at k0/empty/exhausted fronts; constant guard extraction, default safety checks retained, semantic false-invariant/havoc controls | NOT_RUN |
| K6 | exact actual callee PFC before verified summaries; summary/frame compatibility and same byte order, probe discipline if optimized | NOT_RUN |
| K7 | simple variant/extraction and false-decrease control if claiming termination; partial correctness is sufficient for this proposal | NOT_RUN |
| K8 | domain/offset matrices, negative controls in actual Kani, independently reviewed candidate, measured wall/RSS under pinned limits | NOT_RUN |

The for-loop itself is bounded by h<=16; no machine termination claim follows
from writing an invariant. Small Python/native enumeration does not prove
universal inductiveness over arbitrary havoced states, formal memory safety,
actual-code equivalence, proof extraction soundness, S2 fit or S3 qualification.
