# INTEG2 — GO received, approved dispatch in progress

Work only in `/root/verify-rust-std-kani-integtwo`, branch `experiment/kani-k1-integtwo-20261031`.
Coordinator Claude Code explicitly approved review source e0ff82577dc58950621dadc9c141d88a5821987f.
GO is recorded in go.json; task is ../TASK-INTEG2.md.
Library commit20aa864ad04e8d81b46d41024b75dc7aa1103dcf;
frozen tree c522edd42ae67c385e1ee42a1c4d1bffb611c90b for all three builds.
No semantic library changes without committed delta review/GO.

Actual per-stage request/source SHA/UUID/status and own accounting: builds.json.
Submit G1→G2→G3 in order, fresh global budget + selected own UUID budget before every dispatch.
Publish each distinct request commit, then run preflight.py STAGE && k1g.sh dispatch BRANCH.
Record each successful dispatch with record_submission.py STAGE.
G1 ordinary inventory197 work30+setup30/USD0.810; G2 controls inventory479 work60+setup30/USD1.215.
G3 exactly three approved controls, jobs1/controls:true/timeout10min, work30+setup30/USD0.810.
Max3 builds/USD2.90. G3 requires actual own spent+reserved+0.810<=2.90.
Original T0 UTC11:58, deadline16:58 UTC/19:58 MSK, closing reserve30min; never reset.
Full next envelope+closing must fit; otherwise NOT_RUN/PARTIAL and exact request handed over.
Only k1-standard4; CAP_USD73.96/pin/toolchain/flags/lane unchanged; no fourth build.
After submissions register k1g.sh watch for each build, then end turn. Do not poll builds while waiting.

Source forecast ordinary197/cfg-on479/static P2=343; exact manifests in scope/.
Source audit, helper-use forecast, scope check, static P2 apply/name check and prescribed rustfmt PASS.
All native inventory/proof/compiler warnings on candidate remain unreviewed until terminal results.
Controls are not accepted yet; intended frozen-source coordinates/classes are in controls-plan.json.
Use only approved K-1 summary/inventory/peaks/log-grep/log-lines/check-tooling/budget readers.
Review exact inventory sets and complete bounded pages/bindings; targeted compiler warnings.
G3: exactly one intended count/prefix/suffix FAILED per harness, all covers, no other failures/OOB.
Check actual location/class against frozen source manually; matcher mismatch stays gate=false.
No local Rust/cargo/Kani/CBMC, no Actions/CircleCI/submission branches.
Native P2/macOS/positive integration proofs/full CI remain NOT_RUN; coordinator owns later CI.
Cfg-only fallback patches in cfg-fallbacks.json, not applied; no baseline duplicates resurrected.
After evidence: update result<=100 lines/ledger, commit+push, final markers from task; stop after marker.
