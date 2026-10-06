# Challenge 8: current checkpoint

Updated 2026-10-07. **IN PROGRESS — stock generic H_align, then narrow Rust ZST layout prototype.**
Owner resumes from e170656b7ff00e8de8ac9d5ebc949d2dbf3cfd75; entry clean,
local/remote research heads match, fork Tiramisu-Cake/verify-rust-std, no active run.
Budget: at most **6 NEW manual hosted runs / 10800 summed job-seconds** including
all builds, preparation and verification. Used 3/6; 125 completed job-seconds plus current job. One experiment at a time.

**Stock baseline PASS** in [run37540829027](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37540829027),
source968c073983e0fa27112c5d8a4e10a36b05828323, exact head_sha checked.
Both generic cases export/decode/VF/refinement exit0; source hashes unchanged,
72 verified statements per case, all four posts/leak paths and dead-code gate pass.
Two ZST positives INCONCLUSIVE (size0 / pointer limits); negatives2/2 intended
assertion failures, replay3 groups/30 mutants PASS. Job22:28:51–22:29:34Z,43s.
Full logs/artifact11447599817 inspected. **Proceed to separate layout prototype.**

Completed reachable ghost cases i<1, i<2, i<3, otherwise i==3 on unchanged
official VeriFast 26.09 / source809de459 / nightly-2026-02-05. Advance ONLY when
both generic const/mut have VF exit0 and all original integrity/refinement gates pass.
Keep stock ZST failures separate; no overall-green workflow requirement.

Prepared separate experimental-rust-fieldless-layout-v1 (NOT YET BUILT / RUN),
patch SHA256 fd37c158aecd1d383d32e1a7656fc9a1bc4f9d73504baf2f15a9f5714d79ee7a.
Prototype [run37542669720](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37542669720),
source/head f9697b8f3f894eb24115684a41da3d88566ddc9e, exact SHA checked, FAILURE.
Job112539146765,22:46:24–22:47:46Z on2026-10-06,82s. Console build fails translator
line6066: unary minus_big_int applied to two arguments. Exporter build and entire
experimental matrix NOT RUN. Full logs/artifact11449447487 inspected. Stock PASS
unchanged. Next: binary sub_big_int correction, NEW exact-SHA hosted run/30;
no semantic expansion or weakening.
Active NEW [run37543115091](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37543115091),
source/head55b856cd5285961e02323dd269044d2d194183d6, created22:50:41Z on2026-10-06,
exact pushed/head_sha match. Monitor this run; no duplicate.

Separate experimental layout profile limited to genuinely
fieldless, nongeneric-definition Sized Rust structs, repr(Rust)/repr(C), optional
repr(align). Compiler-backed optional size/ABIalign metadata with type/source/
target binding; Rust-only nonnegative struct-size bound. No exact facts for
fielded/generic/packed/transparent/enum/union/DST types, no offset/ownership/alias changes.
All executable checks/builds on GitHub-hosted only; stock profile kept unchanged.

[Phase and pre-implementation criteria](SORT4-ALIGNMENT-PHASE.md#stock-generic-and-fieldless-layout-prototype--2026-10-07).
[Prior checkpoint/history](STATUS-HISTORY-2026-10-07.md), [results](SORT4-ALIGNMENT-RESULTS.md),
[layout review](SORT4-ALIGNMENT-MODEL-BOUNDARY.md), [journal](EXPERIMENT-LOG.md).
RAPx CLOSED / NO-GO; B/C NOT RUN; ZST retained in target contract. Full sort4,
historical FnMut/Drop changes and external issues/PR/messages excluded.
