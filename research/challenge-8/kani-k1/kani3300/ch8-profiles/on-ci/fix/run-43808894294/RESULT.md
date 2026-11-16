# PROF-ON-02 — run 43808894294 (coordinator intake, bounded receipts only)

- Source `166a406e22` (tree `460029c0d9`, on P′ `9fa2f7f977`), control tree `1352d0b759` → trigger `5710dd6758`
  (parent SEL1) on `uninit-ci/ch8-prof02-a`. Jobs: `profiles-on` 05:14–06:37Z (SEL1 `14bc57fdb9`, `-Z uninit-checks`),
  `profiles-off` 06:37–07:12Z (stock `0aac16ef62`). Both jobs conclusion failure = runner verdict
  `PENDING_INDEPENDENT_REVIEW`, credit NONE (by design).
- Artifacts: ON `ch8-prof02-on-43808894294-1` (id 14203740678), OFF `ch8-prof02-off-43808894294-1` (id 14204858070).
- Export SHA256: ON g00 `260ccaeb…a301`, g01 `e5203e85…8e8a`; OFF g00 `575999fc…d8d1`, g01 `4d0fd897…1104`.
- Compile/RSS: ON g00 218 s / 4.74 GiB, g01 48 s / 0.98 GiB; OFF g00 56 s / 2.85 GiB, g01 35 s / 0.17 GiB.
  63/63 rows OBSERVED in both lanes, no timeout/OOM.

## Kani verdicts (stdout `VERIFICATION:-` + FAILURE count; acceptance not applied)

| Lane | SUCCESSFUL, 0 failures | FAILED on own named check only | Tool-blocked |
|---|---|---|---|
| ON | 53 (incl. new `profile_merge4_contract_u8_len4`, all 8 former array_assume_init rows, both former write_any_slice consumers, `swap_safety_u8_backing4`) | 8 negatives | 2 PolymorphicIter: `freeze_noncopy_n2`; `rejects_always_true` (own assertion.4/.6 also fail) |
| OFF | 54 (incl. merge4 leaf, `freeze_noncopy_n2`) | 9 negatives (rejects_always_true: assertion.2/.4/.6) | 0 |

Workarounds A/B/C removed all 11 ON-only tool blocks of PROF-ON-01; no new failure class appeared.

OFF lane in-run export states (`SOURCE_STAGE_TARGET_MISMATCH` 33, `INCOMPLETE_CHECK_INVENTORY` 21 — SUCCESS-status
unsupported constructs: caller_location, rust_begin_unwind, pointer to unallocated memory) are the pre-accept-v2
in-runner labels, same as PROF-OFF-02; they are not Kani failures. Acceptance must be re-applied offline with accept-v4.
