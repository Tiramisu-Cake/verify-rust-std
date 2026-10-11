# Build af4e44a3 raw-evidence review — 2026-10-10

Read-only review of the fresh `allprooflogs/cases/integration` archive. This
review does not change the classification of the build or grant proof credit.

## Outcome

The C4 baseline is a genuine positive: exit 0, zero verifier errors, no dead
code, and the five required C4 proof helper bodies precede `sort4_stable`. All nine C4
negative controls enter `sort4_stable`, exit 1, and have one target VC at the
expected site:

| Control | Observed first VC |
| --- | --- |
| C1/C2/C3/C4 unwind false assertions | `Cannot prove false` at lines 365/398/447/482 respectively |
| Normal false post | `Cannot prove false` at line 315 |
| C4 normal/unwind missing close | Missing `comparison_debt<T>` at line 68 |
| C4 normal/unwind omit join | Missing joined `foreach<T>` at lines 317/324 respectively |

These logs support the intended target VCs, subject to the independent review
of the full assertions and posts. They do not establish selector composition.

The selector positive and cleanup-off runs both stop before any function
verification with exit 2:
`SORT4-GENERIC-GUARD: certificate mismatch: exact body count:
<DropOnPanic<T> as std::ops::Drop>::drop`. This is an admission/setup refusal,
not a selector proof failure or semantic negative. The incomplete cleanup
opt-in control correctly refuses with the exact cleanup certificate
`exact root/test opt-in pair` message.

The isolated strict-lifetime positive passes. Its three negatives fail at the
intended lifetime sites: live typed chunk at binding end; missing full
`lifetime_token(cmp_k)`; and missing reserved half-token. The raw-pointer
identity positive passes; its negative fails at the added line-3 pointee claim
with `No matching heap chunks: points_to_<T>(result, _)`.

ManuallyDrop `forget` and shared-cleanup positive fixtures pass. The
dead-precondition fixture exits 1 with exactly these four dead-code spans:
`dead_code_pre.rs(1,1-7,2)`, `(6,13-43)`, `(6,41-42)`, and `(7,2)`. The two
original `-allow_should_fail` fixtures exit 0 with no errors and complete the
target functions; verbose logs consume the exact false postcondition at line 3
and false unwind postcondition at line 14. These are retained-fix success
controls, not negative diagnostic runs.

## Selector environment correction

The phase `selector_env()` at tested d90a1a8e added every `BASE_GATES` root. The actual
nine-body admission explicitly rejects `SORT4_A1_LINK_REPO_ROOT` when
`SORT4_A1_NINE_REPO_ROOT` is active; the generic guard and guard-template
opt-ins additionally ask for a different exact `DropOnPanic::drop` body
certificate. They are unrelated to this selector unit and cause the observed
generic-guard refusal. Keep the `stage()` sanitizer list intact, but stop
setting these three roots for selector proofs:

- `SORT4_GUARD_REPO_ROOT`
- `SORT4_GUARD_TEMPLATE_REPO_ROOT`
- `SORT4_A1_LINK_REPO_ROOT`

Retain the required `SORT4_MAYBEUNINIT_REPO_ROOT`,
`SORT4_SELECT_INTRINSIC_REPO_ROOT`, and `SORT4_POINTER_DROP_REPO_ROOT`, along
with the owner/A1-nine/nested-H2/forget and R2/R3/FRAME/cleanup parent opt-ins.
The historical FRAME runner's parent set does not add the three unrelated
roots, and the A1-nine gate itself requires the A1-link root to be absent.

## Blockers and gate corrections

Composition did not run because selector admission failed. Therefore there is
no same-tool proof of nine imported selector bodies before the C4 call, no
wrong-selected-original/frame/thread-resource composition control, and no
composition AST-location audit. Source/contract/type/Move/edge/reachable-unwind
admission mutants and outer-type-escape control remain unrun. The reachable
cleanup refusal remains a static exact-MIR/callee guard without its targeted
mutation regression.

For follow-up evidence gates, the four observed dead-code spans must be the
expected `dead_code_pre` oracle; an exact-one-span check is incorrect. For the
two original MDnew `-allow_should_fail` fixtures, gate on exit 0, no verifier
errors/dead code, target header, `0 errors found`, and the exact verbose
consumption at lines 3/14 plus full target return/leak completion. Do not
require an `error:` line from these original files; a separate diagnostic
derivative is needed to establish an expected negative VC.

The run remains an incomplete integration diagnostic. No new build was
submitted and no toolchain was run locally.
