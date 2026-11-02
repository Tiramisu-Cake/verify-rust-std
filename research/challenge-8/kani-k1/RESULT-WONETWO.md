# RESULT WONETWO — SUCCESS (3/3 fixed-N2 PFCs)
Branch experiment/kani-k1-wonetwo-20261102; 2026-11-02; base WONEDIAG b7a8db4a98.
REVIEW REQUEST d32f2107a4e57db5ea4046b4b43d01ebf21b700d; coordinator GO for this exact packet.
Library commit 4231462d124b8c69bfaa55dd0eb956717308f1be; tree c407b96a8cde34a9f28b8a967bf897f74bd06992.
G1 84ff0a05-c37c-4628-8675-28241997093d / wonetwo-g1-20261102: Cloud SUCCESS, COMPLETE, gate/expectations true.
Kani9461e07af7; measurement/controls:true/jobs1/uninit off/timeout10/standard4/unwind16 unchanged.
Head/request/pin/pool identities match; check-tooling vs 30f77e859903df14b442ff9294d4fbbd44827f20 PASS.
Three appended opt-in PFCs: backing4/offset1/literal2, unrestricted A/B/probe/sentinels, no length dispatch.
Private T/F/CMP, targets/requires/ensures/modifies/bodies and all old harnesses remain byte-identical.
Stable u8 retains separate uninitialized scratch48, entire borrowed slice and whole-slice modifies.
Static ordinary exact200/cfg-on394, target ordering26/bad0, rustfmt/whitespace PASS; counts are not proofs.

| wrap::wone wrapper | Length | Status | VT s | cbmc RSS KiB | Failed/total | Covers |
|---|---|---|---|---|---|---|
| stable_cell | N0..3 (WONE) | SUCCESS | 147.8958 | 968156 | 0/328 | 18/18 |
| unstable_byte | N2 | SUCCESS | 31.006783 | 227280 | 0/492 | 7/7 |
| unstable_byte | N3 (WONEDIAG) | SUCCESS | 59.776577 | 416160 | 0/498 | 7/7 |
| freeze_noncopy | N2 | SUCCESS | 193.36943 | 814568 | 0/472 | 7/7 |
| freeze_noncopy | N3 (WONEDIAG) | SUCCESS | 272.5441 | 1161416 | 0/478 | 7/7 |
| stable_byte | N2 | SUCCESS | 181.03746 | 808972 | 0/469 | 7/7 |
| stable_byte | N3 (WONEDIAG) | SUCCESS | 286.1486 | 1156924 | 0/475 | 7/7 |

Cell/N3 entries reuse RESULT-WONE.md / RESULT-WONEDIAG.md evidence; they were not rerun here.
N2 covers: return/reversed/increasing/tied-distinct/duplicate/independent-probe hit/miss; 21/21 satisfied.
No failed checks; N2 unreachable checks 18/8/8 in row order; input_frame checked after return.
VT explicitly printed. RSS sampled kernel VmHWM with direct metadata binding; OOM scan none_seen.
Whole-run wall8:08.66/maxRSS1728084KiB incl compilation; own builds1/1, spent$0.2025/reserved$0 vs $0.810 reserve.
For the three byte/NonCopy wrappers: sorted keys x>>1/full-byte count/frame proved only at N2/N3 in these backing/scratch48 fixtures; not N16/generic T/FnMut.
Not a replacement for ordinary N2 wrappers without separate correspondence review; evidence: wonetwo/g1.* and final-check.json.
WONETWO ЗАВЕРШЁН — SUCCESS; this single stage stops, no retry or further Build.
