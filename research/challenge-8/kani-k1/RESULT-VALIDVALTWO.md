# RESULT-VALIDVALTWO
Stage `validvaltwo-s1`; request `validvaltwo-s1-20261104`; owner `k1-merge`; runtime Codex.
Build `13642a63-de9e-4e28-b4e3-f55fd370538d`; source `79043a28cfd8caa42ecfe7b3446ad00b52c599ba`; Cloud Build FAILURE, compilation SUCCESS.
Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`; library `5453d3515f19a5b63368710170a67631f2018b0f`.
Request SHA256 `d455ff141b7bead9b3bd42fe66803e781ce113c7da267cbe6c2fefa4407c0564`.
`check-tooling` PASS against `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`: source/run identities, all six hashes, lane equality and k1-standard4 pool.
Diagnostic: controls=true, valid_value_checks=true, uninit_checks=false, jobs=1, 10 min/root; outside organizer CI. One build, actual $0.1215, reserved $0, own cap $0.90; no retry/repair.
Evidence: bounded K-1 summary, rows 0..2 (next_offset=done), log-grep and log-lines 2710..2747, check-tooling and selected-build budget; no raw evidence access.
Roots have prefix `slice::sort::shared::smallsort::verify::validval::`; located failures below use `/workspace/src/library/core/src/`.

| Root | Actual classification | Exact text / location | Failed/total; covers; time |
| --- | --- | --- | --- |
| accepts_bool_byte_0_or_1 | SUCCESS | VERIFICATION:- SUCCESSFUL; no failed check/location | 0/33; 2/2; 0.05790285s |
| unstable_bool_n2 | UNSUPPORTED OPERATION (reported FAILED) | Kani currently doesn't support checking validity of `copy_nonoverlapping` for `*const bool`; `ptr/mod.rs:578`, ptr::copy_nonoverlapping::<bool> | 1/688; 2/2; 1.0034426s |
| unstable_bool_n4 | UNSUPPORTED OPERATION (reported FAILED) | Kani currently doesn't support checking validity of `copy_nonoverlapping` for `*const bool`; `ptr/mod.rs:578`, ptr::copy_nonoverlapping::<bool> | 1/694; 2/2; 1.4320953s |

No timeout, compile error or invalid-value counterexample occurred. COMPLETE accounts for all rows; gate=false. Real-root covers 2/2 do not override unsupported checks (23 unreachable checks/root).
Together with RESULT-VALIDVAL: deliberate bool byte 2 and char surrogate loads are detected; valid bool/char loads pass, with the bool positive control reproduced here. Real bool N2/N4 now show the same unsupported copy_nonoverlapping validity class as char/NonZeroU8 N4, not successful safety/value-validity verification.
Both fixed bool roots use Unstable network entry's insertion body from index 1; no sort9/sort13 or scratch merge. Symbolic bool N4..8 remains unresolved by VALIDVAL's 2-minute timeout; these fixed roots do not resolve it.
NOT_RUN: bool N8, other sizes/routes/types, uninit checks and a wider validity matrix. No sorting-correctness claim; the single authorized build is closed with these limitations.
