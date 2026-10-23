# N5 admission review

**Decision: GO for the scoped N5 phase admission/account/recipe change.** This review grants no Build dispatch authorization or proof credit. It does not close the N13 acceptance matrix.

## Reviewed identities

- Baseline: `f25aa438fdf204664217ed42aef93877328fda7a`
- Candidate: `5b4dba1627b9f0632faf9816ee611634b28351a8`
- Candidate tree: `d1c15796fd96c34dd71bda7baecf434d137918c3`
- Diff SHA-256: `f89b7f0f18ea7a1dc9f98af1418f795462786f0c5ce74fa72dd230db9bc38588`
- Spec SHA-256: `8f6c6842692073654c3a9099b2a7fdc8b7b1a749550e74f783a3db8df9ead365`
- Packet inventory SHA-256: `18fa7ad0dc0a4ac10622a15a4a3da55d71c35476c3a360e997220368f95e5ae5`

## Findings

- N5 is registered for owner `network`, the sole lane `network-n13`, phase `NETWORK-N13-EXACT-2026-10-24-N5`, the 10,800-second ceiling, and the exact T0/main/absolute deadlines `2026-10-23T10:48:37Z`, `2026-10-26T10:48:37Z`, and `2026-10-26T11:48:37Z`. Registration pins the unchanged N4-HANDOFF profile SHA-256 `08e016f4c97d919421b5325c41c98e94ea987162d44681be04dc91b1476f6e13`.
- The new account has the matching owner, lane, phase, ceiling, deadlines, timeout ceiling, and report reserve. The recipe substitutes the N5 ledger and retains the existing N13 stages, entrypoint, proof paths, and profile path.
- The order-negative stage remains 600 seconds case time / 975 seconds Build timeout; standalone universal remains 480 / 855. The existing gate checks the pinned profile stage values, exact registered stage and recipe, the timeout envelope, the 60-second queue reserve against the main deadline, and the 270–1200-second timeout bounds.
- The existing N4 ledger is byte-identical across baseline and candidate (SHA-256 `c203996b38bbeecafa5eccf43dbd94ab6d2543ca6a4d3529e29127b227098068`); the handoff profile is also byte-identical (SHA-256 `08e016f4c97d919421b5325c41c98e94ea987162d44681be04dc91b1476f6e13`). No shared coordinator or transport file is changed. I found no weakened gate or removed control in the reviewed diff.

## Validation and limits

- `test_network_n13_client.py`: 15 tests passed, including exact-account admission and refusals for mismatched/draft accounts, shortened timeouts, unregistered stages, and an envelope that exceeds the main window.
- `test_admission.py`: 3 tests passed. `test_run_cloud.py`: 12 tests passed, preserving the existing malformed, partial, mismatch, and failure-path controls.
- `git diff --check` passed for baseline to candidate.
- Review was static plus isolated synthetic tests only. No generator, compiler, verifier, Cloud operation, or raw evidence was used. N5 Builds and full N13 matrix acceptance remain unverified/open.
