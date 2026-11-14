# C2-S5 candidate CI — run 43641978948

- Candidate head: 8d67298c48eb7b2381f806a6353433d1440e3d94 (fix/kani-3300-c2-s5), parent 6d2e9ae621.
- CI-only commit: 45efcdcbbd (workflow `uninit-quick.yml` = scratchpad `s5-candidate.yml` with `--force-rerun`, plus `.github/s5sens/*.patch`), branch `uninit-ci/c2-s5-cand2`, ubuntu-24.04.
- Conclusion: success.

| Step | Result |
|---|---|
| fmt / build / clippy | PASS |
| unit tests | 6/0, 2/0, 9/0 |
| kani suite (uninit) | 24 passed / 0 failed |
| expected (uninit) | 228 passed / 0 failed / 2 ignored (pre-existing `slices_fixme.rs`, `fixme_unions.rs`) |
| ui | 17/0 |
| script-based-pre | 2/0 |
| json-handler (all) | 17/0 |

Sensitivity mutations (each applied, selector rerun with `--force-rerun`, reverted):

| Mutation | Selector | Result |
|---|---|---|
| positive-remove-useful-assertion | uninit/private-transfer-frame/lawful-modifies | DETECTED (exit 1) |
| negative-extra-reached-failure | uninit/maybe-uninit-contract-frame/main | DETECTED (exit 1) |
| negative-repair-user-write | uninit/maybe-uninit-contract-frame/main | DETECTED (exit 1) |
| golden-invert-required-count | uninit/private-transfer-frame/lawful-modifies | DETECTED (exit 1) |

Previous run 43636027466 (head 6d2e9ae621): two `contract-modes/replace-transfer*` compile errors (missing local `proof_for_contract` for `stub_verified`), mutation step invalid (no `--force-rerun`, tests reported ignored). Both fixed here.

Verdict: S5 ACCEPTED by coordinator.
