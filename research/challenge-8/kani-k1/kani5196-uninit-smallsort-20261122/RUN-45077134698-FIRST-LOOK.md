# Run 45077134698 — kani5196 SmallSort uninit experiment (coordinator first look)

Fork kani `uninit-ci/ch8-q-pilot-v1`, trigger `29b4206fb46322f7c47484ed7be572490290aeaf` (tree `cf85db1883`, parent `3c9b9e7590`, = reviewed control `467af9cb8d`). Job `uninit` success, 22:20–23:03Z (43 min). Index: stop_reason null, 26/26 roots EXITED. Artifact: `/root/ch8-artifacts/run-45077134698/ch8-kani5196-45077134698-1/`.

Coordinator heuristic counts (regular.json; "unsupported" = non-UNREACHABLE properties whose description mentions unsupported). Not a verdict.

| Pair | OFF | ON | ON failures | VT off→on s | peak RSS off→on KiB |
|---|---|---|---|---|---|
| canary positive | — | 0 of 153 failed | — | | |
| canary negative | — | 2 of 78 failed | uninit read `*const u32`, `u32` (expected pair) | | |
| candidate S2 | 0 of 426 | 2 of 877 | uninit read `*const usize`, `usize` | 2.1→16.4 | 2042212→2496408 |
| candidate UF2 | 0 of 652 | 2 of 1179 | uninit read `*const usize`, `usize` | 2.6→28.9 | 2108876→2520828 |
| candidate N18 | 0 of 393 | no terminal summary | — | 17.0→none | 2044740→7587440 (near 8 GiB cap) |
| candidate M8-C | 0 of 229 | 0 of 353 | — | 48.3→68.4 | |
| candidate M8-R | 0 of 271 | 2 of 409 | uninit read `*mut [u64]`, `*const MaybeUninit…` | 4.6→40.6 | 2000060→2423056 |
| candidate S2-C | 0 of 487 | 3 of 915 | uninit read `*const usize`, `usize`; unsupported: calls through function pointers | 69.8→102.2 | |
| candidate F2-C | 0 of 497 | 3 of 951 | same as S2-C | 69.4→112.5 | 2572832→2548424 |
| pr752 head, all five pairs | no summary | no summary | — | — | ~1.5 GiB (likely compile incompatibility of the older toolchain) |

Index calibration state: INCOMPLETE (canary unsupported counts 4/1). Planner offline analysis pending: calibration, per-root classification, triage of the `usize` and M8-R reads (real body vs model/harness vs tool), N18 ON cutoff phase, pr752-head blocker.
