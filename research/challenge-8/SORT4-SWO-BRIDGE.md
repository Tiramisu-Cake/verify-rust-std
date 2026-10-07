# Finite strict-weak-order rank bridge — accepted stock component

This is an independent pure lemma after the [checked rank-network theorem](SORT4-ORDER-LEMMA.md).
It aims to replace the remaining mathematical claim that any fixed strict weak
order on four occurrences can be represented by integer ranks. It does not
model Rust `T`, callbacks, pointers, memory or unwind.

## Preexperiment card

- **Actual std obligation:** the five `is_less` sites and selected logical
  indices of `sort4_stable`, SmallSort blob
  `e555fce440872898e47fd5114f32eb15401d07df`. Their pure rank network is
  separately checked; applying it to a fixed strict weak order requires a
  checked relation-to-rank bridge.
- **Hypothesis and domain:** an arbitrary 4×4 Boolean strict relation over
  logical occurrence IDs `0..3`, including ties, with irreflexivity, strict
  transitivity and transitive incomparability. All 4 diagonal and 64 triple
  instances of each transitivity rule appear in the finite `s4_is_swo`
  predicate. Lemma inputs use the exact finite predicate
  `s4_id4(i) := i==0 || i==1 || i==2 || i==3`, rather than relying on the
  verifier to derive integer discreteness from `0<=i<=3`. These are the same
  four logical IDs; no safety-domain restriction is introduced. No totality,
  antisymmetry between equal-class occurrences or
  distinct-address premise is imposed.
- **Full local post:** let `rank(i)` count the four strict predecessors of
  occurrence `i`. For any `x,y` in `0..3`, the checked lemma
  [`s4_swo_rank_bridge`](sort4-swo.gh) establishes `rank(x),rank(y)` in
  `0..3`, `less(x,y)` iff `rank(x)<rank(y)`, and incomparability/equivalence iff
  the ranks are equal. Its body derives predecessor-set inclusion and equality
  from the finite SWO laws; the [positive application](sort4-swo-lemmas.c)
  calls it with the full post, without an assumed helper contract or axiom.
  These ghost lemmas have no executable normal or unwind path.
- **Profile and expected stages:** unchanged official VeriFast 26.09 source
  `809de4596839b739dd999f9e462242c835e3af46` on a GitHub-hosted runner,
  no patch. The positive should verify its complete post and leak/dead-code
  checks. The isolated [negative](sort4-swo-negative.c) supplies an all-tied,
  valid relation and then incorrectly treats occurrence IDs as ranks; its only
  expected error is the marked `TARGET_ASSERTION` in
  `s4_wrong_rank_bridge`. A setup/frontend/helper failure is inconclusive.
- **Outcome mapping:** if positive and intended negative pass, the *pure
  finite-4 quotient transfer* is checked, and the existing rank-network lemma
  can be applied mathematically to a fixed relation on the four original
  values. If ordinary proof syntax or missing case analysis blocks it, repair
  within this ghost profile and use a new exact-SHA run. If the marked false
  assertion verifies, quarantine the profile and preserve evidence. A need
  for a new axiom, verifier semantics or quantifier feature ends this gate as
  a design/blocker, without broadening the trust boundary.

Even with this bridge, proof of the actual Rust function still needs to show
that every normal callback answer equals this one fixed relation on preserved
keys/values and that the selected pointers carry the corresponding occurrence
and permissions. Panics require the separate full unwind/resource contract.
For ZSTs, predecessor counts use occurrence IDs, not pointer addresses.

N9/37550139106 timed out at equivalent_ranks count equality after completing
pointwise laws. N10/37553115842 checks the isolated count-equality helper and
 equivalent_ranks to completion, then times out at less_rank strict-count sum.
Full finite quotient transfer is still UNPROVEN and negative NOT RUN. N11 isolates
strict-count/bounds arithmetic using the same evidence-backed proof technique.
No definition, full domain/post or stock verifier semantics changes.

Accepted N11/37553933186,source3c3f0f338559675c5b4ce0859126bbedf8d9495c:
stock VF0,104 verified statements, all eight helper bodies and positive application
complete with return/leak checks. Full iff/bounds posts discharge. All-tied valid
relation negative rejects only marked ID-as-rank assertion19; hashes unchanged.
Earlier timeouts remain historical. Full pure choice-network composition is a
separate prepared gate, not yet an accepted actual Rust theorem.
