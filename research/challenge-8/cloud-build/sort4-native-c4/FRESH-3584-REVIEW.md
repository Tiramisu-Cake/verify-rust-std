# Fresh independent follow-up 3584fb04

Build3584fb04-e237-4d66-9c85-60de4df059c4 SUCCESS, proof=infra
285220a384d050e046d1e8709b79a52bd602e675, create14:26:37.205010179,
finish14:32:58.810723UTC, charged382seconds. Archive
84208867c4ed920d3ab41012e56ab4a887396ae1da1d387dae317efcf6fab633;
all payload/inventory/index integrity verified. Profile SHA256
4d8c67cbd0c65e3c0065b5b4442b940ba9a7ef74143def5c7241c736708ce47a.
Full raw support/log/source/AST fingerprints:3584-ARTIFACT-INDEX.json.
SUCCESS means diagnostic_complete; verification_accepted=false remains correct.

All six isolated cases have fresh normal/readonly MIR/refinement0 and immutable
source pairs on the SAME frozen C4 tool. No previous AST fingerprint is applied
to the new guard/MU/expression units. Full verification is separate from AST dump.

- selected-guard-lemma VF0/53: checked pure branch implication and a concrete
  len8/size0/scratch24 witness. It proves len/scratch>=4 and size>16 when len>=16
  under the mathematical selected condition. It does not prove actual caller
  guards, bind its inline-const boolean or solve generic ZST/layout.
- mu-roundtrip-current-owner VF1 at12:42: after stock storage open/close, the
  reconstructed CURRENT wrapper has no matching opaque MaybeUninit_own chunk.
  The old owner remains for old, not automatically for new(inner(old)). This
  separately exposes the native owner-restoration obligation without requiring
  exact entry wrapper equality in the post. No failed summary used.
- native-guard-prefix VF1 at23:24, Potential arithmetic overflow on len+16.
  With unrestricted safe native slices including ZST, array bounds need not
  imply len<=usizeMAX-16. Actual Rust checked overflow can panic; this profile
  requires a no-overflow proof at the operation before its panic route can
  establish the automatic full resource post. This is a conservative proof
  blocker, not evidence of an unsafe std operation or a semantic negative.
  Scratch abort/inline-const/selected-size proof remains NOT_RUN after this
  first failure. No arbitrary length/positive-size premise added.
- native-slice-cast-expression VF parser refusal at21:5. The unparenthesized
  ghost pointer equalities were not parsed; no primitive implementation proof
  credit. Parenthesized correction was begun before main end and saved DRAFT,
  Cloud NOT_RUN. No assertion or source guarantee removed.
- extra-runtime-body VF2, exact-one-body gate before any target entry.
- comment-only source mutation VF2, verified-source SHA gate before target.
  These fresh distinct refusals support the source/bodies admission boundary;
  neither is a semantic negative. The earlier wrong gate-order classifier was
  corrected using saved d5 replay before this fresh follow-up.

C1→C4/its five controls and unchanged native alias fixtures are explicitly
NOT_RUN in this follow-up, retaining their fresh d5 evidence. No matrix was
repeated. No native→C1/native→C4/actualcaller→sort4 credit or profile acceptance.
New strict-cut draft and selector work excluded; no trusted semantic delta.

The final started draft adds actual native earlyreturn to the resource/expression
components and a minimal safe usize-add overflow reproducer. It was NOT
dispatched, is disabled at session close, and has static syntax/recipe review
only. Its source, MIR, AST and proof statuses are all NOT_RUN. Reusing prior
admission controls in that draft gives no fresh-proof credit. A new phase would
need separate authorization; this session does not restart automatically.
