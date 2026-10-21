# Select-R13 semantic/probe review

**Decision: conditional GO for the bounded Cloud probe.** Static inspection finds
the new shared-reference ownership mapping matches the existing pinned RustBelt
interpreter representation. The review does not establish parser acceptance,
actual source applicability, or verifier behavior; those remain the probe's
Cloud questions.

## Semantic correspondence

At pinned tool head `f76012fb518703b1d98e243ac4f487f16877cfcb`,
`translate_ref_ty`'s `Mir.Not` branch sets reference `.own` to the pointee's
`ptee_shr` callback. `RustBelt.shr` is documented as duplicable, and
`general.rsspec` already defines `shared_ref_own` as a dummy-coefficient
pointee share. The added `shared_ref_type_own<'a,T>` body is exactly
`[_](<T>.share)('a,t,r)`. Its registration matches only `&'a T`; it does not
match `&'a mut T`. The lifetime and pointee type are both parameters, and the
wrapper has the same `(thread_id_t, &'a T)` predicate arguments as `.own`.
Generic `Option_own` therefore resolves its shared-reference field through the
same representation the translator assigns, while a non-reference field keeps
its existing `<T>.own` predicate.

The inspected f760 blobs are `general.rsspec` SHA-256
`ef2ff16dffd472bbc5fd7fa17e7f13a03d83919520da5ce7e2d7095194790d1d`,
`vf_mir_translator.ml` SHA-256
`c1eb897673f88b0b8dc50798deca603bdad2c60818b6d5380ccf1dda055fe445`, and
`rustbelt.ml` SHA-256
`91905bc6a3812a3eb0de6bcc965e658eb86bc948d887a7bf4de7f1baec9b3aa0`.
The proposed normalization patch is pinned as
`a91484d3c556c84d6f89f95b8cccb07505edd249c1747a8523d7d6838b714e47`,
with expected result SHA-256
`d24d3bc884b40b57ba4a6ff7ed20753a6f8a6bfffc2937558ca87d40c9d28620`.

The patch adds no lemma, axiom, or reverse use of `close_ref_own`. However,
`type_pred_def` installs its equality through the existing type-predicate
definition machinery, which uses `assume_forall`; describe this accurately as a
new explicit definitional registration whose soundness relies on exact
correspondence to the translator. Do not claim the registration is a theorem
derived from the former opaque symbol. The manifest's narrower
`new_axiom_or_assumed_lemma: false` is consistent if it means no axiom/lemma was
added, while the review and profile retain the trusted definition identity.

## Probe scope and fail-closed behavior

The seven variants cover the canonical generic `Option<&'a T>` helper, `Some`
extraction preserving the share, shared-reference roundtrip, generic
non-reference roundtrip, generic erasure refusal, mutable-reference erasure
refusal, and lifetime-redirection refusal. Each variant uses a checked ghost
lemma with the same helper name and source interval gate; the canonical helper
contains both `None` and `Some`, with no `Copy` or `Freeze` requirement.
The negative controls expect one matching verifier diagnostic in that lemma's
body interval and terminal exit 1. Positive controls require terminal exit 0
and no diagnostics. Missing stages, timeouts, wrong exits, stale log hashes,
missing AST selection, unexpected diagnostics, and tool hash changes classify
as inconclusive. The mode exits before matrix classification and sets
`accepted`, caller receipt, matrix admission, and proof credit false.

The progress snapshot uses same-directory atomic replacement and contains only
compact status, identities, and non-admission fields. Explicit `not_run` events
are required for `NOT_RUN`; started work stays inconclusive and unseen rows stay
unknown. The recovery wrapper copies the current `diagnostic-audit.json` on
success and ordinary nonzero/timeout stage exits, so the last complete snapshot
remains the packaged audit when the wrapper regains control. A hard external
kill cannot guarantee the wrapper copy. The probe also writes its own
per-variant audit after each terminal stage; neither artifact contains proof
credit.

The first review found that the final `passed` rewrite used a direct
`Path.write_text`, which could truncate the complete seven-variant snapshot on
a hard kill. The implementation now publishes this final document with the
same temp-file plus `os.replace` pattern as the per-variant snapshots. I also
checked the added R13 focus guard: it requires exact equality between the
normalized-spec profile and reconstruction receipt before backend use. Both
localized issues are resolved.

## Remaining gates

Decision: GO to the bounded Cloud compile preflight and probe once the
coordinator profile refreshes and independently verifies exact pins for the
final `general.rsspec` patch, tool, runner, fixtures, probe, ghost grammar
helper, and progress writer/tests. A PASS on this mini-unit remains intermediate
evidence: it does not provide the canonical P0c helper/caller receipt, native
P1 acceptance, matrix admission, or B1/B2 credit. Keep all seven source/span
and intended-resource controls in the same probe Build, and keep any timeout or
missing row inconclusive.

No compiler, preparer, exporter, or verifier was run for this review.
