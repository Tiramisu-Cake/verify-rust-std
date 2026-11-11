# KANI3300 U4 — PRE-BUILD packet

PREPARED; U4 Cloud NOT_RUN. Research only, Runtime Codex, one stage.
Worktree `/root/verify-rust-std-kani3300-u4`, branch `experiment/kani-k1-kani3300u4-20261111`.
Task `research/challenge-8/kani-k1/TASK-KANI3300-U4.md`; slug `kani3300`, stage `kani3300-u4`, owner `k1-merge`.
No dispatch, reservation, phase registration or watcher during preparation. Stop at PRE-BUILD REVIEW.
Thread cwd is `/root`; no Build watcher has been armed. A later authorized runtime must satisfy its watcher entry rules.

## Immutable identities

- U2 base `4ecdcc5930`; task commit `7b4502fedfc5b0630561da91d01bf192e5cf04bf`.
- KT2 cherry-pick `d483dc371967cc5be6b0166eb506c2f4cb0179aa` → `af6434d23f`.
  All protected lane paths equal `3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c`.
- Entire library, including all nine harnesses in `verify/uninit_probe.rs`, equals U2 base byte for byte.
- Kani pin `f046b70644e113be0df9c22c2e6ea44a65a57566`, toolchain `nightly-2026-10-23`, unchanged.
- CMP2 full candidate `b1f0105c0390fb55081e3d186fa286d23867b585`, tree `45511935c1ce911ea6c85eee5f6850095cbf966e`.
- Production-only `kani-uninit.patch`: SHA256 `46ad585f769143200634e2c2ddf3c16e4b5f33955985791c0962ac446cf354e4`,
  100977 bytes, eight production files, no Kani tests, diffstat 576 bytes ≤4096.
- Production sections are byte-identical to CMP2 build patch SHA256
  `17db5a0db394c5c5db8f7182fb61866df656747b17e160ead4034e03a14dbc0a`, from exact research head
  `6f50f1fbc4a95ca21444ee9ac6f101034081cd43`. CMP2 Build `a13d3781-287d-4229-88d6-6b3dd1a74879`.
- Expected production-only applied tree `d356238999ab436ddc1dd7ffa845b0db214aa53e`: static Git object calculation,
  not a prepared Kani checkout or observed Cloud tree. Full/subset CMP2 trees include tests and must differ from U4 tree.
- Request `kani3300-u4-uninit-20261111-01`, SHA256 `778b2ef2a1f148dd8c8e3e7b98f3da8cf99c7b48a805ef2cde38a6c9f21cf381`.
  Root request equals this directory's snapshot. All five row entries equal their corresponding U2 entries.

## Rows and manual acceptance

All names have prefix `slice::sort::shared::smallsort::verify::uninit_probe::`.
These are requirements; every U4 runtime observation remains NOT_RUN.

| Row | Harness | Required result |
|---|---|---|
| U1 | `pincheck_calibration_uninit_read_u8` | FAILED, exactly one uninit-read failure; before-read cover reached |
| U2 | `pincheck_calibration_init_read_u8` | SUCCESS, initialized read returns written byte; covers reached |
| U6 | `permutation_merge_u8_n4` | SUCCESS; normal-return probe-count cover reached |
| U8 | `small_sort_general_with_scratch_u8_n4` | SUCCESS; sortedness, count, normal-return cover 1/1 |
| U9 | `small_sort_general_scratch_unwritten_slot_u8_n4` | exactly one uninit failure at scratch[4], none at scratch[3]; required covers reached |

U1/U9 retain `expect_check: Reading from an uninitialized`. The substring gate does not enforce failure count,
exact call site or cover reachability. Manually inspect all failures/omissions and individual cover statuses.
U9 reads scratch[3] at `uninit_probe.rs:198`, scratch[4] at `:204`. Its six covers include normal return,
both written-byte outcomes, reaching the unwritten read and both unwritten-byte outcomes. Require full cover accounting,
in particular all prefix covers and scratch[3] observations; no inference from suffix covers alone.
For N4, real core copies to slots 0 and 2 and extends each half to length 2 (`smallsort.rs:260–277`);
merge reads slots 0..4. Slot 3 is written; slot 4 is unwritten. Preserve unwind17, assertions and panic stub.
A callee failure without second-read call-site binding leaves location acceptance UNCONFIRMED.
Blockers: U9 SUCCESS, failure on scratch[3], unreachable U8/U9 covers, missing instrumentation, or new Unsupported.
Classify new Unsupported by bounded KT2 excerpt/native-field and operation/location, never as SUCCESS.

## Dispatch boundary, budget and evidence

One diagnostic build: standard4/jobs1, timeout3m per harness, controls/uninit on, inventory off.
Envelope `(5 × 3 + 30) = 45min`, planned reserve `45 × $0.0135 = $0.6075` ≤ cap$0.80.
U4 spend$0, submitted reserve$0. Dispatcher/coordinator recheck project and nightly budgets/slots at GO;
this packet makes no claim that another task's reservation is available. No repair without new GO.

Dispatch requires BOTH accepted native CMP2 PASS for the bound candidate and coordinator GO for the final full U4 SHA.
If CMP2 repairs/rebinds, regenerate production patch, equality receipts, expected tree/request, and review the delta.
Current CMP2 result is pending; its source-reported review/native status is not U4 evidence or proof credit.
After GO only: existing `k1g.sh dispatch experiment/kani-k1-kani3300u4-20261111`, then `k1g.sh watch BUILD` and end turn.
After terminal: bounded summary/rows (`summary BUILD 0 5`), native/native-field as applicable, status, budget and
`check-tooling BUILD 3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c`. Do not read raw logs/archives/credentials.
Require COMPLETE, exact head/request/pin/patch and observed applied tree, check-tooling PASS, actual `-Z uninit-checks`.
Generated `kani.args` proves intent only. If ordinary diagnostic argv/check/cover detail is absent from permitted fields,
report the binding/evidence limitation as UNKNOWN; do not use raw fallback or infer acceptance.

After that build, write `RESULT-KANI3300-U4.md` here (≤30 lines): five rows with status, failed/total, covers,
verbatim located Failed Checks/class, compare U2 (U1 uninit; U2/U6 SUCCESS; U8/U9 array-iterator blockers),
actual cost and next step. Scope: u8/N4, actual general scratch route, normal returns with panic stub;
no arbitrary types/lengths, unwind theorem, independent B1/B2 credit or resolved U3 PFC claim.

Static receipts: request validation, unchanged library/protected paths, production-section equality, Git-derived tree,
non-patch committed `git diff --check`, and 117 Python unit tests PASS.
The full nested-patch diff check flags 37 context blank-line markers; patch bytes remain unchanged. No local cargo/rustc/Kani/CBMC or Kani checkout preparation.
Independent Luna HIGH integration review PASS: `INDEPENDENT-REVIEW.md`, semantic candidate
`47f33dda784613382c5bf50dd6c90851251ba3e7`; no blocking findings. No review receipt authorizes dispatch.
