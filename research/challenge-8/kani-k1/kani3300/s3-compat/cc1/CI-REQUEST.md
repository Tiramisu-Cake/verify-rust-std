# CC1 bounded coordinator request — no dispatch authorization

Exact source/base/tree/inputs: INPUTS.json. Exact12 invocations,14 harness results,
source SHA256, selection, environment and flags: CI-ROOTS.json. No local execution,
CI overlay or push by worker14. Coordinator owns independent review, GO, submit,
resource caps, source publication and binary capture. Binary hashes UNKNOWN until
that exact source is built; pin driver/compiler/CBMC hashes in the build receipt.

1. Independent semantic review of the source diff/dependencies against C2.
2. Existing build/preflight/typecheck recipe on nightly-2026-10-23, then targeted
   Rust helper units (`cargo test -p kani-compiler active_call_tests`, CI ONLY).
   Build cap600s, unit cap120s; stop before proof on build/type/unit failure.
3. Run the12 manifest invocations sequentially in fresh directories,1 job each.
   Singleton: scripts/kani INPUT plus common_cli, --exact --harness ROOT,
   output_cli and tail_cli. Mixed: same command with no --harness/--exact;
   require exactly the two listed roots. CHECKOUT/scripts/kani execs exactly
   CHECKOUT/target/kani/bin/kani-driver (with argv0 kani); retain that wrapper
   and the matching CHECKOUT/target/kani/bin/kani-compiler identities.

Proposed caps require coordinator GO:120s per harness,180s per whole invocation,
RSS12582912KiB, total envelope3600s including preparation/collection. Source
unwind attributes4/8 remain intact; default unwind8 only fills absent attributes.
Object bits12 is explicitly per invocation, passed last through --cbmc-args.
Default solver, slicing, unwind/overflow/memory/undefined-function/reachability,
contract/receiver/bool checks remain enabled. No retries/H1 matrix/new tracing.
Build exceeding its complete cap is a preparation failure, not a verifier result.

Original recursive_check, recursive_ordinary and recursive_simple_check MUST be
separate exact invocations. Do not use the existing mode collector to stop these
companions after the first error. Original source hashes stay unchanged. A new
cycle Unsupported must bind to the actual entry and list its active cycle path.
An ordinary recursive root with Unsupported remains release BLOCKED. The
SimpleCheck companion's remaining bool/layout failures remain failures, never
mode-exclusion success. The capture-free legal recursive-mode companion removes
predicate/upvar confounding only; it does not qualify recursive mode.

Retain complete per-root JSON plus regular property inventories (including all
successful/failed/unreachable/cover/Unsupported checks), selected model artifacts,
source/model binding and binary recipe. Preserve original exit/signal, timeout,
RSS KiB and command/environment. Missing/malformed/partial export, collection
crash, stack overflow, signal or cap is failure, never expected-negative PASS.
Cycle roots need targeted Unsupported, complete exports and no stack overflow.
Positive DAG/P1/independent roots need reached useful assertions/covers and no
extra failures. Hole control needs actual read check binding, no unrelated
protocol/frame/Unsupported/invalid-value failure; record the full exact set.

For mixed files establish actual starting_items grouping/order using existing
preparation artifacts; declaration order alone is insufficient. If the two source
permutations induce the same internal order, record order coverage UNKNOWN;
require helper unit coverage of both orders and a coordinator-approved existing
way to exercise both actual orders before claiming that integration obligation.
Compare good root mixed/singleton complete inventories; no leaked error/seed/body.
Inspect actual registration versus discarded overrides from the selected model.

Read coordinator evidence only through the established Evidence Brief interface.
No raw logs/archive downloads or historical oracle/mode-findings rewrites.
After this targeted stage, common reviewed-head Quick + all8 strong oracles and
C03/S3 hole controls remain a separate composition gate; M3/full/platform/SmallSort
also separate. CC1 makes no Part1 GO and does not issue CC2/CC3.
