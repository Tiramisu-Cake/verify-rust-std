# R12 S1 integration review

**Decision: GO for the bounded S1 attempt, with proof credit pending actual same-Build verifier results.** The registration and grammar-preflight path are fail-closed after the two concrete control issues found during review were corrected. This GO permits the experiment; it is not helper-body acceptance, P0c/P1 proof credit, or matrix admission.

## Registration and historical boundary

R12 uses a fresh 3600-second ledger, exact Select owner and existing lane, explicit R12 authorization phase, and the preserved historical A1 protocol phase. The control, lane, recipe, profile, entry adapter, R12 runner adapter, shared runner/backend/tool routes, and source-restoration setup bind the R12 profile. XZ transport is enabled only for R10–R12 and preserves source bytes; coordinator capacity remains authoritative for R12, while the earlier A1 two-slot guard remains on historical phases. R11 profile and ledger records remain unchanged and closed. The active R12 entry, runner, source-runner, helper files, grammar module, helper block, and import hashes all match the R12 profile.

## Grammar preflight and proof boundary

The new grammar module runs after exact tool reconstruction and before canonical fixture construction. It creates three fresh verified/original source pairs: standalone module-level import plus the helper and exported Option anchor; the fully qualified constructor negative; and the prior S5-style bare `use` placed inside the helper declaration block. It binds each source pair, checks the active reconstructed tool identity before and after the verifier stages, requires the positive run to emit an AST selecting exactly one source-located manual helper lemma, and requires each negative to produce its expected diagnostic at the expected source line. The minimal environment contains no A1 summary/stage controls. The record carries neither proof credit nor caller receipt.

Any failed, missing, malformed, partial, deadline-limited, source/tool-mismatched, or diagnostic-mismatched preflight blocks dependent work and preserves its details; all 26 matrix rows stay `NOT_RUN`. On a grammar pass, the ordinary same-Build checked-helper proof remains required on each canonical source pair before the caller or P1 can consume it. The grammar preflight does not prove the `Some` ownership obligation, and its positive exit is not a helper-body result.

During review I found two concrete negative-control defects and returned them to the owner: the S5 control inserted the standalone `//@ use` marker inside the ghost block instead of the prior bare `use` declaration, and it expected the parse error on the import line rather than on the following lemma line reported by S5. The stable delta now strips the marker for the in-block negative, anchors the expected parse error at `lem a1_cleanup_option_ref`, and tests that the same parse diagnostic on the wrong line is rejected.

## Validation and attempt bound

Validation passed: 11 grammar-preflight synthetic tests, 7 R12 registration/transport tests, 11 profile-binding tests, 6 observer-helper construction tests, 17 checked-helper receipt-gate tests, and 2 historical R11 registration tests. Python compilation, shell syntax, JSON parsing, and `git diff --check` also passed. The R12 profile’s entry, runner, source-runner, every ordinary helper, grammar module, helper block, and import pins matched current files. No compiler, extractor, preparer, verifier, full runner, or Cloud Build was invoked in this review.

The bounded profile uses a 1000-second Build timeout, 760-second execute cap, 700-second nominal work deadline, 240-second report reserve, and 60-second inner margin. The 1060-second envelope fits the fresh phase budget. Prior target runtimes plus three grammar-stage caps do not establish execution fit; keep fit **UNESTABLISHED**. If the preflight or target cannot finish within the caps, preserve partial/`NOT_RUN`/`INCONCLUSIVE` outcomes and make no acceptance claim. The eventual 26-row matrix remains mandatory in one same-Build run after prerequisites pass.

## Static-closure follow-up

I reviewed the subsequent recipe-only closure delta. Both `infra_paths` and `proof_paths` retain their exact prior membership and counts (36 and 118); each list is now lexicographically sorted. This ordering-only change does not alter the R12 registration or evidence scope, and I see no new blocker.
