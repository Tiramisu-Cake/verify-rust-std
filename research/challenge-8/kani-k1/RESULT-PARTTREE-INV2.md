# RESULT PARTTREE-INV2 — INTEGRATED + INVENTORY PASS, PROOF NOT RUN
Runtime Claude Code, no subagents; owner k1-merge. Coordinator GO for reviewed/published `8cba6bd0fd136c39d854b1c228d24e85785a6043`
(parttreeinv2/PREBUILD.md). Library commit `2756f0e2a6ae0956fdb427574eda39b5b9a76e64`, tree `a45388ac593c809405558ea0c27599f487b17e4e` unchanged.
Request `parttreeinv-g1-cfgon-20261102` sha256 fca8268d…5067d149 = RUN-REQUEST.json at build commit; diff vs
  parttwotree/g1.request.json only request_id/purpose/harness_timeout_minutes 20→60; kind inventory, controls:true, harnesses:[].
Build `02b46b34-d19c-47c1-9f96-52f84d72467b`, pool k1-standard4 (4CPU/15.6GiB container), source_sha = reviewed SHA, timeout 5400s.
  Cloud create 19:00:20, start 19:01:51, finish 19:40:39 UTC (38.8 min), status SUCCESS; lane COMPLETE, Kani exit 0, gate true.
check-tooling vs 30f77e859903df14b442ff9294d4fbbd44827f20: PASS (lane files, pool, 6 bound hashes). Kani 9461e07af7, nightly-2026-10-12.
Inventory artifact sha256 82161be4…ae6028 (header binds request/build/head/Kani); names_sha256 81855bf3…da94fd in artifact order;
  6 pages offset 0..400 by next_offset to `done`, total 438, 438 unique.
check_native_inventory.py g1: ok — native set == parttwotree/cfg-on-expected.txt (sha256 da9bcae2…b578f1b) = 438;
  missing [], extra [], duplicates []; ordinary members 202/202, added opt-in 54/54. Sorted-unique native set sha256 = da9bcae2…
  (expected file is sorted); raw artifact-order hash differs only by order.
Bounded log (log-grep/log-lines): cargo `Finished dev profile ... in 10m 11s` (line 2706), `Wrote list results to
  .../kani-list.json` (line 2709); no ^error/panicked/Killed/Terminated lines.
MISSING/UNKNOWN: list start/end timestamps and list duration (not exported; not derived from Finished line); peaks/VmHWM
  (no peaks.txt, inventory branch has no sampler); memory cap MISSING. PARTTWO-TREE G1 timeout cause stays UNKNOWN
  (this run only shows 60-min budget sufficed; 20-min runs not compared further).
Static (unmodified check_parttwotree.py, re-run pre-build): PASS 50/50; ordinary 202, PFC 36, insert_tail 5; outputs byte-equal.
Native cfg-off inventory of this tree not run; not inferred from cfg-on.
Scope: compile/list only. No formal verification of the 54 transferred roots; no AST/MIR/callee-binding or theorem credit.
Cost: own 1/1 Build $0.5265, reserved $0; reserve was $1.215 ≤ cap $1.25. Project after: used $82.0635, reserved $0, cap $88.96.
Historical PARTTWO-TREE result/ledger untouched. No G2, retry, highmem, Actions, PR, or proofs.
Evidence: parttreeinv2/g1.{status.txt,summary.md,tooling.txt,cost.txt,inventory-page-*.txt,inventory-check.json,
  log-grep.txt,log-lines-tail.txt}, runs.json, budget-final.txt.
Status: INTEGRATED + INVENTORY PASS, PROOF NOT RUN. Stage stopped.
