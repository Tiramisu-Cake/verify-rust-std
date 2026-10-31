# INTEG2 — CLOSED / PARTIAL, three builds consumed and all results reviewed

Worktree /root/verify-rust-std-kani-integtwo, branch experiment/kani-k1-integtwo-20261031.
Coordinator Claude Code; original task ../TASK-INTEG2.md.
GO source e0ff82577dc58950621dadc9c141d88a5821987f; go.json.
Library20aa864ad04e8d81b46d41024b75dc7aa1103dcf;
frozen library tree c522edd42ae67c385e1ee42a1c4d1bffb611c90b for all three requests.
No library changes after GO. Report ../RESULT-INTEG2.md <=100 lines.

G1 cda795d5-1cd1-4c32-a87e-778302647151, source e0ff82577d:
FAILURE/TOOL_ERROR, Kani exit1, ordinary inventory absent. Cost USD0.1080.
E0425 network.rs1268: ordinary START1 group helper uses controls-gated set_value_probe import.
Additional E0034 checked_sub/MAX diagnostics recorded; causal resolution not established.
Initial source binding/unused forecast missed cfg-availability; historical reports retained.
g1.failure-review.json/g1-import-availability-review.json document the finding.
g1-proposed-import-cfg-fix.patch removes only the import cfg, NOT_APPLIED.
Any library delta requires committed review/GO; this session has no remaining build slot.

G2 7a0cbca0-dda5-4cb2-a0ea-ad6f9112ad71, source580296b8f5:
SUCCESS/COMPLETE/gate true, exact cfg-on479 names in six bound pages, no duplicates/missing/extra.
g2.inventory-check.json binds request/source/pin/artifact/names hashes and complete coverage.
Cost USD0.6075, targeted warnings no match; inventory resource/time fields MISSING.
Native enumeration only, no positive verification credit.

G3 fb2ec8a5-9870-4301-a892-ad5d48b74560, source00c7a1e00a:
SUCCESS/COMPLETE/gate true, expected Kani exit1. Cost USD0.1215.
Exactly one intended FAILED each, covers3/3, no other failures/OOB.
Manually verified frozen-source count841/prefix1257/suffix1260 locations/classes.
Sortedness839 not FAILED; terse output has no separate explicit sortedness SUCCESS line.
g3.controls-review.json/g3.rows.txt/g3.summary.md bind the accepted negative controls.

All three tooling checks PASS against GO. Only k1-standard4; pin/toolchain/flags/lane/CAP unchanged.
Own exact UUID ledger budget-final.txt: spent USD0.8370 <=2.90, reserved0, builds3/3.
All watches delivered and all terminal results reviewed; no pending watch/build and no more dispatch.
Original T0 UTC11:58/deadline16:58 and closing30min preserved; closed within original window.
No local Rust/cargo/Kani/CBMC, Actions/CircleCI, submission branches or positive integration proofs.
P1-max197/static P2=343; full names/diffs/manifests in scope/, static P2 apply/name check PASS.
A-u8 N5..8 retained; fallback patches in cfg-fallbacks.json NOT_APPLIED; no baselines resurrected.
Native P2/macOS/full CI NOT_RUN. Candidate is not green; ordinary compile blocker must be resolved.
Coordinator handoff: review/GO import fix, later ordinary inventory, macOS/cfg selection and full CI.
After final commit/push and completion marker, do not continue this closed session.
