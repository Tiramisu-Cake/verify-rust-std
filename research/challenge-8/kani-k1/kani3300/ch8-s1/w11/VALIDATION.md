# Validation and limits

Local Git/source checks PASS: exact std/Kani object/tree identities, std base and
source parent, allowed two-file source diff, clean worker11 source worktree,
source diff --check, source commit [skip ci] and author/committer identity. No
smallsort.rs/verify.rs/lib/Cargo/tool config or foreign files changed by worker11.

`python3 check_model.py` PASS (synthetic-result.json):7225 pairs of sequences over
{0,1,2,255} for N0..3, compared to independent Counter/order oracle; all32640
strict byte pairs with legal/order/count cases; lengths0/1/2/3/16/31/32/33,
invalid/changed-length/overflow rejection, owned mutable pre-state, read-free
inactive sentinel, static exact-three-pair/default-path/facade checks,12 roots.
These are Python mathematical/source sanity checks, NOT Rust/Kani qualification.
The manifest is checked against root names and source assertion/cover strings.

Independent read-only Luna HIGH review: GO_WITH_NITS on exact source3f469d3ba2,
packet/spec identities in REVIEW.json. No found soundness blocker. Documentation
nit (auto-trait/!Copy expectations) is covered in TYPE-REVIEW/MODEL-SCOPE without
changing reviewed source. Packet check verifies inventory integrity, not review
or proof credit by itself. Reviewer did not compile or run a verifier.

Rust compilation: NOT_RUN. rustfmt: NOT_RUN. Kani/CBMC/Miri: NOT_RUN.
Actual trait/PFC/ensures attachment, fn ABI/min_specialization core acceptance,
compiler-listed selector and property counts, covers: NOT_RUN. No actual-sorts
proof, full threshold/body theorem, extra-UB/Replace qualification or P1 acceptance.
Cloud spend $0; fork dispatch0. No push, remote publication or external messages.
W11↔13/14/15 messages were internal coordination under the explicit task interface.

Worker13 must integrate this source, add minimal feature/cfg/module registration,
and bind all12 model rows plus six actual PFC, attachment controls and bridge to
one exact combined export/tool/flags manifest. Coordinator alone handles fork
CI and subsequent P1 acceptance. Incomplete or unsupported evidence remains
UNKNOWN/NOT_RUN; do not bypass source blockers or loosen enabled/post.
