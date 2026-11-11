# KANI3300 CMP4 — clean PRE-BUILD packet

PREPARED; Cloud NOT_RUN; proof credit NONE. Runtime Codex; diagnostic only, no repair.
Task: `../../TASK-KANI3300-CMP4.md`; planner: `PLANNER-AFTER-CMP3-ANSWER.md`, points 3–6.
Worktree `/root/verify-rust-std-kani3300-cmp4`; branch `experiment/kani-k1-kani3300cmp4-20261111`.
Stage `kani3300-cmp4`; owner `k1-merge`; task baseline `2f0c922464772be8f917b17eba7c58f030b60455`.
Separate library commit `2121ff2d08d50d412c834760af925b202a1d8c01`; one appended opt-in runtime root; existing library bytes/adapters preserved.

## Exact inputs and roots

Active root request equals `clean/RUN-REQUEST.json`: `kani3300-cmp4-clean-20261111-01`.
Request SHA256 `9ab5f113371d3d360ae7592e42bee058d7c1b4a936b93a128dc7a26afc4ca6a3`. No `kani_patch` key: clean Kani f046.
Kani pin `f046b70644e113be0df9c22c2e6ea44a65a57566`; toolchain `nightly-2026-10-23`.
Protected lane/tooling paths unchanged from KT2 `3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c`.
Same std library fixture, roots, generated argv and flags are required for the later CMP2 run.

| Root suffix (prefix `slice::sort::shared::smallsort::verify::uninit_probe::`) | Requested observation |
|---|---|
| cmp3_index_range_len | zero_to(2), assert len==2, post-len cover; unchanged CMP3 step1 |
| cmp4_index_range_len_runtime | n:any_where(n<=4), zero_to(n), assert len==n, post-len cover |
| cmp3_manually_drop_unsized_len | unchanged CMP3 step4 ManuallyDrop/deref/unsize/native len positive |
| pincheck_calibration_uninit_read_u8 | unchanged U1, FAILED with Reading from an uninitialized |

Exactly four roots; kind diagnostic, uninit/controls true, inventory false; standard4/jobs1; 3m per harness.
SUCCESS expectations diagnose unexpected positive failures; they are not established runtime results.
No new pre-len raw-read/AddressOf; no real-method, visibility, production Kani or runner changes.
Existing U1 observations/covers remain intact; covers after intentional UB do not establish credit.

## Budget, boundaries and interpretation

One clean attempt and one CMP2 attempt, no retries. Each envelope 4*3+30=42min, reserve $0.5670.
Stage reserve $1.1340 <= cap $1.20; actual spend/submitted reserve $0. No reservation/dispatch during preparation.
Existing coordinator/client and project budget/slots/owner controls remain in force; preparation does not activate a phase.
Each Build requires its own exact published head/packet and coordinator GO. This packet requests clean only.
After clean evidence, activate the separately prepared CMP2 snapshot, commit/publish and request a separate exact-head GO.
`cmp2/RUN-REQUEST.json` SHA256 `e23db232f257a8977e1d90b15260de6295da02898e612c60333fbe19c97abd51` is a future snapshot, not the active dispatch request.
CMP2 patch stays `kani3300/u4/kani-uninit.patch`, SHA256 46ad585f769143200634e2c2ddf3c16e4b5f33955985791c0962ac446cf354e4.
Expected CMP2 applied tree d356238999ab436ddc1dd7ffa845b0db214aa53e is inherited static U4 binding; actual tree NOT_RUN.
Inherited U4 acceptance text is historical, not CMP4 authorization or proof credit.
Static validation/scope/identity checks PASS; wrapper rustfmt --check and git diff --check PASS.
Independent review pending before final published PRE-BUILD marker; packet check alone is not review/GO.
No local compiler/Kani/CBMC/preparation. Runner unchanged; no service tests required for this fixture-only delta.

Actual MIR assignment remains UNKNOWN. Source literal call is const-evaluable; runtime bound is nondeterministic.
A const fn call does not establish actual Rvalue::Use(Constant); source contrast does not prove MIR contrast or cause.
No new compiler/MIR tooling here. Use existing bounded evidence if available; otherwise retain UNKNOWN.
Same located clean failure establishes pre-existing behavior; clean SUCCESS/CMP2 FAIL establishes fixture regression;
Unsupported/missing/binding-incompatible evidence leaves comparison unresolved. Never infer causality from spans alone.
After GO: existing `k1g.sh dispatch` on the exact published branch, then `k1g.sh watch BUILD` and end turn.
Task explicitly specifies k1g watch; no smallsort-session watch launch here. Thread cwd is /root; assigned worktree is above.
Terminal evidence: Brief plus bounded k1g summary/native/native-field/rows; check tooling/actual argv/pin/tree bindings.
No raw/full logs, archives, credentials or bypass. Keep exact/complete/omitted metadata and all failures.
Final RESULT <=25 lines: four rows x clean/CMP2, status, failed/total, covers, located Failed Checks, comparison,
const/runtime uncertainty, spend and justified next step. No fix in CMP4; any constant transfer repair is a later task.
Stop now at PRE-BUILD REVIEW <full published SHA> until exact-packet coordinator GO; after two diagnostics stop.
