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
| R7 reference `ptr::swap` / G2D R0 on `u8` | SUCCESS / SUCCESS = exp. | — | 2/2 |
| G2B body replayed, assert per step | FAILED = exp. | step 4 `ptr::read` of selection; step 5 pos 0 after `ptr::copy` | 1/2 |
| G2C array `==` oracle only | FAILED = exp. | `array == oracle` | 2/2 |
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
- G2C: `[u8; 17]` `==` detected at least one failure in this context; this is not correctness of
  `==` for all lengths, payloads or PFC contexts.
- OPEN: the pin mis-models array-element read/copy through a selected pointer in a direct harness, and
  why the PFC context is spared is unknown, so an array-model PFC PASS is a model run of that harness,
  not yet evidence of faithful modelling there. Scalars: only `u8` re-checked (G2D); u64, Cell<i32>
  and DropValue not re-tested — no evidence either way. Array real-body safety rows (dispatch
  bytes16/17/85) are a value-independent question, not assessed.
- Follow-up run as CASE5-2 (below).
Artifacts: `casefive/`, `casefivetwo/` (packets, gates, requests, per-build files, budgets); bounded
summaries only.
## CASE5-2 (`TASK-CASEFIVETWO.md`): array-model PFC trust — model-trust OPEN for all three
Library `d558b986c6` (tree `50c243e332`, only casefive.rs), packet `278c0d39d6` (`casefivetwo/`). Build
`fa0039da-c781-49a0-9abd-fb133b7fe40d` (`casefivetwo-g1-20261101`, head `278c0d39d6`): 8/8 compiled
and ran; build status FAILURE = gate false (3 TIMEOUT). Own $0.2565 (reserve $0.729 released);
check-tooling vs `30f77e8599` ok; cbmc peak 7.20 GiB (P17), no OOM. Project $72.1545/$88.96.
| Row | Expect | Status | Failed checks | Covers |
|---|---|---|---|---|
| A1 plain `swap_profile::<KeyB17>`, PFC fixture | SUCCESS | SUCCESS 15.6 s | — | 7/7 |
| A2 raw `swap_if_less(.., &mut KeyB17::CMP)`, same fixture | SUCCESS | SUCCESS 15.9 s | — | 7/7 |
| P17 / P16 PFC, swap twin with byte checks in target | SUCCESS | TIMEOUT (3 min) / TIMEOUT | — | — |
| S4 PFC, sort4 twin with byte checks in target | SUCCESS | TIMEOUT (3 min) | — | — |
| C1 wrong body (old b into a and b), swap contract | FAILED | FAILED = exp., 12.6 s | transfer ensures only (`:602`) | 4/5, 1 unreachable |
| D1 `[u8; 1]` read through `select_unpredictable` | FAILED | FAILED = exp., 0.28 s | `D1: read through the selection` | 2/2 |
| D2 D1 on `u8` | SUCCESS | SUCCESS | — | 2/2 |
A1/A2: `eq_ok == bytes_ok` and byte transfer held on all paths, both orders and both branches covered.
C1: 4 covers in source: two index orders and the witness (equal key, byte 1 differs), all
unconditional in the harness before the call, plus the body's return. Kani counted 5, 1 *unreachable*
(not unsatisfiable). From the counts, the extra one is a copy in a contract closure that check mode
does not execute. Terse output does not name it.
**Verdicts** (task criterion; local consistency would still not prove general faithful modelling):
- KeyB17: model-trust OPEN. A1, A2, C1 fit, and the contract check catches a payload corruption with
  equal keys. P17 (in-target byte checks) timed out, so the criterion is not met.
- KeyB16: OPEN (P16 TIMEOUT; no matched plain baseline was run; C1 is on KeyB17).
- Sort4ReadB16: OPEN (S4 TIMEOUT; C1 does not exercise the sort4 contract).
- NOT TRUSTED does not apply: no in-target check failed, and C1 is not SUCCESS.
**Trigger narrowed.** Same call and same fn-pointer comparator type: R3 fails (`[x, y]`, fixed (0, 1)),
A2 passes (`from_fn`, `reverse`; also another comparator symbol, `pre`, unwind 180). The divergence
depends on the fixture, not on contract instrumentation. Construction vs symbolic positions is not
separated. My hypothesis (symbolic positions) matched every prediction but is unproven.
**Minimal reproducer (run, D1):** `x, y: [u8; 1] = any`, `v = [x, y]`, `c: bool = any`,
`base = v.as_mut_ptr()`, `s = hint::select_unpredictable(c, base, base.add(1))`,
`kani::assert(ptr::read(s)[0] == if c { x[0] } else { y[0] })` → FAILED, covers `c`/`!c` with
`x[0] != y[0]` both satisfied. The same on `u8` (D2) → SUCCESS. Pin `9461e07af7`, nightly-2026-10-12.
Which branch fails is not printed. No external publication.
**Part 1:** keep `swap_contract_bytes16_n2`, `swap_contract_bytes17_n2`, `sort4_contract_bytes16_n4`
in ordinary with the caveat "model-trust OPEN (CASE5-2)". No row shows them wrong: the divergence
needs the direct constant-position form, and the plain PFC-fixture baseline passes for KeyB17.
Do not cite them as evidence of faithful modelling. Closing needs a cheaper in-target check (the
twins exceed 3 min / 7 GiB; cause not analysed) or a newer pin: coordinator/owner decision.
## A1 ARRAYFACTOR — PRE-BUILD REVIEW, NOT_RUN (await coordinator GO)
Task `TASK-ARRAYFACTOR.md`, library `56387d7234` (tree `894ee6d862`); packet `arrayfactor/PREBUILD.md`.
One planned diagnostic `arrayfactor-a1-20261101`, 8 rows, reserve $0.729 <= $0.75; no submitted UUID.
Own spent $0, reserved $0. Pin `9461e07af7`, nightly-2026-10-12; ordinary 197 unchanged.
All entries below describe A1 only; earlier CASE5-2 D1/D2 evidence remains separate.
| Row | Status | Failed checks | Covers |
|---|---|---|---|
| F0 existing D1 | NOT_RUN | UNKNOWN | UNKNOWN |
| F1 existing D2, u8 | NOT_RUN | UNKNOWN | UNKNOWN |
| F2 if selection | NOT_RUN | UNKNOWN | UNKNOWN |
| F3 dereference copy | NOT_RUN | UNKNOWN | UNKNOWN |
| F4 from_fn construction | NOT_RUN | UNKNOWN | UNKNOWN |
| F5 symbolic indices | NOT_RUN | UNKNOWN | UNKNOWN |
| F6 address/value oracles | NOT_RUN | UNKNOWN | UNKNOWN |
| F7 concrete [1]/[2], branch checks | NOT_RUN | UNKNOWN | UNKNOWN |
Factor/branch/value-vs-address conclusions: UNKNOWN pending the authorized build.
F6 value-check silence after address failure is not PASS on cut paths; covers precede both asserts.
F7 SUCCESS would only mean this witness did not reproduce. Predictions are in PREBUILD.md.
Local exact D1/D2 fragment and pin/flags: `arrayfactor/reproducer.rs`, `arrayfactor/REPRODUCER.md`.
No local proof, trace/playback workaround, Part 1 validation, external publication or issue.
