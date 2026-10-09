# Canonical FBC → actual Drop geometry diagnostic V3

AFTERNOON-MERGE-GUARD-CLOUD-2026-10-09; written before implementation.
Profile `copy-on-drop-canonical-fbc-self-geometry-diagnostic-v3`.

Observed blocker: V1/V2 never reached constructor bodies because precise own
cannot contain existential fraction/nonprecise foreach. The nonprecise V3
constructor is being tested separately. Existing direct actual Drop is only a
conditional component: its strong req contains six self/root geometry facts
not yet derived from canonical safe-Drop FBC. Generated normal Drop post returns
fields/padding/field own, omitting payload, and generic glue forwards no copy effect.

Obligation: retain exact source private struct AND actual Drop implementation,
V3 full-source non-False own (same current source array, writable destination,
all current generic owners, geometry and positive-stride domain), and the entire
previous direct Drop req/ens/on_unwind contract. Retain canonical safe-Drop
prototype pre and compatibility check. Add only checked ghost assertions after
opening canonical FBC and own in safety_proof. Assertions identify which exact
self facts follow: nonnull, alignment, whole-object limits, address no-overflow,
self/source separation, self/destination separation. Bind src/dst/len from
existing field chunks before asserting these facts; neither addresses nor bytes
create owners. Zero-length branches remain present; V3 construction still len>=2.
No tool/frontend/model/kernel/prelude change, stronger canonical pre, assumed
lemma, removed compatibility check or weakened post is part of this experiment.

Own stays nonprecise, full source fraction1; no duplicate owner, resource loss,
external unaccounted payload or generic own precision/uniqueness premise.
Opening consumes FBC and its own; its body exposes existing field/padding and
payload chunks. Assertions preserve chunks. Exact req consumes them once and
unchanged actual Drop must prove full CURRENT source/destination/foreach post.
Canonical post compatibility and payload preservation remain mandatory; a
geometry success alone grants neither callable Drop nor compiler glue credit.
Caller must already supply initialized CURRENT scratch and owner pool plus
writable destination; actual seed/sort4/sort8/insert_tail acquisition remains open.

Separate stock/six groups, three isolated cases:
- positive: exact source/MIR/refinement, nonprecise own/generated FBC shape,
  all six ordered assertions, canonical compatibility, actual full-count copy,
  full normal/unwind posts/return/leak/no-dead required for component credit.
- prototype_false: same state, exact assert false immediately after opening
  FBC/own and before geometry; only exact prototype assertion refusal counts.
- first_body_false: same geometry and contract, exact false at first actual
  body statement; only reached actual-body assertion counts. A geometry/header
  refusal before it is INCONCLUSIVE, never intended negative success.

Pin source/blob/block, unchanged direct contract and annotation hashes,
compiler/exporter/refiner/schema/console/profile/patch identities. Ghost stripping
must restore exact runtime bytes. Failure at one recorded geometry assertion is
an OPEN diagnostic frontier, not proof acceptance or an expected negative.
Missing payload/assumptions/setup/parser/precision/AST/helper errors are separately
INCONCLUSIVE. Never repeat the prior direct body PASS as canonical caller credit.
Normal forget and unwind owner recovery/glue remain separate checked obligations.

Self-review: ordinary nonprecise full chunks can expose generic owners without
claiming precision. Existing pointer field lemmas do not establish full root
geometry or numeric disjointness; this probe tests entailment without inventing
such a rule. Independent Luna exploration and Sol review identified these exact
six gaps and generated payload/glue limitations. Any subsequent semantic rule
requires a new rationale and controls; this card authorizes assertions only.

## Evidence-directed root-bounds V3b amendment (before implementation)

Build1219ab51-c577-4f6f-bba5-a763d29e934a at baa57248c63929085b3d8e2e486d076b341250a1:
V3b constructor positive/fullpost/return/leak and false78(20-25) pass bothprofiles.
ExactDrop geometry stock/six own/FBC/MIR/AST/refinement admitted; prototypeFalse
111(12-17) is matched; positive/bodyFalse stop at selfnonnull112(50-52).
No actual Drop body/copy/post credited. All6geometry conditions remain required.

New separate profile `copy-on-drop-canonical-fbc-root-bounds-diagnostic-v3b`
adds a checked invocation of existing `points_to_limits::<CopyOnDrop<T>>` after
FBC/own opening and before field binding/assertions. Pinned assertions.ml
2387–2420 autocloses whole-struct points_to from same full physical fields and
padding; it neither consumes nor introduces payload arrays or owners. Pinned
prelude_core229–231 returns that same points_to chunk and whole-object limits.
Object-limits definition163–165 includes nonnull and end-pointer bounds; pointer
arithmetic/provenance-max bounds135–137 should entail exact no-overflow fact.
Following field-binding assertion must recover allthree fields without losing
padding or aggregate memory, and the unchanged strong Drop req still consumes
all resources. No trusted rule added. This is a concrete actual-pre bridge.

Reorder retained6assertions: nonnull, objectlimits, nooverflow, alignment,
source/destination intervalseparation. All exactpropositions unchanged. A first
failure at alignment records actualprogress but still INCONCLUSIVE overall.
Existing lemma gives no alignment/intervalsep promise; do not assume those.
PrototypeFalse stays immediately afteropens beforelemma, actualbodyFalse stays
firstbody; eachnegative onlycredited atits ownstage/predicate/location.

Add explicit checked `call();` afterallsixassertions in safety_proof. Pinned
verifast.ml4028–4045 requires this; previous False-own legacy masked its absence.
verify_expr.ml252–273 consumes strong pre, produces strongpost, runs epilog,
consumes canonicalpost then checks leaks. Generatedcanonicalpost omits payload,
so successfulgeometry alone will still expose a separate postconservation gap.
No leak command, pre replacement, compatibility removal, weakening or effect
claim. Direct req/ens/unwind and runtimebytes remain byte-identical.
Independent Luna found resource-preserving aggregate route; Sol confirmed
call/prototype/leak behavior and absent canonical payloadpost. This reasoning
supports this exact proof-invocation diagnostic, not a new semantic kernel axiom.
