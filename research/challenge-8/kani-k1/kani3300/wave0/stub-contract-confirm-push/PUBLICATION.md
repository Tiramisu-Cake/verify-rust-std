# Coordinator final-head and request binding

Publication and CI remain coordinator-owned and outside this preparation. This document specifies the reviewable topology for a later UPDATED GO.

The source commit is exact main `faffcee3bca2770c03bd21c3bde89cc8f6f7a14e`. Proposed final ref: `refs/heads/stub-contract-confirm-ci/w15-push` in Tiramisu-Cake/kani. The coordinator must confirm the stock base already exists on the remote and that the proposed trigger ref is absent. The future operation creates that one ref once, from zero, without a force update, deletion, tag or extra ref. The introduced commit range relative to the already-present stock base is exactly `[FINAL]`; FINAL has the sole parent `faffcee3bca2770c03bd21c3bde89cc8f6f7a14e`. Existing refs and default-branch/workflow-enabled settings stay unchanged. If the ref already exists or any prerequisite changes, this topology has failed and needs an explicit new reviewed request.

Local reviewed candidate `e9f0e9a38bf679fead630c44eec3bc08ebb9202b` has no skip directive and tree `76ffe2048b88d45c759d0b297362c2c4981e7ad6`. Its preparation branch `w15/stub-contract-confirm-push` remains unpublished. The coordinator may propose that exact candidate, or create a direct sibling with the exact same tree, stock soleparent and profile digest `ceb930a5b7764799880ac48ad6318bbaf6e14d6af70ea98abbe9da82107af148`. A sibling changes only commit metadata, so its actual request digest must be recomputed. No skip candidate or range containing skip directives can be treated as an attempt. A final child of the candidate is rejected because its parent is wrong. Multi-parent commits and refs in place of exact SHA inputs are rejected.

Read-only gate commands, from this packet directory (replace FINAL_SHA with the exact proposed 40-hex commit):

```sh
PYTHONDONTWRITEBYTECODE=1 python3 check_push_head.py /root/kani-stub-contract-push-control-w15 FINAL_SHA refs/heads/stub-contract-confirm-ci/w15-push --derive-request
PYTHONDONTWRITEBYTECODE=1 python3 check_push_head.py /root/kani-stub-contract-push-control-w15 FINAL_SHA refs/heads/stub-contract-confirm-ci/w15-push --request EXPECTED_FINAL_REQUEST_SHA256
```

The first mode returns DERIVED_REQUIRES_EXACT_REQUEST_GATE and confers no acceptance. The second checks the explicit expected digest and returns FINAL_HEAD_REQUEST_GATE_PASS. It reads immutable packet pins and Git objects; it does not check out, commit, push, dispatch, enable a workflow or read/edit accounting. The wrapper and implementation are pinned by MANIFEST.json and INVENTORY.json. Final remote preconditions are coordinator checks; an offline PASS does not establish remote absence or authorization.

The future UPDATED GO-request must contain the containing g0 packet commit, SAME11 delta approval identity, actual FINAL SHA, tree, soleparent, exact ref, profile/workflow hashes and the gate's final request binding/digest. Candidate request `45b074506bd6e40e2f25bc1fc3603d1491bbbfda4c7a4295e40ec785cecb651c` applies only to `e9f0e9a38bf679fead630c44eec3bc08ebb9202b`. FINAL-HEAD-GATE.json records the read-only local candidate check; no real push event has occurred. Runtime snapshot.request and snapshot.request_sha256 must equal the final gate/UPDATED GO values during later artifact intake. Slot invocation identities inherit that same actual request digest.

The workflow checks the platform-provided required event name/repository/ref/SHA/payload against Git, rejects payload inputs and SC_CONTROL_HEAD/SC_CONTROL_TREE/SC_REQUEST_SHA256 even if they match, and derives the request. That derivation records actual identity; approval of the exact tree/profile/request remains the external immutable-packet/coordinator boundary. Runtime enforces new-branch created=true, before=zero, deleted=false and forced=false. Runtime also rejects a skip head. The test suite establishes both exact-candidate and same-tree-sibling paths, stale-request rejection, depth2 admission and pre-build rejection.

Only g0 evidence commits carry [skip ci] in this preparation. The isolated control candidate has a normal message so it can be reviewed as a possible final head; creation of a future publication ref remains a separate coordinator action.
