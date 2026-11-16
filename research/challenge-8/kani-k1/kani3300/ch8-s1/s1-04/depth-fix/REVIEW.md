# Independent review: S1-04 depth fix

**Result: PASS for the bounded checkout-depth delta.** Reviewed candidate `205b0e98c771a7e6c6b8ec28414494868bcca4e0` (sole parent `40b5d9cf48900ff1e227e1fbba24cb5b2edbf8d5`) against sibling `2a532e5913173d6af4490c25d74c587f7bf1a749`. Packet inventory SHA256: `f950bdd8a8daf63ba87b97a5c01d876b39d8ddd822bd586682f4761c48338c5e`; spec SHA256: `6bc96e20f2885dd8b660af55bf83a0efa80796fd126b4c5c38dd3efc07192fee`.

## Findings

No correctness issue found in the reviewed delta. All four workflow jobs set only the control checkout depth from 2 to 3; export and tool remain at 2. `check_package.check_yaml` enforces control/export/tool depths of 3/2/2 in each job. This matches the control graph used by `control()`: `HEAD` → `HEAD^` (control parent) → pinned tool commit, with the latter required as the `git diff` endpoint. `runner.verify_source()` checks the checked-out source/tool HEAD, tree, object type, and cleanliness; it does not require older history, so depth 2 remains sufficient there.

The regression test covers all 12 checkouts across the four jobs with actual shallow `file://` clones and no alternates. It invokes the real `control()` and `verify_source()` checks, checks the control diff and shallow boundary, rejects bad depths through the typed YAML preflight, reproduces depth-2 diff failure (exit 128), and checks that depth 1 lacks `HEAD^`. Workflow comparison against the sibling is equal after normalizing only the four control fetch depths. Request comparison shows only `ci_payload_sha256` changed, with exactly the workflow, `check_package.py`, and `test_package.py` entries updated. Candidate parent and author match the stated invariants; commit message has no skip-CI marker.

The inspected g0 `s1-04/validate.py` and `yaml-fix/validate.py` include local metadata/history comparisons (`git diff`/`git show` against older fixed commits). They are not run by the workflow; their OLD-vs-HEAD comparisons need the full local history as described in the packet limitation. The new shallow regression appropriately exercises the workflow preflight operations instead of claiming those local historical comparisons work in a shallow checkout.

## Validation and limits

Ran only the two authorized targeted tests:

- `test_checkout_depth_policy_in_every_job` — PASS
- `test_every_checkout_shallow_clone_runs_real_identity_operations` — PASS

No full suite, CI/build, compiler, verifier, or proof execution was run. This is a bounded code review; it grants no proof credit (`NONE`) and makes no claim about GitHub Actions server acceptance or production CI execution.
