# Next frontier after R19 S2: actual selectors (design note, not implemented)

## Observation

S2 (Build `8916761a`, pins `3af7d37d`, profile `c7bbbc46`): the actual sort4 body passes c1–c4 on the first explored path and fails once, at `lib.rs:371 let min = hint::select_unpredictable(c3, c, a);` with `No such function: std::hint::select_unpredictable` ([S2-evidence.json](S2-evidence.json)). The actual-body route exports no body or spec for the generic `core::hint::select_unpredictable::<*const T>`, so the first of the eight selector calls cannot be verified. Causality UNKNOWN; credit0.

## Applicability and constraints

- CORE allows a summary only with a proof of the actual callee of the same version. An unchecked spec for `select_unpredictable` would be an assumed summary, so it is not allowed.
- The actual callee thread (`SORT4-SELECT-CALLEE.md`, `SORT4-SELECT-POINTER-RESULTS.md`) is open. S6v4 accepted only components; S7b did not accept the auxiliary generic body or the actual linkage, and the last actual run stops at forget guard-own (`std/lib.rsspec:420`). The translator still contains that route (`Sort4SelectIntrinsic`, activated only by `SORT4_SELECT_INTRINSIC_REPO_ROOT` with its own helper and probe inventory), but the R17-chain actual-body route does not enable it.
- `a1-actual-selector-permutation.rs` is a checked pure selector/permutation component. It does not replace the callee proof.

## Options (owner/mission choice)

1. **Close the actual callee first (Select mission, W1).** Finish the S7 `select_unpredictable::<*const T>` proof: forget guard-own, then the actual linkage. After that, include the actual hint body and intrinsic chain in the sort4 crate with checked callee specs, and expose it to the actual-body route under an explicit opt-in with source/MIR certification. This is a new overlay/profile, so it needs review.
2. **Route the existing certified intrinsic path into the actual body.** This means enabling `Sort4SelectIntrinsic` (the actual graph certificate plus checked pointer helper) for `sort4_stable`. It needs the same callee acceptance that S7b lacked, so it is not admissible until option 1's blockers are closed.

Until one of these lands, c5 (prepared and reviewed, candidate `6f76ab3b`), the copies and the final posts cannot be reached on the actual path.

## Carried candidate and transport

- Candidate `6f76ab3b` (count-5 overlay, result `df541233`; c5 layer for `unknown_right`/`unknown_left`; profile `5a15addd`) is reviewed GO_WITH_NITS. Its precondition (S2 reaching c5) is **not met**, so it was not submitted. It becomes useful once the selectors verify.
- The pinned source transport is at its cap: S1 used 191/191 chunks, and S2 fit only after the R16-route-only files were dropped. `6f76ab3b` needs 192. Dropping the closed R17 profile from the recipe measured 191 chunks with 882 bytes spare (not committed). Selector work will add more and will need a transport plan (closure pruning of closed routes, or an owner decision on the transport cap).

## Controls to carry

- c3 controls were not rerun at count 4 and c4 controls are not rerun at count 5. The final matrix needs a count-independent re-qualification.
- Frontend controls are observed only as prerequisite failures; the refusal reason is not observed.
- All c-results are path-partial until the whole body verifies on every (c1..c4) path.
