# WRAP-N2 — G1 COMPILE_ERROR; G2 PRE-BUILD REVIEW

Worktree `/root/verify-rust-std-kani-wraptwo`, branch experiment/kani-k1-wraptwo-20261031.
Base6f3a262961; Kani9461e07af7/nightly-2026-10-12 and cap88.96 unchanged.
G1 built head9f3da88a0b/library20c91cb296; UUID7d5d04ec-f1da-493d-8be2-7ce36de3624b.
G2 source `811c78777dc6d324444111bb1104d2166aef727c`, library `47a9f618077d539860f6c7f2ce92d5a059e45c57` (NOT_RUN).

| PFC | Real selected implementation | Clauses | G1 |
|---|---|---|---|
| stable_cell_n2 | Stable Cell default fallback insertion | fixed N2, canonical F, sorted >>1, scalar old full-value count, input frame | NOT_RUN |
| unstable_byte_n2 | Unstable u8 → Freeze/Copy network; N2 insertion | same, no sort9/sort13 | NOT_RUN |
| freeze_noncopy_n2 | local NonCopyU8 default Freeze general | same, real singleton copies/merge to input | NOT_RUN |

Independent arbitrary u8 probe shared pre/post by value; models u8/Cell.get()/inner u8.
PFC backing4 active[1..3], sentinel prefix/suffix. Stable scratch backing2 len0..2, initialized
slot0 checked unchanged; uninit slot1 never read. No stubs/shared statics/F calls in specs.

| G1 row | Expect | Status / covers / VT / CBMC RSS |
|---|---|---|
| 1 stable_cell_n2 | SUCCESS | NOT_RUN / NOT_RUN / NOT_RUN / NOT_RUN |
| 2 unstable_byte_n2 | SUCCESS | NOT_RUN / NOT_RUN / NOT_RUN / NOT_RUN |
| 3 freeze_noncopy_n2 | SUCCESS | NOT_RUN / NOT_RUN / NOT_RUN / NOT_RUN |
| 4 rejects_always_true | FAILED at canonical guard | NOT_RUN / NOT_RUN / NOT_RUN / NOT_RUN |
| 5 rejects_payload_corruption | FAILED at full-value checker | NOT_RUN / NOT_RUN / NOT_RUN / NOT_RUN |

G1 failed at compilation: E0502 at built wrap.rs:84/103/118 on old(count(v,probe)), conflicting
immutable/mutable captures around &mut-slice wrappers. Compile wall44.88s, run max1326476KiB,
sampled kani-compiler1324600KiB; no solver/proof outcome. Head/pin/request identities match;
check-tooling vs30f77e8599 PASS. Own G1 cost$0.108, live reserve$0; builds1/2.

G2 delta: unsafe raw span exactly2, geometry/init/writable requires, explicit Stable scratch
disjointness retains exclusivity. Construct &mut pair after guard; modifies exact pair;
scalar old(pair_count) adapters call original pure checker. Same5 domains/rows/controls/covers,
unwind16 and real entries retained. Compile/fix acceptance NOT_RUN; no proof credit transfers.
G2 request wraptwo-g2-retry-20261031; controls true/jobs1/uninit off/10min×5, reserve$1.08.
Own actual+reserve$1.188≤$2; project used$70.0215/reserved0/cap$88.96 (refresh before dispatch).
G2 is final build; subsequent failure means PARTIAL. Native ordinary inventory NOT_RUN:
cfg-off library projection byte-identical; controls:false cannot check wrappers. No inventory slot.
Static32 checks, request validation, rustfmt and diff --check PASS; G2 proofs/covers remain NOT_RUN.
Ordinary F03 consumers remain StageA OPEN; no literal trait contract or integrated PASS.
N7/N8 needs new real-body proofs/resources and nontrivial general halves/merge/insertion.
Three concrete paths do not cover all implementations; no threshold/uninit/padding theorem.
Artifacts: wraptwo/g1.* bounded evidence, G2-PREBUILD.md, exact requests, static-check-g2.json.
Stopped at new PRE-BUILD REVIEW; G1 GO does not authorize G2. Await explicit coordinator GO.
