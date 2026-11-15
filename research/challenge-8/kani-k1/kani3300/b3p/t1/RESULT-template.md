# B3 T1 result — template, NOT RUN

- Exact Kani CI SHA / research SHA / run URL / attempt / runner image: TODO.
- Source A / B / A and submodule identities verified: TODO.
- Job duration/cap, original build/Kani/compiletest/shim exits: TODO.
- Complete 15-row harness census (attach per-name inventories): TODO.
- Cargo.lock paths, saved bytes/hashes, offline and zero drift: TODO.
- rustc/driver/compiler/backend paths/hashes/versions: TODO.
- A1/A2 named-model/metadata/argv equality: TODO.
- Positive control A1=A2≠B1 and exact wrapper payload replacement confirmed by
  symbol/function diffs, reviewer/evidence references: TODO.
- Comparison files: `compare/RESULT.json`, symbol/function dumps/diffs: TODO.

Until the positive-control structural gate is confirmed, status is
CONTROL_WRAPPER_REVIEW_REQUIRED. No detected control difference means
INVALID_CONTROL. Any change outside the expected control wrapper invalidates T1.

Choose exactly the supported outcome after checking completeness and identities:

1. **A1=A2=B1 for perf, valid control:** «Различий моделей указанного perf-профиля
   не обнаружено». This covers the captured final CBMC inputs and argv with pinned
   backends; it does not promise absence of resource regressions or explain runner loss.
2. **A1=A2≠B1, perf changes only in zero-width wrappers:** attach the complete
   symbol/harness census. Do not call these harmless: they change byte-operation
   handling. Coordinator decides the next step and PR readiness.
3. **Perf changes outside wrappers:** auditor §3 analysis is wrong; do not submit
   the PR. Attach symbol/function diffs and request the next bounded investigation.
4. **A1≠A2:** postpone all B3 conclusions; classify file-name, provenance, symbol
   and function differences. No normalizer exists in this candidate. Any later
   normalization must explain every nonsemantic field, produce zero A/A
   differences and retain positive-control sensitivity.
5. **Missing/partial/error/timeout/tool or lock drift:** INCOMPLETE/INVALID, exact
   failed stage/exit and preserved evidence. Do not equate missing text with NOT_RUN.

SAT is explicitly NOT_RUN at each successfully captured shim invocation. No
verification verdict, independent B1/B2 proof, performance result or resource
regression credit is claimed by this comparison.
