# Proof identity and isolated classifier replay

Tool `4a34010cc3930eec46fc4e72c1b793ad734fa730`; profile
`verifast-c4-select-composition-20261011-c3`. Actual proof used runner
`ca5f54607bf9e36ecbb9a24085cc6cc9e18db98c`, delivery
`84f21b3bf244eb352cb91584fc84a73d6703b117`, Build
`9397d5cd-51e6-4de4-87d0-e2195728f713`. Corrected runner and standalone auditor
are commit `8fd96ce4927c853ed6e02be6f9cba1fd4131eb05`;
Cloud execution of this classifier revision is NOT_RUN. Its saved-data replay
is sufficient for this authorized reclassification of unchanged semantic inputs.

Exact historical proof command (run from delivery84f21b3b, **D account CLOSED**):

```sh
python3 research/challenge-8/cloud-build/control.py \
  --state-dir /root/verify-rust-std-verifast-compose4/.verifast-c4-outer-d-state \
  --phase-id VERIFAST-C4-SELECT-OUTER-CLOUD-2026-10-11-D \
  --ledger research/challenge-8/cloud-build/verifast-c4-select-outer-d/BUDGET.json \
  --owner verifast submit \
  --infra-sha 84f21b3bf244eb352cb91584fc84a73d6703b117 \
  --proof-sha 84f21b3bf244eb352cb91584fc84a73d6703b117 \
  --lane verifast-c4-select-integration --timeout 1050
```

This pins the old execution, not authority to reopen a ledger. Any future proof
requires a separately authorized registration/account and reviewed exact inputs.
This session authorizes no Cloud/proof dispatch. Original summary remains FAILURE.

Replay on the saved extracted artifact root, from auditor8fd96ce4:

```sh
python3 research/challenge-8/cloud-build/verifast-c4-select-integration/outer_bool_auditor.py \
  --evidence-root /tmp/verifast-d-9397-extracted \
  --auditor-commit 8fd96ce4927c853ed6e02be6f9cba1fd4131eb05 \
  --output /tmp/verifast-bool-review-g/replay.json
python3 research/challenge-8/cloud-build/verifast-c4-select-integration/test_outer_bool_auditor.py \
  --evidence-root /tmp/verifast-d-9397-extracted \
  --output /tmp/verifast-bool-review-g/tests.json
```

The root is a read-only unpacking of
[the retained D archive](../verifast-c4-select-outer-d/raw/evidence.tar.gz), SHA256
`8a8428b2958176f9135841aa77dee2c96a1da72a3961a4183a8d957743aacf50`.
Only stdlib imports and saved/synthetic data are used. No proof-runner imports or
subprocess tools. Missing raw events are INCONCLUSIVE; self-consistent derivatives
cannot pass the fixed saved-Build identity gate. Original logs/summary/verdict
are not edited. Replay records auditor version/hash, original and new verdict,
Build/tool/runner/delivery/profile, finalAST/source/log and input-envelope hashes.

Expected: PASS_POSITIVE_LOCAL_HRTB_CLOSURE and CLASSIFIER_TESTS_PASS30.
This is not a fresh proof, historical Cloud SUCCESS or owner profile adoption.
