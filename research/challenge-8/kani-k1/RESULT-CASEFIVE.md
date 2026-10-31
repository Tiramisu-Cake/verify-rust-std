# RESULT CASE5 — COMPLETE: Kani model divergence, not library or harness; trigger OPEN

Task `TASK-CASEFIVE.md`. Base `f000cb484e` (library tree `73e902bec8`); pin Kani `9461e07af7`,
nightly-2026-10-12; cap 88.96 inherited; tools/flags untouched (check-tooling vs `30f77e8599` ok ×2).
Opt-in `verify/merge/casefive.rs` + cfg-gated `mod casefive;`; runtime and ordinary 197 untouched
(`casefive/gate*.txt`). Library `18bb799795` (G1), `849f1e6bd8` (G2, G1 rows unchanged).
| Build | UUID / request / head | Result | Own cost |
|---|---|---|---|
| G1 | `8c52a7a8-…-86d4f1bf5d26` / `casefive-g1-20261101` / `aa4469674a` | 8/8 ran; 4 rows ≠ prediction | $0.1215 |
| G2 | `543c7d89-…-f7850ccdadd3` / `casefive-g2-20261101` / `f64dcb1edd` | 3/3 = prediction | $0.1215 |
Total $0.243 of $1.26; project $71.7225 / $88.96, reserved 0. Packets `casefive/PREBUILD*.md`.
## Rows (M = 17 unless noted; failed checks by message; covers satisfied/total)

| Row | Status | Failed checks | Covers |
|---|---|---|---|
| R0 closure (case5 repeat) | FAILED | pos 0, pos 1 | 1/2 |
| R1 `assume(taken)` | FAILED | pos 1 only | 1/2: reached, no path passes |
| R2 `assume(!taken)` | FAILED (exp. SUCCESS) | pos 0 only | 2/2: some path passes |
| R3 fn pointer | FAILED (exp. SUCCESS) | pos 0, pos 1 | 1/2 |
| R4 closure M = 1 | FAILED | pos 0, pos 1 | 1/2 |
| R5 one assert per path | FAILED | `[taken]` and `[not taken]` (exp. `[taken]`) | 2/2 |
| R6 snapshot `pre` | FAILED | pos 0, pos 1 | 1/2 |
| R7 reference `ptr::swap` | SUCCESS | — | 2/2 |
| G2B body replayed step by step | FAILED | step 4 `ptr::read` of the selection, step 5 pos 0 after `ptr::copy` | 1/2 |
| G2C array `==` oracle only | FAILED = exp. | `array == oracle` | 2/2 |
| G2D R0 on `u8` | SUCCESS | — | 2/2 |
## Which branch, and where

**Both** branches diverge. My G1 prediction (taken only) was wrong. R0's lost cover is the assert-assume cascade (R5: 2/2 covers, both labels fail).
Taken: position 0 matches, position 1 never does. Not taken: position 0 wrong unless x == y.
Every row fits the simplest outcome "both slots hold the old `v[1]`", (y, y). This is inferred, not printed.
G2B: decision (`should_swap == taken`) and both `select_unpredictable` pointer values hold on every path. The first wrong
value is what `ptr::read` returns through the selected pointer (step 4), then position 0 after `ptr::copy(v_a_swap, v_a, 1)`
(step 5; on not-taken paths src == dst). Not closure-specific (R3), not size (R4 M = 1), not snapshot/MIR copy
(R6). Element type matters: `u8` passes (G2D), `[u8; 1]` fails (R4).
## Class: Kani model (pinned pipeline). Component and trigger UNKNOWN

- Not the harness: R7 and G2D pass with the same fixture and oracle. G2B checks bytes without array `==`. G2C shows `==` sees it.
- Not the library: the source moves `*v_b_swap` = old `v[0]` when taken and leaves `v[0]` alone otherwise. The program
  has defined behaviour (valid distinct initialized slots), and (y, y) is not a possible execution of it.
  The model also contradicts itself: reads through `&*v_a` give old `v[0]` (decision correct), but `ptr::read` through a
  pointer equal to it (step 3) does not.
- Which pipeline part (kani-compiler codegen of the selected thin `*mut [u8; M]` / `MaybeUninit` union in
  the `select_unpredictable` fallback, or CBMC) is UNKNOWN without a trace. So is why `swap_contract_bytes17_n2` (same body,
  `[u8; 17]`) passed: its fixture is `array::from_fn` + `reverse` indices inside a contract harness.
- Reproducer candidate (minimal form NOT run; G2B is the run form). Two arbitrary `[u8; 1]` in `v`, `c: bool = any`,
  `s = hint::select_unpredictable(c, v.as_mut_ptr(), v.as_mut_ptr().add(1))`,
  `kani::assert(ptr::read(s)[0] == if c { x[0] } else { y[0] })`. No external publication.
## Impact on P1

- Case5 section in P1: fold into a pointer here. The anomaly is a pinned-model divergence, not a library, profile or
  oracle defect. It stays an OPEN model limitation, not closed.
- Do not return the raw case5 check to Part 1. It fails on the pin for a model reason. Part 1 keeps the profile PFC form
  (fn pointer, model `==`). R0 can stay as an opt-in known-failing diagnostic until the pin changes.
## Separately: P1 PFCs with an array model (KeyB16 / KeyB17 / Sort4ReadB16)

Affected: `swap_contract_bytes16_n2` (KeyB16), `swap_contract_bytes17_n2` (KeyB17, PASS in P1-CLEAN G1),
`sort4_contract_bytes16_n4` (Sort4ReadB16, NOT_RUN on `73e902bec8`).
- What G2C rules out: the PASS is not vacuous through a blind `[u8; M]` `==`. The same `==` fails on this divergence.
- What stays OPEN: the pin models array-element read/copy through a selected pointer wrongly in a direct harness, and the
  reason the PFC context is spared is unknown. So an array-model PFC PASS shows the model run of that harness. It does not
  yet show that real execution is modelled faithfully there. Scalar profiles: only `u8` re-checked here (G2D);
  u64, Cell<i32> and DropValue were not re-tested; this run gives no evidence on them either way.
- To close (≤ 1 diagnostic build, coordinator GO): (a) G2B step asserts inside the PFC fixture (`from_fn`, `reverse`, fn
  pointer, no contract). If the move is right there, the divergence depends on the trigger. (b) Trigger isolation: R0 with
  `from_fn` instead of `[x, y]`, and with reversed indices. (c) Negative array control in PFC context: KeyB17/KeyB16
  through a deliberately wrong move must FAIL the transfer ensures. (d) Run the minimal reproducer. (e) Re-check on a newer
  Kani pin (owner's decision). Until (a)+(c) pass, mark the 3 array-model PFCs "model-trust OPEN" in the P1 ledger.
  The array real-body safety rows (dispatch bytes16/17/85) are a value-independent question and were not assessed.
Artifacts: `casefive/` (packets, gate script/results, requests, per-build summary/status/peaks/tooling/cost/wait/
dispatch, budgets). Only bounded summaries were used, no raw logs.
