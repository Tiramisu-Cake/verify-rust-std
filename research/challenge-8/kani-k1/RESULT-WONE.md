# RESULT WONE — PARTIAL (1/4 PFC passed; 2/2 negative controls as expected)
Branch experiment/kani-k1-wone-20261102; task TASK-WONE.md; base e382287728 / v5 cbe69760c8.
Library commit e4f1df6a348fe67277250f84e5a6aa83638a7892; tree 1731596d7c6df1e7fc745fa9e8d6a9ae4df7a432.
REVIEW REQUEST 07e6954e3c6593e18ff28580106d147cd914e1dd; coordinator GO for exact G1 packet.
Full diff/domain/review: wone/PREBUILD.md, library.patch, static-check.json, review.txt.
Opt-in wrap::wone adds stable_cell_len / unstable_byte_len / freeze_noncopy_len / stable_byte_len:
`(v:*mut T, len:usize, [scratch:&mut [MaybeUninit<T>]], cmp:fn(&T,&T)->bool, probe:u8)`.
T = Cell<u8> / u8 / private Freeze !Copy !Drop NonCopyU8 / u8; F canonical cell/byte/noncopy fn pointer.
Requires len<=3, nonnull/aligned initialized writable region; separate entire borrowed scratch.
Stable u8 requires len<2 || scratch.len()>=len+16 (N2/N3:18/19); shorter scratch there aborts.
Modifies v[..len]; Stable u8 also whole scratch slice. Pure key x>>1 sortedness + scalar-old full-byte count.
PFC N0..3: each match arm backing N+2, active offset1/lenN; A/B/C/probe/sentinels unrestricted.
Cell scratch backing2/borrowed0..2, slot0 initialized/slot1 uninit; explicit slot0 and input-sentinel frame.
Stable u8 separate uninit scratch48, input-sentinel frame only; scratch may change; no other sizes proved.
NonCopy route owns internal scratch48; unstable u8 network/insertion; all real trait bodies, no summaries.
Ordinary exact200 unchanged statically; cfg-on388 = cleanup382 + six; old N2 code byte-identical.
pfc_order.py:20 sites/bad0 (includes four gated child PFCs); separate gate/name check, rustfmt/whitespace PASS.
G1 19e85ac8-ab3d-4e47-9fe7-a73547326ae0, wone-g1-20261102: Cloud FAILURE; summary COMPLETE, gate/expectation false.
Kani 9461e07af7; reviewed head/request hash match; measurement, controls on/jobs1/uninit off/timeout10.
Compilation succeeded; tooling vs 30f77e859903df14b442ff9294d4fbbd44827f20 PASS; check/peak artifacts in wone/.

| wrap::wone row | Status | VT s | cbmc RSS KiB | Fail/total | Covers |
|---|---|---|---|---|---|
| stable_cell_n0_to3 | SUCCESS | 147.8958 | 968156 | 0/328 | 18/18 |
| unstable_byte_n0_to3 | TIMEOUT | UNKNOWN | 2101724 | UNKNOWN | UNKNOWN |
| freeze_noncopy_n0_to3 | TIMEOUT | UNKNOWN | 15585836 | UNKNOWN | UNKNOWN |
| stable_byte_n0_to3 | OUT_OF_MEMORY | UNKNOWN | 15679436 | UNKNOWN | UNKNOWN |
| rejects_always_true | FAILED expected | 0.21927 | UNKNOWN | 1/289 | 1/1 |
| rejects_payload_corruption | FAILED expected | 3.60902 | 85120 | 1/310 | 1/1 |

Only failed literals: `wone canonical comparator required` wone.rs:58; `wone full-value checker rejects payload corruption` :321.
RSS is sampled process VmHWM, direct metadata binding; run time-v max15681840KiB, wall38:25.66; OOM scan positive.
Established: Cell Stable N0..3 sorted/count/frame in listed fixtures; N0 input no-op/vacuous sorted-count,
N1 trivial order but substantive singleton count preservation; N2/N3 covers reversed/tied/duplicate.
Controls establish canonical rejection and sensitivity to ^=1 payload corruption after real Stable u8 N3.
Other three PFCs remain OPEN; controls do not prove those contracts. N0..3 != N0..32; no all-backings/stability/init claim.
Own builds1/2, spent$0.6345/reserved$0 <=$1.5; no G2: no compile error, same reserve would total$1.8495.
API ready for later N expansion; proof/resource readiness blocked. N4..N8 cost-to-success UNKNOWN; baseline envelope
20 wrapper×N positives+2 controls, four batches<=6, timeout10: (220+120)*$0.0135=$4.59, no success guarantee/authorization.
WONE ЗАВЕРШЁН — PARTIAL; this stage stops, no automatic L1/length expansion or additional Build.
