# C2-S3 result — confirmed pairs and docs follow-up

READY `ad324418cdc66b18e9b71f76a412be6ccea20c7e`

Docs-only commit, tree `b7e9e8ffa7212c1c41299c32ebd0b72fd9951a68`, parent
`5ca3cbf2e913e9c9b1d81cad3bce598964bafeac`, branch `fix/kani-3300-c2-s3`
in `/root/kani-fix-3300-c2-s3`. Author and committer Tiramisu-Cake
<igkharin@gmail.com> through git -c. Source worktree clean.

## Confirmed distinguishing pairs

Coordinator report: [ci-2/CI-RESULT.md](ci-2/CI-RESULT.md), SHA256
`5241ed88cc944c9d11f6b7d7b4bdab6a7fbd1d8044024b76b62a586797b4f2df`. These are supplied coordinator CI results, not a worker rerun
or an independently reconstructed proof/MIR inventory.

| Control | Baseline run 43614612145 | Candidate run 43614615441 |
| --- | --- | --- |
| moved-from-source | False VERIFICATION SUCCESSFUL; 0 of 183 failed; expected-negative selector fails | Exactly one intended raw `*const u8` uninitialized-read failure; selector passes |
| repeated-destination | False VERIFICATION SUCCESSFUL; 0 of 189 failed; expected-negative selector fails | Exactly one intended raw `*const u8` uninitialized-read failure; selector passes |
| reinit-companion | Legal control passes | Legal control passes |

Baseline is exact bf8170b28afb682f8dd55a94199caa247736d8fa plus
controls-v2/baseline-tests.patch, tree 1356cb004836d69fa0c234801e9c0600a7146167,
with CI-only overlay 8cf1626b30. Patch SHA256
`f93a436385b739261459853b0d173ad9afe343d2dd26cd960e5be18fc2cf2f05`.
Tested candidate is 5ca3cbf2e913e9c9b1d81cad3bce598964bafeac with CI-only
1b9be0f53b. Its fixture sources, goldens and flags match the baseline package.
Coordinator confirms both F6 paths reproduced and fixed by the candidate;
targeted nested-aggregate-reset 3/3, fmt/build/clippy PASS.

Earlier CI1 (baseline43611505688, candidate43611509452) remains
NONDISCRIMINATING: all three old-form fixtures stopped at the existing Nested
pointer/layout guard before the target reads. No credit is taken from those
failures. Historical excerpts and preparation records are retained.

## Boundary and documentation

Existing static source coverage/extent/order review is in REVIEW.md and
RESET-COVERAGE-MAP.md. Actual Move source resets follow all supported argument
snapshots and precede the Call. Exact destination full-storage reset occurs on
normal continuation only. The tests preserve the same destination across two
returns or retain the address of the original live moved source; controls-v2
uses direct byte-field pointers, fieldwise construction and no whole-Nested
assignment. New CI confirms the distinguishing observations; full consumed-MIR
identity/offset/alias bindings were not independently reconstructed by this
worker from the summary.

Task §5 now permits docs narrowing after the coverage review and two confirmed
pairs. The sole source change in this follow-up is
`docs/src/reference/experimental/contracts.md`: it describes conservative
full-storage reset for sized aggregates rejected by the nested-union layout
check, normal-return destinations and moved call sources. It retains possible
false positives, absence of nested shadow transfer support, whole-value
Unsupported, the known initialized tuple-return false positive and the advice
to return a supported top-level slot. It makes no blanket aggregate-support,
full-soundness or whole-#3300 claim.

Production and tests are unchanged from tested 5ca3cbf2e9. Runtime, F5, DFCC,
F7/cache, SEL1/F8, existing controls, composition roots/checker/allowlist and
base/pins are unchanged. S4/S5 were not started.

## Validation and remaining limits

Docs diff inspected against §5; committed `git diff --check` PASS. No new
compiler/build/verifier/test, push, dispatch or CI was performed. The docs-only
HEAD itself has not run CI. No new B1/B2 or independent proof credit is claimed.

Coordinator reports earlier full uninit Quick on 86428e9313: kani 24/0,
expected 210 ok (only the three superseded old-form controls failed), ui 17/0,
script 2/0. Composition remains FAIL, separately deferred S5 debt, not an
all-PASS Quick or a blanket waiver for new lost checks/status/payload drift.
A full Quick on the final docs-only HEAD and independent full evidence binding
remain NOT_RUN/UNKNOWN.

Current test package and exact identities are in controls-v2/INPUTS.json;
original top-level preparation patches/manifests refer to superseded controls.
Research, including this updated RESULT, remains uncommitted under
kani3300/c2-s3 in g0. Existing CI reports and unrelated work were not modified.
