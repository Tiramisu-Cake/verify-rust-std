# S1-07 accept-v3

READY for W14 review. Admission root: **PENDING**. Computed qualification:
**14/35 rows**, **0/4 N0..3 unions**.
This is bounded source-reported Profiles v4 assurance, trusting the pinned stock compiler.
Independent compiler/MIR, B1, B2 and general sorting proof credit: **NONE**.
W14 component/composer review: **PENDING**; CI GO: **false**.

Composition consumes only these committed S1-07 inputs:

| Input | Commit | Receipt SHA-256 |
| --- | --- | --- |
| accept | `b84003a4fdb2416d0742b21a5151b0d32d047d35` | `d9e7d7a7c7a19a2a00de494538bc385490a5e557f86e9f6c5a2bf959b74fe816` |
| accept-pfc | `013f288ca5111c0587e087567d2ec4182856be1d` | `bc7d87074c655f250563274eae072cfa2482a2514dc71fafe5ffd893a7f77479` |
| accept-u | `16e36c4a2c244bb23ae71c80e5aa6db5f95e5338` | `fb422b5a641892c161ddcc0e82e654dd083ac495bfe2777c813250818db4965d` |

`accept-v2/` is excluded from admission. Its five files are rehashed only because the immutable U manifest
retains their integrity snapshots; no accept-v2 verdict is parsed or passed to the composer.
No S1-08 labels or ROLE-MAP are inputs. Historical directories remain immutable.
`INPUTS.json` pins 152 committed files, including the replay implementations and their dependencies.
Replay verifies working bytes against both exact hashes and git objects, runs all three complete upstream replays
without write flags in isolated Python subprocesses, rechecks input identities, then composes and compares ACCEPT.json byte for byte.
Pinned source/control worktrees supply only git objects at fixed commits; their working changes are never evidence.
The original receipt rehashes retained compact payload bytes without extracting archives or reading raw logs.

| Computed gate/evidence | Historical | accept-v3 |
| --- | ---: | ---: |
| Qualified rows | 1 | 14 |
| Unknown U records | 187 | 0 |
| Rows with U gate | 31 | 0 |
| Rows with effective PFC gate | 22 | 0 |
| Rows with companion qualification gate | 8 | 0 |
| Rows with required-success gate | 21 | 21 |

All **111** unresolved success-message roles remain PENDING, on **21** rows; all original **16** exact
success bindings and **113** required SAT covers are unchanged. SOURCE SUCCESS alone never qualifies a row.
All 226 previously allowed U checks and 2 negative-return covers retain their exact original records.
The 187 consumed U checks remain UNREACHABLE: only applicability changes under their pinned local safety arguments.
All 22 PFC binding gates close only under source-reported Profiles v4, without independent compiler-origin credit.
Requires remain assumed by PFC; ensures asserted; modifies enforced by the sole contract.

All 9,986 reconciled properties, 14 inventories, 35 harnesses, 322 native metadata files, source/binary snapshots,
18 location-only exceptions over 2 IDs, 76 exact unsupported links and 1,276 successful MIR-unreachable guards
are retained. All 8 predeclared sole-failure negative oracles retain expected FAILURE; they are not source SUCCESS.
Companion qualification is the least fixed point of actual local gates and exact same-run/pin edges:
missing/foreign/unqualified companions and cycles stay PENDING. Group verdicts do not substitute for row qualification.
All unions require every exact member qualified, N0..3, original success/cover requirements, pins and the unchanged
fixed-fixture domain. No partial-union or general-threshold acceptance.

Each row below links its change to `rows[].component_consumption` (U record pointers/hashes and PFC edge pointers/hashes)
and `rows[].transition.companion_edge`. All record pointers are relative to the exact component receipts above.

| Row | Old → new | Removed gates / consumed records |
| --- | --- | --- |
| activation-default | PENDING → QUALIFIED | qualified stable_default_activation-legal; PFC exact chain; U 15/15 |
| activation-override | PENDING → QUALIFIED | qualified stable_freeze_activation-legal; PFC exact chain; U 16/16 |
| stable_default_cell | PENDING → PENDING | PFC exact chain; U 4/4 |
| unstable_default_cell | PENDING → PENDING | PFC exact chain; U 4/4 |
| freeze_copy_u8_n0 | PENDING → PENDING | PFC exact chain; U 6/6 |
| freeze_copy_u8_n1 | PENDING → PENDING | PFC exact chain; U 6/6 |
| freeze_copy_u8_n2 | PENDING → PENDING | PFC exact chain; U 6/6 |
| freeze_copy_u8_n3 | PENDING → PENDING | PFC exact chain; U 6/6 |
| freeze_default_noncopy_n0 | PENDING → PENDING | PFC exact chain; U 6/6 |
| freeze_default_noncopy_n1 | PENDING → PENDING | PFC exact chain; U 6/6 |
| freeze_default_noncopy_n2 | PENDING → PENDING | PFC exact chain; U 5/5 |
| freeze_default_noncopy_n3 | PENDING → PENDING | PFC exact chain; U 5/5 |
| inactive_pairs_read_free | PENDING → QUALIFIED | U 12/12 |
| activation_descending_rejected | PENDING → QUALIFIED | qualified inactive_pairs_read_free |
| activation_effectful_rejected | PENDING → QUALIFIED | qualified inactive_pairs_read_free |
| activation_unsupported_type_rejected | PENDING → QUALIFIED | qualified inactive_pairs_read_free |
| snapshot_guards_companion | PENDING → QUALIFIED | U 2/2 |
| invalid_snapshot_rejected | PENDING → QUALIFIED | qualified snapshot_guards_companion; U 11/11 |
| ordinary-bridge | QUALIFIED → QUALIFIED | unchanged |
| stable_default_activation-legal | PENDING → QUALIFIED | PFC exact chain; U 4/4 |
| stable_freeze_activation-legal | PENDING → QUALIFIED | PFC exact chain; U 5/5 |
| corruption_companion | PENDING → QUALIFIED | U 1/1 |
| order_corruption_rejected | PENDING → QUALIFIED | qualified corruption_companion; U 8/8 |
| count_corruption_rejected | PENDING → QUALIFIED | qualified corruption_companion; U 1/1 |
| model_u8_n0_3 | PENDING → PENDING | U 4/4 |
| model_cell_n0_3 | PENDING → PENDING | U 4/4 |
| model_noncopy_n0_3 | PENDING → PENDING | U 4/4 |
| stable_freeze_u8_n0 | PENDING → PENDING | PFC exact chain; U 6/6 |
| stable_freeze_u8_n1 | PENDING → PENDING | PFC exact chain; U 6/6 |
| stable_freeze_u8_n2 | PENDING → PENDING | PFC exact chain; U 5/5 |
| stable_freeze_u8_n3 | PENDING → PENDING | PFC exact chain; U 5/5 |
| unstable_freeze_u8_n0 | PENDING → PENDING | PFC exact chain; U 6/6 |
| unstable_freeze_u8_n1 | PENDING → PENDING | PFC exact chain; U 6/6 |
| unstable_freeze_u8_n2 | PENDING → PENDING | PFC exact chain; U 6/6 |
| unstable_freeze_u8_n3 | PENDING → PENDING | PFC exact chain; U 6/6 |

Reproduce locally from this directory:

```sh
python3 -B replay.py
python3 -B test_replay.py
```

Default replay is read-only. Explicit `python3 -B replay.py --write` writes only this directory's ACCEPT.json.
See VALIDATION.json for the executed upstream suites, composer mutation coverage, hashes and read-only check.
Only accept-v3 is committed; no CI/push/publication/ledger or local compiler/verifier invocation.
