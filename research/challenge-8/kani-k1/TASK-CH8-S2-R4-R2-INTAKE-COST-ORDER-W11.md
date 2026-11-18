# W11 — ISSUED terminal intake plus actual cost/order explanation

Owner18:52 explicitly authorizes /new11. Follow frozen base task
TASK-CH8-S2-R4-R2-INTAKE-W11.md at e462f0e327801eecee9598a6f5f8af4d9279992d
and postrun-r4-r2/INPUTS.json; this amendment adds focus and current provenance.
Same canonical output run-44336681406/, no duplicate intake. Current model/tier,
Fast OFF; no subagents. STOP only real blocker, not volume/context. No compiler,
verifier/full runner/CI/source/control/ledger/budget changes.

Connected metadata independently confirms terminal FAILURE44336681406/attempt1,
push/head6157554df88fa810496fa6ba10a16a8acc805687/ref…r4r2-20261118.
Exact sourcebd62/control d33/package3cdec7/review7c0a05/GO3c52 as base inputs.
Owner/coordinator reports (NOT yet independently replayed by intake):
- Source compilation COMPLETE35.5s.
- First backend root general32_weak: symex488.5s,4.18M steps,
  376543 VCC /155645 after simplification; group interrupted569.7s at12GiB cap.
- Other10 roots did not start, outcomesUNKNOWN. Counted because root executed:
  item2 10/14,total39/43, ledger943d67bd487ea3ab33e5e77a0d0dfe8453a83532.
Preserve report provenance; derive exact values/units/stages from ONE allowed compact
artifact ch8-s2-batch3probes-44336681406-1 using base-task digest/cap restrictions.

Required additions to COST/RESULT/HANDOFF:
1. Separate compile wall, symex wall/completion, solver phase if exposed, VCCs,
   steps, root/group elapsed, and verification_time_s. Root interruption is not
   a successful negative/control detection; absent final property verdicts UNKNOWN.
   Distinguish raw/rounded counts, sampled maxima vs true peak, RSS vs virtual
   memory, per-backend vs whole process-tree/group sum and monitor's trigger.
   Determine enforced limit/PGID/kill path from exact runner/caps, not kernel-OOM
   speculation. Unknown phase gaps/metrics remain UNKNOWN, not subtraction-based
   invented costs. Preserve exact completeness/censoring and partial receipts.
2. Explain WHY general32_weak was first: reconcile request row order, actual
   command selectors/argv/jobs, codegen/stub-unit grouping and stock0aac launch/
   scheduling order from exact source. Cite bounded paths/lines. Distinguish
   compilation inventory/export order from actual verification start order.
   Do not assume editing JSON row order would control Kani scheduling. If actual
   launch ordering cannot be established, record exact UNKNOWN and missing field.
   This is bounded source tracing of entry/scheduler, not a new compiler audit.
3. Table all11 root outcomes vs execution status. Separate proven NOT_STARTED
   from missing evidence; neither becomes zero cost or proof failure. Show what
   general32_weak teaches about this exact model/domain/caller copy only; do not
   infer general32_assumed or sort13/merge32/swap costs from its single observation.
4. Give compact constraints for r5: cheap-prefix preservation, isolated root RSS/
   timeout termination, executable root order, fresh per-root identities/cfg/stub
   context and safe continuation. No new r5 implementation, run or proof admission.

Base task still governs complete inventories/oracles/diagnostics/provenance,
DIAGNOSTIC_ASSUMED/copy/PFC-registration limits, ownpaths-only [skip ci] commit.
Report source compilation now observed if artifact confirms; a passing compile
supports the repair without uniquely proving historical R3's failing unit/cause.
READY fullSHA/completeness/exactcost/orderbasis/remainingUNKNOWN.
