# RESULT PARTTWO-TREE — INTEGRATED, INVENTORY NOT OBTAINED (kani list timeout), PROOF NOT RUN
Runtime Claude Code, no subagents. Coordinator GO for reviewed `2841212a77c6c5c13147276c9b0f41b3a70cfba8` (parttwotree/PREBUILD.md).
Library commit `2756f0e2a6ae0956fdb427574eda39b5b9a76e64`, tree `a45388ac593c809405558ea0c27599f487b17e4e`; base v6 tree `d4ec476a7a` (= MACSPLIT head 4f4034527d).
Integration: 9 byte-identical files + netcomp.rs (NETCOMP2 blob + netten/neteighteen/mergestep registrations); 3 cfg-gated `mod`
  inserts in verify.rs/network.rs/wrap.rs; runtime/ordinary/tooling unchanged; N1–N4 not transferred (coordinator decision).
Static (check_parttwotree.py 50/50): ordinary 202 = MACSPLIT native exact202, PFC36, insert_tail5; v6 roots unchanged;
  expected cfg-on 438 = v6 384 ∪ 54 transferred (cfg-on-expected.txt sha256 da9bcae2…b578f1b; added ac8c1c4a…74230).
G1 `2fc095d3-81a7-4b4b-9fa5-dec2c3b7a4d5`, request `parttwotree-g1-inventory-cfgon-20261102` sha256 e10c0993…bc4d98, source_sha = reviewed SHA,
  pool k1-standard4 (4CPU/15.6GiB container, swap off), Kani 9461e07af7 / nightly-2026-10-12, controls:true, inventory, 20 min.
check-tooling vs 30f77e8599: PASS (lane files and 6 bound hashes equal).
Outcome: Cloud FAILURE, lane TOOL_ERROR, Kani exit 124, gate false. kani.log (2708 lines): no `error`/panic/Killed/OOM lines;
  cargo `Finished dev profile ... in 11m 56s` (line 2706) for the cfg-on core build, then nothing; `kani list` produced no
  kani-list.json before the job deadline (start + 20 + 24 slack min; Cloud start 17:47:08, finish 18:31:40 UTC, 44.5 min).
Native cfg-on name set: NOT OBTAINED (k1g inventory: none). Expected 438 vs native: UNKNOWN; missing/extra: UNKNOWN.
Ordinary202 source check: static PASS only; no native membership from this tree.
Peaks: compiler / kani-driver / process-sum MISSING (no peaks.txt; summary memcap MISSING). OOM: no evidence either way.
Compile: cargo finish line reached with no error lines, but native harness/contract metadata was not listed, so
  "native cfg-on compile SUCCESS" is not established by this Build.
Cause: UNKNOWN. Not separated: list post-processing time for 438 roots vs setup time before list (CLEANUP G2 382 fit the same
  20-min inventory budget) vs memory pressure. Raw/full logs and Cloud build log not read.
Cost: own 1/1 Build $0.6075 (45 min), reserved own $0; reserve was $0.675 <= cap $0.70. Project after: used $80.9160,
  reserved $0.6750 (foreign unfinished), cap $88.96.
No G2, retry, longer budget, highmem, Actions, PR or next stage run.
Unresolved: (1) native inventory of tree a45388ac59 — coordinator decision (e.g. same request with a larger
  harness_timeout_minutes; request-only change, new reserve); (2) peaks; (3) cause of the list timeout.
Future proof matrix (NOT_RUN): parttwotree/PROOF-MATRIX.md + proof-matrix.tsv — A 28 SUCCESS-gate (6 leaf/consumer pairs
  same-Build), B 17 expected-FAILED single literals, C 10 OPEN/diagnostic. No formal credit from historical rows.
Evidence draft copy: parttwotree/PART2-EVIDENCE-DRAFT.md (N22c from RESULT-NETTEN-CALLER; totals §4.1); shared draft untouched.
Evidence: parttwotree/g1.{summary.md,status.txt,tooling.txt,cost.txt,log-lines-2700.txt,log-grep.txt,inventory.txt}, runs.json.
Status: INTEGRATED + INVENTORY NOT OBTAINED (TOOL_ERROR exit124), PROOF NOT RUN. Stage stopped.
