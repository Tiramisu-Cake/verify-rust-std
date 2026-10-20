# R6 candidate 1 independent review — 2026-10-20

**Decision: GO for the authorized Cloud candidate build** at the reviewed source hashes below, subject to the current preflight/pinned-input gates. Independent reviewer: GPT-6 Luna, HIGH reasoning, `fork_turns=none`, no nested delegation. This is an implementation review, not proof evidence or proof credit. No compiler/verifier was run for this review.

The actual late-call preparation now derives the share from each exact post-initialization physical coefficient and FBC, converts that borrow with the existing `borrow` / `full_borrow_into_frac` / `frac_borrow_implies_scaled` rules, then invokes the checked representation helper for the same `r5_late_k`, thread, and referent before `close_ref_own` and tuple ownership. The helper binds the actual fraction before folding and leaks that fractional predicate to the dummy share required by the postcondition. Its monotonicity companion follows the existing `u32_share_mono` close-and-leak pattern. The R5 missing-share issue is addressed by an explicit u64 type-predicate representation definition whose body matches the pinned primitive share semantics and translator; the helper proves resource folding under that definition. It does not establish the model definition as a theorem.

The first review found missing `leak` steps after fractional predicate closes. The current diff includes those steps in both helpers. The representation controls check one positive bridge call and reject missing resource, wrong referent, wrong lifetime, and wrong thread at the helper precondition. The classifier requires exact source hashes and stage receipts, the caller target to be the last executed statement before the error, and the error at the recorded bridge precondition. Synthetic service tests also cover wrong error location and setup/receipt failures. These controls remain diagnostics and do not qualify actual `insert_tail` proof credit.

R6 registration matches the authorized merge account: 3600-second ceiling, exact start/main/finishing timestamps, merge-only lane, pinned objects, 90–900-second submission timeout, no new submit/request after main deadline, and the second authorization check before reserve. The merge recipe includes the new controls module. No discrepancy was found in the reviewed registration.

The source remains an intentional partial diagnostic: lifetime exit, exact `borrow_end`, both `end_ref_readonly` obligations, CURRENT recovery, guard Drop, and normal/unwind resource return remain open gates. A green share control or reached late call does not close them. Preserve those distinctions in reporting.

Reviewed tool baseline: `45594fb821805f10c4e05f02912d1ea3bf920e62` (clean worktree).

| Changed input | SHA-256 |
|---|---|
| `first-callback.py` | `47676d3cd0a288688ce39d62cea69cac5d4cc72b93c2b80b529e1914c9ad514c` |
| `r6-share-controls.py` | `c532ef4dc43d5b71a99e3e46e1fe990f876c378ea70c1d55c7babb5439fbd699` |
| `CANONICAL-SHARE-R6-BUDGET-20261020.json` | `b8e12bbbcc10691a964c3349b9215bef933b8bf4c51db45eb026d117d7fe4571` |
| `control.py` | `60cb022717abb6b29b37d82b2a16d6f47a5b3aedd04abd531ffe1c6dd17c2c06` |
| `recipes/merge.json` | `be500d2bb070d1142c0505b43971748cc29bee0a2b4d370f23d0022353ba6e1f` |
| `FIRST-CALLBACK-SEMANTIC-CARD-20261017.md` | `2eb04e768cab145b0e71beb7897e28aecab1fa2d295edee389b6ef56c0d423ce` |
| `r6-share-controls-service-test.py` | `3098ab8a8c95c48ebd56d909a24d6e16cd2f308a4dfeb7f20ec9ba18de1e6bd1` |
| `r6-phase-service-test.py` | `90db3204bc5ec7df4d5415a66f9085f5e6af9719a834ecef4577382f1f8ad578` |

The main agent reports both synthetic service suites pass (share controls 4/4; phase registration 5/5). This review did not rerun them. The review applies to the hashes listed here; any subsequent edit requires a hash refresh and delta review.
