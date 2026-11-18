# F4 conditional clone — full push-CI GO-request

READY_FOR_OWNER_GO, conditional on exact final-head binding. Independent11 review
`516bf3aea71ba7477ce06a1cab5bc956a00be23a` **APPROVE**, no blockers.
No dispatch or publication is performed by this request.

Candidate `ca1452227d6ad319f1b9bc1ad33bf618120733eb`, tree
`baedd51d92073ecb2b96991bae7dc562ee8f58a2`, direct parent
`b5a9678fd7c2a0f67c3fcafd90057fc2afaf9b5d`; package
`a16ef717e18ca8263e360c24058b13a3ef4d4605`. Clone is conditional on the exact
DelayedUbPass activation predicate; other runs reuse the shared transformer.
The existing fixture checks both modes and both feature call paths. New native
build, two-mode regression and performance results remain NOT_RUN.

Request: **one full native push-CI bundle**, prospective item1 **29/29**, on the
new final head. Run unchanged kani.yml with every job and all five regression OS
entries, format-check.yml and deny.yml. Preserve workflow conditions, native perf
retry, timeouts and continue-on-error settings; no additional manual reruns.
Release bundles, std verification and labeled benchmark comparisons remain
deferred to upstream PR CI under the owner's policy. All 16 workflows are unchanged.

Owner/coordinator creates a no-skip same-tree sibling of the local candidate,
with direct parent b5. The candidate has [skip ci] and must stay outside the
pushed b5..HEAD range. The final full SHA is NOT_CREATED; bind exact head/tree/parent,
remote ref and native event, run/attempt IDs and every job/matrix conclusion.
Use the reviewed check_push_head.py before publication. New CI needs separate GO.
Old run44274306776 covers the unconditional-copy b5 only; old macOS non-execution
and Deny external advisory remain historical facts. Preserve new native outcomes
and missing coverage; exceptions require owner classification, no silent green
status or automatic retries. Keep the new standard macOS entries in the matrix.

Review approval authorizes this request's preparation only. PR publication is
owner-only; recheck main drift read-only and hand off relevant changes explicitly.
The external PR draft already labels the old CI link as earlier and awaits new CI.

Reference usage: owner grant ledger968342e0af, item1 **28/29**, item2 provisional
**10/14**, total **38/43**. No new charge, reservation, CI, push, PR or label action
was performed. S2 charge/retry remains a separate owner decision.
