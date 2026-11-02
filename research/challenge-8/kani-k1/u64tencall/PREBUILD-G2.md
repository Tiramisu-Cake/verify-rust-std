# U64-TEN-CALLER PRE-BUILD REVIEW — G2 (controls)

Status: WAITING FOR COORDINATOR GO for G2. G2 not submitted; its compile/proof/covers NOT_RUN.
Runtime: Claude Code, executor alone. Task TASK-U64-TEN-CALLER.md (c80444e8c6); G1 packet PREBUILD.md
(GO 656e806666). Review SHA is the published research commit carrying this file.

## G1 terminal record (accounted)

Build 06da11e6-9985-4965-9464-215cc3ddf390, source 656e806666 (reviewed), pool k1-standard4, Cloud FAILURE
(Kani exit 137), 17:31:22Z -> 17:47:03Z. check-tooling vs 30f77e8599 exit0, 6 bound hashes match.
Compilation finished (`Finished dev ... 1m 04s`), harness started with exactly the 4 expected stub lines
(2 Stub, 2 Verified stub; g1.checks-lines.txt), then `Killed`: dmesg global OOM, task=kani-driver,
anon-rss 15764868 KiB. Row u64tencall_positive_u64_n10: UNKNOWN (no VT/checks/covers printed).
Peaks (g1.peaks.txt): kani-driver VmHWM 15285244 KiB sampled @503s (time -v max 15764976 KiB);
CBMC 2711020 KiB @272s (seen 72-469s); compiler 1865500 KiB; process-sum 15302404 KiB @503s; wall 9:01.
Driver stayed ~7 MiB to 270s, then grew ~0.77 GiB/30s from ~300s while CBMC ran, to OOM.
The fresh-process hypothesis is refuted for this positive: one u64 row alone exceeded 15.6 GiB.
Cost $0.2160 (budget 06da11e6). Not a compile error -> no G1R; positive stays OPEN (stage <= PARTIAL).
No highmem/tooling/timeout/narrowing change; no further positive Build.

## G2 package (unchanged library, only research/request metadata changes)

Library commit a6010df7b451da55d4227ad5960b0c93992f10f0 / tree 514c6f841cf2af3b27f6d9aa8f27c86e24c562af,
identical to G1 (static_check.py PASS again, same child_sha256 9f434dae...). RUN-REQUEST.json :=
g2.request.json, byte-equal, SHA256 2344a3b82f536f8e7b656cf319f7870029922c4eee7c956d09f440bbe8091862;
request-g2.diff (zero context) shows only request_id/purpose/harnesses changed vs G1.
Request usixtyfourtencall-g2-controls-u64-n10-20261102, agent k1-network, measurement, controls:true,
jobs1, uninit off, 10 min/row, gcb-e2-standard-4 -> k1-standard4 (4CPU/16GiB, swap off);
validator accepted 3 rows (g2.args). Kani 9461e07af7 / nightly-2026-10-12, unwind25 + unwinding assertions.

| Row (...::tenleaves::caller::) | Input / probe | Flags | Expect | expect_check (literal, caller.rs line) | Covers |
|---|---|---|---|---|---:|
| u64tencall_swap_binding_negative_u64_n10 | [0;10] / 0 | T/F | FAILED | `u64tencall actual swap adapter binding control` :111 | 1 |
| u64tencall_insert_binding_negative_u64_n10 | [0;10] / 0 | F/T | FAILED | `u64tencall actual insert adapter binding control` :172 | 1 |
| u64tencall_count_negative_u64_n10 | [2^40;10] / 2^40 | F/F | FAILED | `u64tencall negative: full-value count preserved` :339 | 2 |

Covers: swap `u64tencall swap control: actual entry reached` (:297) and insert `u64tencall insert control:
actual entry reached` (:312), each before actual entry; count `returned before corruption` (:332) and
`count check reached` (:336). Swap control: first raw swap passes base/pair/canonical/backing10/probe/
phase guards, fails only marker. Insert control: 25 swaps + all insert premises (prefix9 sorted asserted,
counts, tail, probe) pass, marker fails. Count control: run_u64ten + check_final pass, v[9]=Q=2^41 (same
low 32 bits as P), sorted10 holds, the same count10_preserved_u64 fails only the literal (count 10->9).
No post-guard obligations required; checks after an expected failing marker may be unreachable.
Any other failed check/UB/unwinding/unsupported = FAIL. Gate compares exact literals, not exit code.
Memory risk (fact, not mitigation): G1 positive driver OOMed; driver peaks of these concrete-input rows
are unknown. G2 OOM/TIMEOUT -> per-row facts, PARTIAL, no new Builds (G2R only after compile error).

## Budget/slots (refreshed 2026-11-02T17:50:19Z, k1g.sh budget)

builds175, used$80.1060, reserved by unfinished$0.6750 (one queued/running project Build, not
k1-network: own G1 is terminal). G2 reserve (3*10+30)*$0.0135=$0.810 -> $81.5910 <= $88.96.
Own: spent $0.2160 (G1), reserved $0; +G2 $0.810 = $1.026 <= cap $2.80 (G2R $0.810 would reach $1.836).
Slots after submit: project 2 (<=2), k1-network 1 (<=1). Refresh before dispatch after GO.
