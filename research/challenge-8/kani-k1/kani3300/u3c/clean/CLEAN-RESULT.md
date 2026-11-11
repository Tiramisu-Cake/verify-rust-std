# KANI3300 U3C clean — промежуточная классификация
Build `87c1def4-07d7-4233-84ea-5b01eda765a2`, source `08438b07d1a6dd646cd8c8b7f638ec509229b7e7`: Cloud FAILURE / TOOL_ERROR; native6 PASS,1 ERROR; tool build PASS.
Applied tree `97f86904b400e81c9b269cdafa957750ef741eea`; exact identities и tooling check PASS.
|root / контроль|uninit|clean terminal observation|selector wall s|
|---|---|---|---:|
|contracted_roundtrip_harness|on|native timeout/kill/build/runner ERROR; precise cause UNKNOWN|162.497|
|contracted_roundtrip_harness|off|SUCCESS|3.237|
|contracted_uninit_read_harness|on|VERIFICATION FAILED; actual Failed Check UNKNOWN|124.869|
|contracted_uninit_read_harness|off|SUCCESS, diagnostic only|1.069|
|MU-free PFC write_u16_harness|on|SUCCESS|1.471|
|MU-free PFC write_u16_harness|off|SUCCESS|1.069|
|MU-free plain write_u16_harness|on|SUCCESS|0.767|

Positive-on: report merges timeout/kill/build/panic classes; excerpt reaches Checking harness, lacks terminal result/explicit OOM.
Elapsed time alone does not prove timeout or OOM. Per-root RSS/kernel confirmation unavailable.
Negative-on: own-output diagnostic FAILED established; KT2 omits excerpts for native PASS, even when verification fails.
Targeted native-field output_excerpt returns unknown field; uninit/assigns/other property remains UNKNOWN.
Five SUCCESS entries use actual own-output SUCCESSFUL diagnostic, not neutral golden or native PASS alone.
U3B v2 on-pair had explicit Kani-reported OOM (~50/51 s), off-pair SUCCESS; no v2 MU-free run exists.
Clean comparison does not establish pre-existing OOM or v2 regression; causal mechanism remains open. Await U1.
Cost $0.1755; reserve0; proposed U1 reserve $0.4725; total $0.6480 <= cap$0.95.
Next: unchanged U1 production + identical fixtures, separate exact PRE-BUILD GO; no repair or second marker.
