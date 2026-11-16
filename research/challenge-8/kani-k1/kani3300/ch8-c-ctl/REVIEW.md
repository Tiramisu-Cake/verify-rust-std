# Independent review — C controls

Reviewer: independent GPT-6 Luna, HIGH, separate context, no nested delegation.
Source packet created by `smallsort-session review create`; immutable identities:

- Candidate `56df5b34e4946ceddd231456737e9167a10d666a`, tree `2952c7b664cf04d79de31f865d185362f21f7e3a`.
- Spec SHA256 `cfba1ca4efdbb15b7bdc75f45a2d0bb2383bbf46c9df2b0e264fb08cabd60510`.
- Packet SHA256 `9f1070514d59d3f4f7e9d62e687c84604e494a45b9d38220eb6168766fac5dbc`.

Source decision: **no blocking correctness/design findings**, read-only static review.
No source edit requested. The reviewer checked all eight roots against the design
and verified the production helper dependency and its dst-only merge frame.

N1: both actual merge callbacks pass source slot1 as `a`; volatile write/restore
uses initialized values and live-reference read; lawful order and disjoint MU dst.
N2: one fixed reversed-pair comparison; raw tail alias predates the reborrow;
PFC write set is exactly v; read-only companion differs only by writes.
L3: separate input/counter allocations; explicit mutable and UnsafeCell targets,
real inner helper execution and reached mutation/output sites.
L4: real first insertion, local tmp comparison after gap shift at tail2,
copy-back and subsequent tail3 iteration; scoped borrow ends before storage reuse.

Review does not establish generated property binding, retained writes, cover
reachability or proof results. All roots are **NOT_RUN**, credit **NONE**.

## Connected CI review and corrections

Initial CI candidate `044b6b0c4ca0247005eacef495f961e64c820405`, tree
`cc24233cd7c31200922c6acf0ce0ee7a8df8d56f`.
Spec SHA256 `c470a2784fb7a63f6368c5b5665f9727cfebacbe78626429f60f71babe28277b`;
packet SHA256 `af11d82e812b60e5ce7911cd07091ef6ecc5a378285271a77a2a84788b608261`.
The same independent reviewer checked the frozen CI diff and tool schema/setup
source dependencies, and ran the 16 offline Python synthetic tests successfully.

Findings returned to the original worker:

1. Blocking coverage accounting: `covers.total` could disagree with the satisfied-ID
   count while `n_properties` was adjusted consistently. Enforce exact accounting,
   unique string IDs and a strict numeric count, with malformed-export tests.
2. Remove the extra `reviewdog/action-actionlint` step whose default workspace root
   differs from the nested control checkout. Retain local static actionlint against
   the explicit workflow path, as required by this preparation stage.

Other reviewed CI properties were aligned: exact source/tool/tree/clean sibling
checks, list/export/expected target binding, exact assigns-class/source-write
negative matching, exit-aware ALIAS_GAP, bounded process-group execution and output,
NOT_RUN tail/fallback, production-only source, attempt1 and host gates.

First correction candidate `e664f9a1912ab1079f767d6c7d848c1e533dfe22`, tree
`250f0c0dbbab4d6b66c6aa22a439a9017d076a2c`, resolved both original findings.
The reviewer confirmed exact coverage accounting/unique string IDs and removal of
the extra action. Its 17 synthetic tests and static checks passed.

The follow-up identified the remaining same-class wrong-type hole: Python treats
booleans as integers, so `checks.total=true`, `checks.success=true` and
`n_failed=false` could pass equality/arithmetic. The worker was asked to enforce
strict nonnegative integer types on all five exported property/check/cover counts,
and strict numeric types for matched-count/unwind identity, with boolean/negative
synthetic cases. Original exits, UNKNOWN and NOT_RUN behavior must remain intact.

The review helper requires baseline ancestry. Amended controls are siblings with
the same required tool parent; corrected full packets therefore use the tool
baseline, with exact old-to-new supplemental diffs for bounded follow-up review.
No merge/child control commit was introduced to satisfy the review helper.

## Final preparation decision — ACCEPTED

Final control `7a4f8086e6989dbae10a49b26e83feea8ad34193`, tree
`2ed1a5a98f5009265405b6a5b52b652aea9e8365`, sole parent upstream tool
`0aac16ef62da9e9d5645782d458593e5d78143ba`.
Final packet SHA256 `5f0f019b97e5c2c578ff8ead89ee6f4af000b8b1913e840e4ce716c31d98ccfa`;
spec SHA256 `2b409dd1ba7808c2093cf68dffebe1e3219a140d36bb2a22dbe6bfc5b466939b`;
final numeric delta SHA256 `e28d4f37386edfd7e8fdbe4808c6d2d793914fa0dfa6b0f6e017df8499b76647`.

The same independent reviewer accepted the bounded fixes, confirmed all five
counts reject booleans/negative values and selector/unwind reject invalid numeric
types, and reran the offline synthetic suite: **18/18 PASS**. Exact coverage
accounting and unique string IDs remain enforced; the extra runtime action is gone.
No remaining blocking finding in the reviewed preparation scope. Source remains
`56df5b34e4946ceddd231456737e9167a10d666a`, unchanged since source acceptance.

Acceptance is for source + CI-only preparation. All actual proof roots remain
**NOT_RUN**, with **NONE** proof credit. Generated frame/wrapper/write/cover binding
and named successful assertions still need actual CI evidence and runtime review.
The `[skip ci]` upload commits suppress activation; the handoff specifies a later,
separately authorized same-tree sibling on a fresh activation branch, preserving
the required sole tool parent. No dispatch authority is conferred by this review.
