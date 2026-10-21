# A1 R12 S3 false31 partial and body-entry rationale

## Observed defect

S2's bounded `/observation_details/N-false31` record showed `KeyError: 'structure'`, with `execution_started=true`, `not_run=false`, and failure stage `N-false31-caller-raw-observed`. The exact path is `draft_false31_pair_stage`: it publishes and records the false31 own-pair receipt after both successful body/conformance observations, then `collect_source_case` returns a `BLOCKED_CHECKED_HELPER_PREREQUISITE` result that deliberately has `raw` and helper diagnostics but no `structure`. The runner persists this caller result and next calls `observe_false31_boundary`, which indexes `caller_case['structure']`.

## Applicability and rationale

The helper prerequisite is a real caller gate. Its blocked result must remain failed/inconclusive, while previously established same-pair P0a/P0b body facts, receipt ordering/path, and the returned helper record remain visible. Treating the result as an exception discards those facts from the case observation; treating it as a completed false31 boundary would be unsound. Return a distinct partial classification only when the caller result explicitly identifies the checked-helper block or lacks a mapping-valued structure, and retain the caller result unchanged. Do not compute a boundary or claim caller verification. The matrix classifier accepts only the exact completed classification and independently requires the caller, both same-pair bodies, and admissible boundary, so the partial row remains INCONCLUSIVE with no record or proof credit.

The second defect is a misplaced existing body-entry note/frame check. `body_entry_context` stopped after validating the unique error line and implicitly returned `None`; the already-written strict regex and exact single-frame condition were stranded after `_environment_sha256`'s return. Moving those lines back into `body_entry_context` restores its documented gate. The regex remains tied to the exact pinned body line and alias and requires exactly one matching post-error frame; no matching criterion is broadened.

## Controls

- False31 partials preserve `execution_started=true`, `not_run=false`, exact P0a/P0b pair observations, the issued receipt path/order, and the helper-blocked caller object; they explicitly mark caller verification NOT RUN and boundary/admission unavailable.
- Any unrelated exception from `collect_source_case` or later processing continues through the existing `action()` exception path unchanged.
- Synthetic tests exercise the helper-blocked caller path and actual matrix classifier, asserting INCONCLUSIVE, no matrix record/pass, and no proof credit.
- The matrix classifier recognizes only the new blocked-partial label to provide a precise inconclusive reason; every success prerequisite and acceptance predicate remains unchanged.
- Body-entry unit coverage is owned by the registration worker and must test exact positive-frame matching plus rejection of missing, duplicate, wrong-alias, and wrong-line frames.
- No compiler, verifier, extractor, full preparer, Cloud Build, evidence transport, or profile/pin behavior is changed by this runner fix.

## Evidence identity

S2 Build observation supplied by the coordinator: `/observation_details/N-false31`, request `134728c35b6b933bb551e8b83db7bbff9a5fc198c95ac6f51f68eee1f787d60f`; `adapter_error=KeyError: 'structure'`, `failed_stage=N-false31-caller-raw-observed`, `execution_started=true`, `not_run=false`, `proof_credit=false`. The bounded source-audit record is `A1-R12-S2-FALSE31-PARTIAL-TRACE-2026-10-21` (coordinator confirmed the partial `collect_source_case` result and helper block). A separate bounded receipt record `d32e3a…` (SHA-256 `9207f0434427b3912eb8a861b62f85ab73edc640ad79d13976663b5e43a6c614`) reported build `c08f…`, candidate `bfb…`, profile `a3544473d31e2ef69bab60eaa576debb2c6a89356d6c022e4f3d31386af2d828`, verified source `ad64622…`, original source `43238ed…`, and assurance `runner-reported-both-actual-bodies-and-native-conformance`; this is a source-reported issued receipt and grants no independent credit.
