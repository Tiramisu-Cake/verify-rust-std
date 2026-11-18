# W13 — r4-r2 control-only validation timeout repair

AUTHORIZED owner17:54; coordinator issues to fresh /new13 after preserving the
current gate-only backlog packet/READY. Current model/tier, Fast OFF; no subagents.
STOP only real blocker, not volume/context. No compiler/verifier/full runner/CI.

Source MUST remain bd62e54df1b4749154790aa3db3cc7978f547f75,
tree dc2e7a7f258719a05c65bbb9b1e2c7f1e8271ac8. No source commit/edit.
Frozen control0e8c836857344866564e1423ad5d8d28bbc4106b,
tree9f7c903f2039e6a52b19f37c5f32fbd9cc86566f;
package474e0b4209554bdd69c4303410192d2d472af4a2 and GO6db728b62b unchanged.
Actual run44328364855/1 head173ed30be4cabb6d5f0937279cf0d28cd4e21bae:
coordinator17:54 reports step4 Validate control and synthetic wrapper TIMEOUT
at1min, observed tests ~70s14:48:52->14:50:01; observed tests ok is not suitePASS.
Tool not built, source not compiled,0roots. This is PREBUILD_VALIDATION_TIMEOUT,
not compilefailure. Owner/coordinator charged0, ledger a48799887ccf28ef48e2841f55e817a8398e5f32:
29/29 +9/14=38/43. Accounting is reference only, no policy broadening/refund action.

1. New immutable control/profile: raise ONLY Validate control and synthetic
   wrapper step timeout from1 to10 minutes as explicitly approved. Audit every
   other setup timeout against the enlarged actual command/test workload.
   Record step/name/command/cap/known elapsed/or UNKNOWN, aggregate-clock origin,
   remaining budget and justified keep/change decisions in TIMEOUT-AUDIT.md/json.
   Inspect Check all source identities (currently1min) using actual source gate
   timing. Keep aggregate setup1800s, job180min and proof/backend/group caps;
   sum of step maxima is not actual elapsed and does not override aggregate clock.
   Only additional setup-step increases justified by evidence and within these
   bounds; no speculative changes to build/tool/verification/resource budgets.
2. Gate R14-03 fix may integrate ONLY if its exact gate-only candidate is READY
   and independently APPROVE/CLOSED by14; coordinator supplies committed pins.
   Otherwise prepare timeout-only candidate and explicitly retain R14-03 OPEN;
   do not consume unreviewed backlog bytes or pretend previous exception transfers.
   Previous GO6db exception was one-run-only and is spent. A future exception
   needs fresh coordinator/root decision on exact new pins, if still needed.
3. If approved gate patch is integrated, inherit its reviewed extractor/test bytes
   by exact hash; include its new regression module in actual validation command
   (old command enumerated modules explicitly). Rebind every control/payload/hash
   inventory and source/request/gate maps, workflow copy, parser/oracle fixtures.
   If wiring changes from gate-only review, expose precise integration delta.
4. Execute the actual final Validate command ONCE offline with monotonic timing
   and exact final-object provenance, plus necessary changed-timeout/order/aggregate
   boundary checks. This phase justifies measuring the complete command, unlike
   the preceding narrow gate-only task. No runtime Rust/compiler/full runner.
   Distinguish this machine's duration from GitHub runner time; future duration
   is unknown. Do not claim future timeout absence or relabel partial oldCI asPASS.
   Audit/time actual check-source once; no unnecessary broad repeated suites.
5. Source/tool unchanged, no model/domain/frame/init/oracle changes. Keep11roots,
   20covers,6 exact negatives, DIAGNOSTIC_ASSUMED and copy-identity limits,
   all protected diagnostic/collector/packer/B-01/B-02 controls. Backend600s,
   compile900s, rootsum6600s,group7500s,internal8100s,step7560s,RSS12+2GiB,
   serial1 remain. Native compile/causal repair NOT_RUN, actualR3unit UNKNOWN.

NEW isolated control sole parent9e14e033f9ee31522b571c127609dcdff76d230b,
not child0e8; unchanged source already has parent97ac. Checkout7/5/2.
Write only g0 kani3300/ch8-s2/batch-r4-r2/: full exact pins/request/workflow,
control delta/parent/stock patches, unchanged-source checks, timeout audit and
actual final command timings/tests, gate-review dependency or explicit OPEN,
invariance/maps/manifests/validator/replays/shallow checks/REVIEW14-REQUEST/HANDOFF.
Preserve all old packets. Ownpaths-only --only [skip ci] commits.
Next same14 delta review of final candidate, then root GO-request r4-r2 ONLY;
coordinator alone separateGO/dispatch/accounting. No CI/rerun/cancel/push/PR/issue/
source publication/ledger/reservation/budget. READY full package/control/tree/
parent/request hashes, source unchanged, gate dependency and measured limits.
