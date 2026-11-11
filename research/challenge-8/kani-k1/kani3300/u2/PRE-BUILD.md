# KANI3300 U2 PRE-BUILD

PREPARED; Cloud NOT_RUN. Exact published candidate is identified by the final PRE-BUILD REVIEW marker.
Task: `research/challenge-8/kani-k1/TASK-KANI3300-U2.md`; one Codex stage, research only.
Worktree `/root/verify-rust-std-kani3300-u2`, branch `experiment/kani-k1-kani3300u2-20261111`.
Slug `kani3300`, stage `kani3300-u2`, stable owner `k1-merge`; main 240 + closeout 30 minutes after GO.
No dispatch, watcher, new proof window or phase registration has been performed during preparation.

## Identities and budget

- Task base `97d947b91f628c953c57b9320f44260349aef9f3`, U0 result base `1f2cde2e9d`.
- Library commit `7ed74cec8287dfb3380637a88f5ec5ccfa5bba3c`; only `verify/uninit_probe.rs` changes in library.
- Tooling base `c98d7cee0d509b1633ab61c9a1ae989e286c8e2a`; all protected lane paths equal this base.
- Kani pin `f046b70644e113be0df9c22c2e6ea44a65a57566`, toolchain `nightly-2026-10-23`.
- `kani_patch.path`: `research/challenge-8/kani-k1/kani3300/u2/kani-uninit.patch`.
- Patch SHA-256 `306851ac5dd4f28a11778dfc49e878a5bb62fd7c35a2ad7ad0419053b9504467`; bytes equal the pinned U1 artifact.
- Expected applied tree `b9c36ac5ed550e39d26e1d1d77000052e62a9bb4`, source-reported by U1 RESULT; U2 binding NOT_RUN.
- Request `kani3300-u2-uninit-20261111-01`, SHA-256 `d025202d57d3c271f125ca9ae8dda40b677d2bb591cad6b43307c5222f67bcb3`.
- Active request and this directory's `RUN-REQUEST.json` are byte-identical. Diagnostic, standard4/jobs1,
  controls on, inventory off, uninit checks on, `--harness-timeout 3m`; generated arguments in `kani.args`.
- Reserve `(9 × 3 + 30) × $0.0135 = $0.7695` within U2 cap $0.80. Cloud spend so far $0; no reservation submitted.
- `budget-prebuild.txt`: project used $112.9515, reserved $0, cap $118.96; with U2 $113.7210.
  Snapshot only; dispatch rechecks the ledger. The coordinator owns the separate nightly project cap $6.40.

## Rows and controls

All harness names below have prefix `slice::sort::shared::smallsort::verify::uninit_probe::`.
The first eight request entries and all eight U0 harnesses/helpers are unchanged, byte for byte.
U4/U7 retain request `expect=SUCCESS`: unsupported is an open limitation and must keep the diagnostic gate false.
The prediction column is an observation to classify after GO, never an established result.

| Row | Harness | Request | Predicted observation / U0 comparison |
|---|---|---|---|
| U1 | `pincheck_calibration_uninit_read_u8` | FAILED + uninit substring | uninit read; U0 incompatible-layout unsupported |
| U2 | `pincheck_calibration_init_read_u8` | SUCCESS | initialized read succeeds; U0 incompatible-layout unsupported |
| U3 | `raw_uninit_read_sensitivity` | FAILED + uninit substring | uninit read; U0 raw-pointer/union unsupported |
| U4 | `swap_contract_four_positions_u8` | SUCCESS | same fn-pointer unsupported as U0 |
| U5 | `sorted_permutation_insert_tail_u8_n2` | SUCCESS | same SUCCESS as U0 |
| U6 | `permutation_merge_u8_n4` | SUCCESS | SUCCESS; U0 raw-pointer/union unsupported |
| U7 | `swap_contract_four_positions_u8_function_item` | SUCCESS | planner predicts intrinsic select_unpredictable / Unimplemented; U0 union unsupported |
| U8 | `small_sort_general_with_scratch_u8_n4` | SUCCESS | SUCCESS; U0 array-of-MaybeUninit unsupported |
| U9 | `small_sort_general_scratch_unwritten_slot_u8_n4` | FAILED + uninit substring | one uninit failure on the second scratch read; new row |

U5/U6/U8/U9 keep unwind 17 and the same explicit order-violation panic stub. Other unwind settings are unchanged.
U9 uses u8/N4, 20 uninitialized scratch slots and the function item `strict_less`, with the real general scratch call.
For len=4, `smallsort.rs:260–264` copies to slots 0 and 2; `:267–277` extends both halves to length 2.
Insertion stays in each half, and the final merge reads scratch[0..4] and writes v. Slot 3 is initialized;
slot 4 is never written on this route. Neither core code nor requires/guarantees changed.
The first observable `assume_init_read` is at `verify/uninit_probe.rs:198` (scratch[3]); the second is at `:204` (scratch[4]).
Each read feeds zero/nonzero covers. U9 also covers normal return and reaching the second read: six covers total.
These observations retain both reads. Prefix covers must establish the real call returns and the second read is reachable;
suffix covers alone never prove initialization. If bounded aggregate covers are incomplete, prefix reachability is UNCONFIRMED.

## Required evidence after exact-packet GO

1. Dispatch only the exact reviewed/published SHA through `k1g.sh dispatch experiment/kani-k1-kani3300u2-20261111`.
   Run `k1g.sh watch BUILD` and end the turn. No repair without actual spend + fresh reserve <= $0.80 and new GO.
2. Read bounded `k1g.sh status BUILD`, `summary BUILD`, `summary BUILD 0 9`, `check-tooling BUILD c98d7cee0d509b1633ab61c9a1ae989e286c8e2a`, `budget BUILD`.
   Require COMPLETE and exact head/request/pin/patch/applied-tree bindings; check-tooling PASS; actual `-Z uninit-checks` argv.
   Generated args are static intent, not evidence of actual instrumentation. Missing actual argv is a binding limitation.
3. Manually check all nine statuses, failed/total counts, all verbatim located failures, truncation markers and cover totals.
   U1/U3/U9 require exactly one uninit failure each, with `expect_check = Reading from an uninitialized`.
   U9 additionally requires the second read's location `verify/uninit_probe.rs:204` and no failure at the written read `:198`.
   The unchanged diagnostic gate only matches a located description substring; it does not enforce failure count,
   exact location or covers. Do not equate gate success with this task's manual acceptance.
   A shared callee location without a U9 call-site binding leaves the requested location acceptance UNCONFIRMED.
4. Require U2/U5/U6/U8 SUCCESS and reachable expected covers. U1/U3/U9 SUCCESS, absent instrumentation,
   or an unreachable negative read is a blocker. Classify each new unsupported using bounded evidence.
   For U4 preserve verbatim the fn-pointer limitation from the actual result; for U7 record the actual operation/location,
   not the planner forecast. Gate false from the documented unsupported rows is compatible with COMPLETE research evidence.
5. Write `RESULT-KANI3300-U2.md` here, <=35 lines: identities, nine rows with status/failed-total/verbatim failures and
   locations/classes, U0 comparison, scratch result boundaries, spend, and next core package u64/N4 via Stable trait item,
   then N8/sort4. Preserve normal-return/panic-stub, u8/N4 and general-route bounds; no general theorem or independent credit.

Static receipts: request validation PASS; 15 checks PASS in `static-check.json`; specified rustfmt wrapper PASS/zero diff;
`git diff --check` PASS. No local compiler, Kani, CBMC, extraction or Kani-tree preparation was run.
U1 patch is reused unchanged as instructed, including its source-reported U1 native results; those are not U2 proof.
Independent Codex review covers this integration candidate; coordinator exact-packet GO remains mandatory.
