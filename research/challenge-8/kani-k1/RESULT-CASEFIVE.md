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
## A1 ARRAYFACTOR — COMPLETE: symbolic indices suppress the divergence in this fixture
Task `TASK-ARRAYFACTOR.md`; library `56387d7234`, tree `894ee6d862`; published/run head `0a2764a562`.
Build `cc350da7-7c1a-4acf-abc0-6ee6eda702ad`, request `arrayfactor-a1-20261101`: 8/8 compiled/ran,
all predictions matched; build SUCCESS, gate true (Kani exit 1 is expected for these diagnostics).
Pin `9461e07af7`, nightly-2026-10-12; flags unchanged; 3 min, jobs 1, controls on, uninit off.
Own $0.1080/$0.75, reserve $0 released; project snapshot $73.3560 used + $1.9980 others reserved / $88.96.
`check-tooling` vs `30f77e8599` PASS; compilation+verification wall 69.61 s, max RSS 1664908 KiB, no OOM seen.
| Row | Status | Failed checks (literal message; only listed checks failed) | Covers |
|---|---|---|---|
| F0 unchanged D1 | FAILED | `casefive D1: read through the selection` | 2/2 |
| F1 unchanged D2, u8 | SUCCESS | — | 2/2 |
| F2 if selection | FAILED | `arrayfactor F2: read through if selection` | 2/2 |
| F3 dereference copy | FAILED | `arrayfactor F3: copy through dereference` | 2/2 |
| F4 from_fn construction | FAILED | `arrayfactor F4: read from from_fn selection` | 2/2 |
| F5 symbolic indices | SUCCESS | — | 4/4 |
| F6 address/value oracles | FAILED | `arrayfactor F6: read through the selection` | 4/5 |
| F7 concrete [1]/[2] | FAILED | `arrayfactor F7: first selected value` | 2/2 |
**Factors:** D1/D2 reproduce the array/scalar difference. In this one-factor matrix, symbolic
index order (F5) suppresses the divergence; changing select to if (F2), read to dereference (F3),
or construction to from_fn (F4) does not. Thus select_unpredictable and ptr::read are not necessary
for this symptom; this from_fn form alone does not reproduce A2's success. No general trigger theorem.
**Address/value:** F6's first (address) assert did not fail; its value assert did. With covers
before both asserts, 4/5 covers imply right-address/wrong-value and right-address/right-value
are satisfied, wrong-address unsatisfied (inferred from source/counts and address check; terse
output does not name individual covers). No value PASS is inferred on paths cut by a failed assert.
**Branch:** F7 fails only on c=true (base, expected 1); c=false (base+1, expected 2) holds for
this witness. Both branch covers are satisfied and asserts execute on disjoint paths.
**UNKNOWN:** actual wrong byte, failing-branch distribution for arbitrary x/y, and the responsible
compiler/model/backend component; symbolic indices are a local suppression, not faithful-model proof.
Ordinary 197 source membership unchanged; no new Part 1 validation or array-profile trust credit.
Artifacts: `arrayfactor/` (bounded summary/rows/status/peaks/tooling/cost/ledger); minimal exact D1/D2
code `reproducer.rs`, pin/flags `REPRODUCER.md`. One build only; no trace/raw-log workaround or issue.
