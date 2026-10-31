# RESULT CASE5 — COMPLETE: Kani model divergence, not library or harness; trigger OPEN

Task `TASK-CASEFIVE.md`. Base `f000cb484e` (library tree `73e902bec8`); pin Kani `9461e07af7`,
nightly-2026-10-12; cap 88.96 inherited; tools/flags untouched (check-tooling vs `30f77e8599` ok ×2).
Opt-in `verify/merge/casefive.rs` + cfg-gated `mod casefive;`; runtime and ordinary 197 untouched
(`casefive/gate*.txt`). Library `18bb799795` (G1), `849f1e6bd8` (G2, G1 rows unchanged).
G1 `8c52a7a8-289e-4352-91ed-86d4f1bf5d26` (`casefive-g1-20261101`, head `aa4469674a`): 8/8 ran,
4 rows ≠ prediction, $0.1215. G2 `543c7d89-c003-40f1-b2f6-f7850ccdadd3` (`casefive-g2-20261101`,
head `f64dcb1edd`): 3/3 = prediction, $0.1215. Own $0.243 of $1.26; project $71.7225/$88.96.
## Rows (M = 17 unless noted; failed checks by message; covers satisfied/total)

| Row | Status | Failed checks | Covers |
|---|---|---|---|
| R0 closure (case5 repeat) | FAILED | pos 0, pos 1 | 1/2 |
| R1 `assume(taken)` | FAILED | pos 1 only | 1/2: reached, no path passes |
| R2 `assume(!taken)` | FAILED (exp. SUCCESS) | pos 0 only | 2/2: some path passes |
| R3 fn pointer | FAILED (exp. SUCCESS) | pos 0, pos 1 | 1/2 |
| R4 closure M = 1 / R6 snapshot `pre` | FAILED / FAILED | pos 0, pos 1 (both) | 1/2 / 1/2 |
| R5 one assert per path | FAILED | `[taken]` and `[not taken]` (exp. `[taken]` only) | 2/2 |
| R7 reference `ptr::swap` | SUCCESS | — | 2/2 |
| G2B body replayed, assert per step | FAILED = exp. | step 4 `ptr::read` of selection; step 5 pos 0 after `ptr::copy` | 1/2 |
| G2C array `==` oracle only | FAILED = exp. | `array == oracle` | 2/2 |
| G2D R0 on `u8` | SUCCESS = exp. | — | 2/2 |
## Which branch, and where

**Both** branches diverge (my G1 prediction "taken only" was wrong); R0's lost cover is the
assert-assume cascade (R5: 2/2 covers, both labels fail). Taken: pos 0 matches, pos 1 never does;
not taken: pos 0 wrong unless x == y. All rows fit "both slots hold old `v[1]`" (y, y) — inferred,
not printed. G2B: decision (`should_swap == taken`) and both `select_unpredictable` pointer values
hold on every path; the first wrong value is `ptr::read` through the selected pointer (step 4), then
pos 0 after `ptr::copy(v_a_swap, v_a, 1)` (step 5; src == dst when not taken). Not closure (R3),
not size (R4), not snapshot/MIR copy (R6); element type matters: `u8` passes (G2D), `[u8; 1]` fails.
## Class: Kani model (pinned pipeline); component and trigger UNKNOWN

- Not harness: R7 and G2D pass on the same fixture/oracle; G2B compares bytes without array `==`.
- Not library: the source moves old `v[0]` into `v[1]` when taken and leaves `v[0]` otherwise; on
  valid distinct initialized slots (y, y) is no possible execution. The model contradicts itself:
  `&*v_a` reads old `v[0]` (decision right), `ptr::read` via a pointer equal to `v_a` (step 3) does not.
- Which part (kani-compiler codegen of a selected thin `*mut [u8; M]` / `MaybeUninit` union in the
  `select_unpredictable` fallback, or CBMC) is UNKNOWN without a trace; so is why
  `swap_contract_bytes17_n2` (same body, `[u8; 17]`; `array::from_fn`, `reverse`, contract) passed.
- Reproducer candidate (minimal form NOT run; G2B is the run form): `x, y: [u8; 1] = any`,
  `v = [x, y]`, `c: bool = any`, `s = hint::select_unpredictable(c, v.as_mut_ptr(), v.as_mut_ptr().add(1))`,
  `kani::assert(ptr::read(s)[0] == if c { x[0] } else { y[0] })`. No external publication.
## Impact on P1

- Fold the P1 case5 section into a pointer here: a pinned-model divergence, not a library, profile or
  oracle defect; it stays an OPEN model limitation. Do not return the raw case5 check to Part 1 (it
  fails on the pin for a model reason); Part 1 keeps the profile PFC form (fn pointer, model `==`);
  R0 may stay an opt-in known-failing diagnostic until the pin changes.
## Separately: array-model P1 PFCs (KeyB16 / KeyB17 / Sort4ReadB16)

Affected: `swap_contract_bytes16_n2` (KeyB16), `swap_contract_bytes17_n2` (KeyB17, PASS in P1-CLEAN
G1), `sort4_contract_bytes16_n4` (Sort4ReadB16, NOT_RUN on `73e902bec8`).
- Ruled out by G2C: the PASS is not vacuous via a blind `[u8; M]` `==` (the same `==` fails here).
- OPEN: the pin mis-models array-element read/copy through a selected pointer in a direct harness, and
  why the PFC context is spared is unknown, so an array-model PFC PASS is a model run of that harness,
  not yet evidence of faithful modelling there. Scalars: only `u8` re-checked (G2D); u64, Cell<i32>
  and DropValue not re-tested — no evidence either way. Array real-body safety rows (dispatch
  bytes16/17/85) are a value-independent question, not assessed.
- To close (≤ 1 diagnostic build, coordinator GO): (a) G2B step asserts inside the PFC fixture
  (`from_fn`, `reverse`, fn pointer, no contract); (b) trigger isolation: R0 with `from_fn` instead of
  `[x, y]`, and with reversed indices; (c) negative array control in PFC context: KeyB17/KeyB16 through
  a deliberately wrong move must FAIL the transfer ensures; (d) run the minimal reproducer; (e) re-check
  on a newer Kani pin (owner's decision). Until (a)+(c) pass, mark the 3 PFCs "model-trust OPEN".

Artifacts: `casefive/` (packets, gate script/results, requests, per-build summary/status/peaks/
tooling/cost/wait/dispatch, budgets). Bounded summaries only; no raw logs.
