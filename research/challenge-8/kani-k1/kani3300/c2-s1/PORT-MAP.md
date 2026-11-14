# C2-S1 — source port map

Candidate `ba0e5cfedf31e20d18e95b50ba5dbd6946277d2c`, tree `0fe7f51c1017656ae141f7d223ac737a930d7265`; sole parent B1 `6fe484b30043b3696b5f1ccc4bea0e42891ad012`, whose sole parent is U `0aac16ef62da9e9d5645782d458593e5d78143ba`. Branch `fix/kani-3300-c2-s1`, clone `/root/kani-fix-3300-c2-s1`.

Accepted C1b `3f2c12f46e9e32899e8d84e89c65cb6483ba685a`, tree `e629978d8f0746bddf896d58a156bad2c59f14ce`; merge base `bf9c58e662fd65c64381ef2ac97a6397ffc0693a`. g0 input `7eff3294c6f4baca0d19d1eabe6fc24de2bca6a7`.

## Method and lineage

Created a new local clone because the assigned destination did not exist; both input clones were clean. Checked out B1, fetched the exact C1b object locally, then used `git -c rerere.enabled=false merge --squash --no-commit C1b`. Resolved 14 conflicted paths explicitly (UPSTREAM-CONFLICTS.md). One source commit, author/committer Tiramisu-Cake <igkharin@gmail.com> through `git -c`; no imported source history, CI-only commits, research files or new workflow overlay. Input refs/clones unchanged; no push.

The squash carries the final accepted tree delta, rather than replaying old B1 `cdb439b0a4`. Full original commit lineage, five-way per-file blob map, actual parent list and changed-path inventories are in INPUTS.json. Those source identities support later PR slicing; old receipts are not qualification of this candidate.

| Area | Final source relationship |
| --- | --- |
| Masks/storage/runtime, A3/M1/E2, raw_eq, closure layout, S3/CC/E1/M3 | Accepted C1b delta retained; unchanged paths checked by blob equality |
| AtomicStore | U #5115 arm retained beside accepted RawEq model; outside check-only group |
| Source MIR access | U #5152 retained; propagated `tcx` to shared resolver and imported immutable-origin collector |
| Registration/discarded closure overrides | Accepted body snapshots and provenance retained; checked source lookup is only the fallback |
| B1 unresolved calls | Single shared resolver/local diagnostic implementation; pending checks flushed through common epilogue |
| Fixtures | Union of B1 and C1b, no duplicate paths or obsolete shim fixture names |
| Upstream helpers/CI/JSON/dependencies | U exact blobs retained; three accepted JSON suites remain separate until S5 |

331 paths in old accepted delta; 131 upstream paths since old base; 50 B1 paths; 297 paths in candidate minus B1. Five old-delta/upstream overlaps are listed in INPUTS.json. Candidate minus C1b is upstream-only work plus four integrated production paths, six custom-MIR flag lines and two B1 generated-positive fixture pairs. No F5–F8 repair or SEL1 overlay.

Static identity audit: 139 accepted expected files unchanged; 84 upstream JSON/workflow/clause-helper/validator files match U; 47 files referring to heavy object-bits profiles match C1b. `mem_init.rs` matches C1b. Toolchain/CBMC/Kissat/submodule pins match U. Cargo.lock matches U; its difference from C1b is the pinned upstream serde-saphyr migration, not a new worker repin.

All compiler/runtime/test/CI results NOT_RUN.
