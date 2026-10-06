# Challenge 8: current checkpoint

Updated 2026-10-07. **IN PROGRESS — stock generic H_align, then narrow Rust ZST layout prototype.**
Owner resumes from e170656b7ff00e8de8ac9d5ebc949d2dbf3cfd75; entry clean,
local/remote research heads match, fork Tiramisu-Cake/verify-rust-std, no active run.
Budget: at most **6 NEW manual hosted runs / 10800 summed job-seconds** including
all builds, preparation and verification. Used 3/6; 235/10800 summed job-seconds. One experiment at a time.

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

Experimental-rust-fieldless-layout-v1 has not yet reached executable matrix.
Prototype runs37542669720/f9697b8 and37543115091/55b856c fail console build:
unary subtraction corrected, then unqualified RustLayout constructor.
Latest job112540598709,22:50:46–22:52:36Z,110s; full logs/artifact11449258539
inspected. Exporter build and experimental matrix NOT RUN in both runs.
Next candidate qualifies Ast.RustLayout only, patch SHA256
bb31a6e119a19aee2fee66b3afd07df412b54ceb991e34c672b783b8446b6a9b.
No active run. Next permitted action: NEW exact-SHA experimental selection/30.

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
