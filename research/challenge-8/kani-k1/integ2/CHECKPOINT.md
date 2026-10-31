# INTEG2 — PARTIAL: G1 compile error; G3 controls PASS; G2 watcher pending

Work only in `/root/verify-rust-std-kani-integtwo`, branch `experiment/kani-k1-integtwo-20261031`.
Coordinator Claude Code explicitly approved review source e0ff82577dc58950621dadc9c141d88a5821987f.
GO is recorded in go.json; task is ../TASK-INTEG2.md.
Library commit20aa864ad04e8d81b46d41024b75dc7aa1103dcf;
frozen tree c522edd42ae67c385e1ee42a1c4d1bffb611c90b for all three builds.
No semantic library changes without committed delta review/GO.

Actual request/source SHA/UUID/status and own accounting: builds.json.
All3/3 slots consumed; no additional dispatch allowed.
All three watches already registered. G1/G3 delivered and reviewed; G2 pending, do not re-register.
G1 cda795d5-1cd1-4c32-a87e-778302647151 FAILURE/TOOL_ERROR, Kani exit1, no native inventory.
Primary source error E0425 network.rs1268: ordinary START1 helper uses controls-gated import.
Additional E0034 checked_sub/MAX diagnostics observed; causal resolution unestablished.
G1 tooling PASS, cost0.108; G3 COMPLETE/gate true, three controls accepted, cost0.1215.
G3 one intended FAILED each, covers3/3; actual source locations841/1257/1260 manually verified.
See g3.controls-review.json; no other failures/OOB, sortedness839 not FAILED (no explicit SUCCESS).
Own selected UUID ledger spent0.2295/reserved1.215; no additional slots.
Evidence: g1.summary.md, g1.error-context.txt, g1.diagnostics.txt, g1.failure-review.json.
Proposed fix g1-proposed-import-cfg-fix.patch only removes import cfg, NOT_APPLIED.
Cfg availability source review in g1-import-availability-review.json; not a compiler/proof result.
Initial source audit/unused forecast missed gated-import availability; preserve historical reports.
Frozen library stays unchanged; any semantic delta requires committed review/GO.
Next end turn awaiting G2 notification; then exact cfg-on479 inventory/bindings/pages and warnings review.
Original T0 UTC11:58, deadline16:58 UTC/19:58 MSK, closing30min; never reset.
Only k1-standard4; CAP_USD73.96/pin/toolchain/flags/lane unchanged.

Source forecast ordinary197/cfg-on479/static P2=343; exact manifests in scope/.
Source audit, helper-use forecast, scope check, static P2 apply/name check and prescribed rustfmt PASS.
All native inventory/proof/compiler warnings on candidate remain unreviewed until terminal results.
G3 controls accepted on frozen tree; actual review is g3.controls-review.json; original plan unchanged.
Use only approved K-1 summary/inventory/peaks/log-grep/log-lines/check-tooling/budget readers.
Review exact inventory sets and complete bounded pages/bindings; targeted compiler warnings.
G3: exactly one intended count/prefix/suffix FAILED per harness, all covers, no other failures/OOB.
Check actual location/class against frozen source manually; matcher mismatch stays gate=false.
No local Rust/cargo/Kani/CBMC, no Actions/CircleCI/submission branches.
Native P2/macOS/positive integration proofs/full CI remain NOT_RUN; coordinator owns later CI.
Cfg-only fallback patches in cfg-fallbacks.json, not applied; no baseline duplicates resurrected.
After evidence: update result<=100 lines/ledger, commit+push, final markers from task; stop after marker.
