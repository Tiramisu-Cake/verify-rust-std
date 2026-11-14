# S5 review

Scope is tests only: eight strengthened/split strong fixtures, seven mode fixtures
(six old roots plus false-partition Replace return companion), seven composition fixtures,
and planned deletion of exactly three mapped JSON suites. Compiler/runtime semantics,
pins, driver/schema/matcher/validator/upstream JSON suites and S4 units remain unchanged.

The 21 old case/root rows are closed in ORACLE-MAP.json before deletion. Supplied
exact-base run43630584079 fixes strong-hole N=3 and Replace N=2; current S4 summaries
supply composition counts. New portable inputs/goldens are source-reviewed predictions,
not newly executed observations. False-partition companion (original nondet bool + assume(!initialized), parent unchanged) N=0 follows short-circuiting of
requires/ensures/post-return predicate without reading havoc MU payload; it retains the
same input/relay/helper/Replace route. Its own reached assertion and SATISFIED cover
are required. General Replace/recursive support is not claimed.

Literal matcher audit (verify_output/contains_lines/contains) confirms literal substring
search, no regex or extra-output exclusion, duplicate patterns do not count repeats.
All22 fixtures pin one-harness start/completion, anchored SUMMARY + ** N of and verdict.
Every intended failure has a typed/own prefix+Status+Description block and Failed Checks;
useful body/ensures/root/allowed-write and required SATISFIED covers have chained blocks.
Negative source/helpers contain no covers; only pure true hooks were removed. Frame
roles use own function-prefix, exact description and original-source coordinates rather
than closure-number pins; the permitted write's SUCCESS cannot be replaced by a
private check. No std path/line/toolchain/host/full snapshot pins or blessing are added.

Independent Luna High static review completed at predeletion staged tree
58167147970932ac6e47a038281d99968a046af6. See INDEPENDENT-REVIEW.md. Its copied row-text finding was fixed with row-specific preservation/structured golden blocks and verified for all22 inputs (zero discrepancies). The false-partition wording/hash refresh is complete; current inventory hashes match source. No static source issue blocks the planned deletion. Native execution remains CI-required.
Deletion follows this completed transfer review.

Mixed-isolation acceptance item: per-root expected does not express isolated↔mixed
inventory equality, selector-order behavior or full export schema. We deliberately
remove that exported end-to-end regression with the suite; residual regression coverage
decreases. Unchanged reviewed F7 implementation plus compiler delayed_cache6/scope2 units
and source-reported S4 baseline6/18 mismatch versus candidate18/18 EXACT_MATCH remain
the basis. Research hashes/identities are preserved. No observed producer order or full
semantic equivalence of test formats is claimed. Coordinator must assess this stated
tradeoff, not treat separate legal/cycle successes as mixed isolation proof.

Four sensitivity overlays remain outside export, with independent patch/SHA/selector
manifest and observed native results NOT_RUN. The extra-failure mutant uses nondeterminism,
so a continuing branch retains the original outside-write failure. Positive assertion
removal, negative extra failure, negative repair and count inversion require actual
native compiletest in coordinator CI; a Python model is not used as sensitivity evidence.
Source static checks, wrapper formatting and git diff --check are the local validation.
No builds, compiler/verifier runs, native compiletest, push or CI dispatch.

Final source 6d2e9ae621310605eda4b0c9572d34d9a7ff948d, tree 6a8f2b2e11780445451640eaba8b6a7076686896. Only planned three-suite deletions followed the reviewed predeletion tree; static scope/deletion-set checks PASS. Metadata hashes refreshed. Source-full.patch reconstructs exact tree in an isolated Git index. Native CI remains NOT_RUN.
