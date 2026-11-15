# W0-U submission checklist

2026-11-16. Owner-review package only. Publication, remote branch creation and CI remain coordinator/owner actions. This session uses no dispatch and spends Cloud $0. The U bucket in [the dispatch ledger](../../CH8-DISPATCH-LEDGER.md) permits at most one separately authorized integration dispatch; it grants no CI allowance to this text session.

## Review before publication

- [ ] Review [PR-01](../c2-slices/pr-texts/PR-01.md), [PR-02](../c2-slices/pr-texts/PR-02.md), the [design note](KANI3300-DESIGN-NOTE-DRAFT.md), the [single organizer question](ORGANIZER-QUESTION-DRAFT.md) and [evidence map](EVIDENCE-MAP.md). All remain drafts until the owner acts.
- [ ] Refresh Kani `main` and our existing [dependency #5172](https://github.com/model-checking/kani/pull/5172), including state, head, base and reviews. The metadata snapshot in the map is time-specific. Do not resubmit #5172. A changed identity stops the affected claim pending reconciliation.
- [ ] Verify immutable source identities and actual immediate parents: upstream `0aac16ef62da9e9d5645782d458593e5d78143ba` → B1 `6fe484b30043b3696b5f1ccc4bea0e42891ad012` → PR-01 `d82752c8bc878398e672bffaa631ca6a28430acc` → PR-02 `932fb8395a58f8c86c0d702ba2cae835823b2962`. Only the coordinator may create remote branches at these heads. Do not rewrite, rebase, cherry-pick or recommit accepted source as part of this package.
- [ ] Apply the **2026-11-16 approved W0-U trigger** in [INDEX, Submission triggers](../c2-slices/pr-texts/INDEX.md#submission-triggers): PR-01/02 may be published as stacked PRs, and the design note submitted for review, while parents are open. This overrides waiting for parent merges only for publication of PR-01/02 and submission of the note. It does not alter merge order or the parent-merge comparison/revalidation procedure, especially for PR-03–07.
- [ ] Decide and record Draft or ready-for-review status. Readiness requires applicable exact-head qualification, the actual parent and diff, and correctly attributed deferred integration evidence. PR-01's own run is regression/unit evidence only; it has no new end-to-end tests for the analysis feature on its own. Later cumulative-head tests do not establish standalone behavior on PR-01's head.

## Owner-only publication sequence

- [ ] Publish PR-01 only after reviewing its dependency and explicit cumulative diff against `main`, including open #5172. Actual PR-01 number: **OWNER TO RECORD AFTER CREATION**.
- [ ] Replace **every literal `#<PR-01>`** in PR-02 with that actual number before PR-02 publication. Do not invent a number. Verify PR-02 explicitly depends on PR-01 and #5172 and includes both ancestors in its diff against `main` while they remain unmerged.
- [ ] Recheck both titles, exact heads, tested claims, license confirmation and exact AI disclosure. Neither body claims to close #3300 or implies a single-commit diff against `main`. No coauthor trailers.
- [ ] Decide whether/when to post the design note to [Kani #3300](https://github.com/model-checking/kani/issues/3300). Its seven source slices and separate SEL1 qualification must stay distinct.
- [ ] Decide whether/when to post the one combined U/A7 message to [verify-rust-std #56](https://github.com/model-checking/verify-rust-std/issues/56). Do not duplicate it in #752. Request a pin-adoption route; do not report a requested pin bump as adopted.

## After parent merges / organizer response

- [ ] Preserve review/merge order #5172 → PR-01 → PR-02 → PR-03 → PR-04 → PR-05 → PR-06 → PR-07. Compare actual merged patches and resulting trees with pinned parents, including squash merges; follow INDEX's existing revalidation procedure. New source/test changes need new identities and applicable qualification. Historical receipts stay attached to their original heads.
- [ ] Keep the sorting campaign on std `872d5a43380752786415bc00d2a12ce0e930cb37` and clean upstream Kani `0aac16ef62da9e9d5645782d458593e5d78143ba`, with uninit/value checks OFF, independent of initialization-stack merging. Keep safety on its separately bound source, comparator and flags. Equal root names do not combine the claims.
- [ ] Record the organizer's actual decision on scope, tool pin and selected safety-step flags. Organizer integration requires an adopted compatible pin, accepted step and real organizer CI execution with useful checks; fork receipts or a skipped optional job do not satisfy that gate.

Validation for this handoff is static: source-object parent/tree checks, accepted-receipt consistency, text/reference/link checks and whitespace checks. No compiler, verifier, build, push, CI dispatch or publication occurs here. READY means this research package is committed and reviewable, not that Challenge 8 or upstream integration is complete.
