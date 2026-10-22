# N13 exact adapter — hypothesis and distinguishing controls (2026-10-22)

Status: design note only; nothing run (no Network lane; GitHub Actions are not
a Network lane any more). Source: `networks/prove-ranks.py` (`composition`,
`exact=True`, n=13) and [RANK-RESULTS](../networks/RANK-RESULTS.md).

## Observation (from the recorded runs)

R13e: the universal symbolic body finished at 203.9 s, the domain-law equality
body at 208.2 s, and the exact wrapper `network13_finite_swo_order(rel, d, q)`
(requires `finite_swo(rel, d) == true &*& d == [0..12]`) started its call to the
accepted composition at 218.7 s and did not finish by 300 s. No false assertion
was reported: **inconclusive**, not a refutation.

## Hypothesis H1 (unverified)

With `d == [0..12]` and `finite_swo(rel, d)` in one context, the prover can
match `finite_swo` on the 13-element literal and unfold the finite-law
fixpoint (pairwise/transitivity laws over 13 elements), which the symbolic
component deliberately avoids. The exported post itself is cheap: `!rel(..)`
and the `ce_occ` multiplicity do not mention `d`, and `mem(v, [0..12])` for
literal `v` is closed computation.

## Candidate shapes (each keeps the full post; no axiom)

1. **Membership split:** a pure lemma `domain13_members(d)` (requires only
   `d == [0..12]`, ensures `mem(0,d) … mem(12,d)`), verified in its own body
   without `rel`; the adapter calls it, then the composition, then asserts the
   literal memberships. Tests whether the time is in membership discharge.
2. **Literal export after the call:** keep `d` symbolic through the composition
   call and only afterwards `assert d == [0..12]` to rewrite the 13 `mem`
   conjuncts — ordering the equality after the heavy call.
3. **Per-conjunct export lemmas:** split the 26 post conjuncts into small
   lemmas over the composition's post, so no single proof obligation carries
   all of them at once.

## Controls for the run that tests this

| Control | Expected |
| --- | --- |
| `domain13_members` alone | fast PASS (separates membership cost) |
| adapter shape 1 / 2 / 3 with the full post | PASS within the timeout, or the same timeout (H1 rejected for that shape) |
| each shape with one literal membership flipped (e.g. `mem(13, d)`) | assertion failure (non-vacuity) |
| each shape with one adjacent order post reversed | failure |
| unchanged R13f universal component | byte-identical, PASS (regression) |

Acceptance needs the same gates as R13f (full post, return/leak checks, body
inventory) on one identity; a timeout stays inconclusive. The lane for this
(stock VeriFast, pure ghost) must be a Network Cloud recipe once it exists.
