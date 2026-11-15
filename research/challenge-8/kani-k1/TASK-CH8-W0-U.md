# Challenge 8, item 1 — W0-U upstream package preparation

2026-11-16. This is correctness verification, not security work.

**Worker:** worker14
**Window:** one bounded session; stop after the deliverables below are reviewable.
**Authority:** the owner approved all six decisions in `PLAN-CH8-ITEM1-REMAINING-v2.md` at `dea4b12168` and launched wave 0. This assignment prepares the W0-U submission package only. It does not authorize publication, CI, or implementation work.

## Objective

Prepare an English, owner-reviewable upstream package for the fork-qualified Kani `#3300` work: finalize the two existing stacked PR bodies for PR-01 and PR-02, prepare a design-note draft and one organizer-question draft, and record evidence and a submission checklist. The stack and SEL1 are related evidence, not one source head or one completed challenge proof.

## Required inputs and identity checks

Read `/root/AGENTS.md`, this task, and the relevant sections of `PLAN-CH8-ITEM1-REMAINING-v2.md` (especially §§3–4 and U1–U2). Use the existing drafts and accepted evidence as the factual authority:

- Existing PR bodies: `kani3300/c2-slices/pr-texts/PR-01.md` and `PR-02.md`, baseline `bab3aada59`; their other draft files and `INDEX.md` are context only, except for the narrowly authorized INDEX update below.
- Exact PR-01 source head: `d82752c8bc878398e672bffaa631ca6a28430acc`, parent B1 `6fe484b30043b3696b5f1ccc4bea0e42891ad012`.
- Exact PR-02 source head: `932fb8395a58f8c86c0d702ba2cae835823b2962`, parent PR-01.
- Existing dependency: Kani `#5172`, source head `6fe484b30043b3696b5f1ccc4bea0e42891ad012`, based on upstream `0aac16ef62da9e9d5645782d458593e5d78143ba`. It is not to be resubmitted. Refresh current upstream and GitHub PR metadata read-only if available; record timestamp and exact metadata. Do not inspect CI logs.
- Current accepted SEL1 evidence: `kani3300/sel1-c2/quick/ci-43740679160/ACCEPTANCE.md`, `kani3300/sel1-c2/gatea/run-43744142824/ACCEPTANCE.md`, and `kani3300/sel1-c2/replay/run-43751703000/RESULT.md`.
- Use the accepted source maps, design/review notes, and bounded run summaries for the C2 stack. Keep each evidence item tied to its exact source/pin and distinguish fork evidence, bounded challenge results, and organizer integration evidence.

If any pinned source identity or accepted receipt does not match, stop that claim, record the mismatch, and do not move, rewrite, recommit, rebase, or cherry-pick accepted source. Text-only work may continue where the mismatch does not affect it.

## Deliverables and authorized write scope

Write the supporting package under `kani3300/w0-u/`:

1. `SUBMISSION-CHECKLIST.md` — owner review and publication checklist, including exact-head/dependency verification, stacked-diff disclosure, ready-for-review gate, and the owner-only PR-number step.
2. `KANI3300-DESIGN-NOTE-DRAFT.md` — an English RFC-style draft for issue `#3300`.
3. `ORGANIZER-QUESTION-DRAFT.md` — one concise English question intended for either verify-rust-std `#56` or `#752`; choose one primary thread and do not duplicate-post.
4. `EVIDENCE-MAP.md` — compact source/head/run-to-claim map with limitations and freshness notes.

Finalize only the existing `kani3300/c2-slices/pr-texts/PR-01.md` and `PR-02.md`. A minimal `INDEX.md` update is authorized to add a clearly dated W0-U trigger that explicitly overrides waiting for parent merges for publication of PR-01/02 as stacked PRs and submission of the design note for review. The owner chooses Draft or ready status. This override applies only to PR-01/02; retain the existing merge, exact-patch comparison, and revalidation procedure after parents merge, especially for PR-03–07. Amend or clearly subordinate the existing trigger wording so the index has no contradictory or duplicated triggers. Do not rewrite the index or restate the seven-PR plan. The checklist must identify the new W0-U trigger and its limited override scope.

Do not write or edit any other paths. Keep every deliverable and any proposed publishable text in English.

## PR-01/02 acceptance criteria

- Preserve titles, scope, tested claims, limitation boundaries, and source identities. Do not imply either PR closes `#3300`.
- State the dependency chain and cumulative-diff fact explicitly: PR-01 is based on open `#5172`; PR-02 is based on PR-01. Until parents merge, each stacked PR includes its ancestors in its diff against `main`.
- PR-01 has **no new end-to-end tests for this analysis feature on its own**. Label its exact-head run as regression/unit evidence only. Clearly identify its later integration evidence on cumulative heads 4/5 as deferred tests, not tests run on PR-01's head. Do not claim the later results establish standalone PR-01 behavior.
- PR-02 must include a literal placeholder for the actual PR-01 number in its dependency and cumulative-diff wording. The owner fills it after PR-01 exists. Never invent a PR number or leave wording that suggests a single-commit diff against `main`.
- Use only permitted references: Kani issue `#3300`, the user's own Kani dependency PR `#5172`, and verify-rust-std issue `#56` or our verify-rust-std PR `#752`. Do not add references to unrelated/foreign pull requests or competitors.
- Include this exact disclosure in **each** publishable text: `*Disclosure: this change and description were prepared with the help of AI assistants.*`
- Do not add `Co-Authored-By` trailers.
- Keep the existing license confirmation where appropriate. Do not claim publication, review, merge, or organizer acceptance.

## Design-note content

Use an RFC structure with a clear problem statement, goals/non-goals, proposed architecture, alternatives, evaluation/evidence, limitations, and questions for reviewers. Cover, with precise distinctions:

- the challenge and accepted experimental scope, the seven dependent PR slices and their dependency order, and SEL1 as a separately qualified fallback/change rather than part of the seven-PR source stack;
- the one-witness shadow-state model and its false-versus-true byte masks; direct MIR-body call/transfer handling; selected-body analysis and call-cycle behavior;
- whole immutable allocation mask seeding versus permission to write memory (initialization metadata must not be described as granting mutability or access);
- selected contract/closure bodies, initialization of ordinary argument slots, delayed-body mutation and per-root isolation, and what the structural isolation checks actually establish;
- alternatives considered and why they are deferred or rejected, without proposing a new compiler model or expanding the accepted source scope;
- the precise bounded challenge harness outcomes and measured costs supported by accepted receipts, with exact run/source associations. Include geometry/target limits and `-Z valid-value-checks` status where relevant. Do not imply that a bounded replay is a whole-module proof or that it supplies organizer CI integration;
- known unsupported or unqualified cases: function-pointer/trait-object call dispatch, `stub_verified` (Replace) and `kani::recursion` shadow transfer, delayed-analysis cycles, and other source/evidence limits. Treat loop-contract havoc interactions as unqualified/open unless an actual control establishes their behavior;
- the SEL1 Quick, Gate A, and replay chain with their counts, platforms, flags, and explicit boundaries: bounded closure-comparator evidence, `-Z valid-value-checks` OFF, not all `T/N`, not the function-pointer comparator profile, not the whole module, and `#5104` not addressed. Gate A's curated acceptance reports 41/40/76 minutes for ubuntu-24.04, ubuntu-24.04-arm, and macos-15. The replay result does not report timing or RSS; record those costs as unknown. Do not attribute an older C2 B′ measurement to SEL1. Older measured costs may be included only when clearly pinned to their own source/run and scope.

Do not turn source-reported claims into independent proof credit. Do not call the seven PRs merged or accepted upstream. Keep technical alternatives and open decisions framed as questions for maintainers, not as adopted architecture. Describe actual behavior in the publishable English note, without internal research-stage labels.

## Organizer question

Prepare one short, respectful draft for verify-rust-std issue `#56` or our verify-rust-std PR `#752`, asking whether the challenge requires `insertion_sort_shift_left` for arbitrary valid length/offset beyond the caller's representative thresholds; whether representative types covering all observed type/size/specialization branches suffice or a generic-`T` theorem is required; and whether selected SmallSort harnesses may use a separate `-Z uninit-checks` CI step, with any later `-Z valid-value-checks` step separately qualified. Ask which upstream pin/integration route is expected. Preserve the distinction between a proposal and an accepted ruling. Include the required disclosure. The owner posts it; worker14 does not.

## Checklist and INDEX handoff

The checklist must require the owner to:

- review all text and evidence map, refresh `#5172`/main metadata, and verify the exact source heads and parent relationships;
- decide and record the actual PR-01 number after creating it, then replace the PR-02 placeholder before PR-02 publication;
- ensure both descriptions disclose cumulative diffs against `main`, exact-head test scope, and the deferred integration evidence;
- review and decide whether/when to post the design note and the one organizer question; only the owner publishes;
- preserve review order and source immutability. Exact source heads are fixed; only the coordinator may create remote branches at those heads.

The INDEX insertion should state only the new approved W0-U trigger and link the checklist/design note. It must not erase or silently supersede the existing merge-order procedure.

## Boundaries and handoff

Permitted work is limited to static research, read-only metadata refresh, and the text deliverables above. No local Kani branch or Kani source change; no source rewrite, rebase, cherry-pick, or recommit; no push, PR/issue creation, posting, or publication; no CI dispatch or build. Do not run cargo, rustc, Kani, CBMC, or Miri. Cloud spend remains `$0`.

Commit only the authorized research/text outputs with `[skip ci]`, setting both author and committer per command to `Tiramisu-Cake <igkharin@gmail.com>` via Git `-c`; do not push. Finish with a compact handoff that lists changed paths, metadata freshness, any unresolved mismatch, and `READY <research-sha>` only if the research outputs are committed and reviewable. Do not claim completion of the challenge or upstream gate.
