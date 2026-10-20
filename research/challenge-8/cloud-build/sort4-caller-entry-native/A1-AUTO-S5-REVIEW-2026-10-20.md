# A1 Autonomous S5 independent review — 2026-10-20

**Decision: GO for the bounded S5 Cloud submission after exact committed-closure verification and coordinator live preflight.** This approves the narrow translator representation repair only. It does not claim that the source mismatch is resolved or grant proof credit.

## Review finding

Reviewed `required-item-representation-hir-partition-r2-2026-10-20.patch`, the matching required-HIR inventory validation and synthetic controls, the S5 source-check/profile, and the active profile consumers.

The new `a1_required_hir_method_params` helper validates every HIR parameter before returning only early type parameters. It rejects late type parameters/interleaving, non-plain early names, const/unsupported kinds, non-Fresh late lifetime names, invalid or reused Fresh IDs, `pureWrtDrop`, and dummy spans; it checks late lifetime count against the independently validated signature region count. The pinned schema defines HIR parameter bounds as `Void`, so this representation cannot carry non-void bounds. The existing compiler-own-generics comparison then checks the returned early type list, and the existing small_sort gate requires exactly the method type parameter `F`.

Both HIR-consuming sites now use the partitioned list: clause/type validation and `A1RequiredInterface`/AST construction. `method_params`, F-clause checks, type names, interface registration, and AST parameter order therefore contain early type generics only. Semantic outer lifetimes still come once from the validated `FnSig` lifetime rows and typed input references; clause binders still use their separately validated scoped rows. The patch does not equate Fresh LocalDefIndex words with scoped signature aliases, which the current schema does not link. I found no change to signature, binder, clause, source, admission, native-envelope, normal/unwind, or proof-post criteria.

S5 source-check records a full source-only reconstruction from the pinned pre-R base and patch chain, application of the complete new R2 patch, and application of unchanged C. The translator is the only changed R/C source; exporter and schema pins remain unchanged. Profile helper/entry/runner/source-check hashes match. All active consumers and the sorted recipe select S5/R2. Window, owner, build budget, timeout, lane and sequential-build controls remain unchanged.

## Controls and limits

The required-HIR partition suite was reported by its worker as **7 PASS**, including empty threshold HIR, valid Fresh metadata renaming, malformed ordering/count/kind/identity/flags/span rejection, and preserved signature/FnMut checks. Inventory **24 PASS**, admission **23 PASS**, and profile-gate **5 PASS** were also reported. I reviewed the test source and hash, but did not run tests independently. `git diff --check` is clean.

No local compiler, exporter extraction, decoder, MIR replay, full runner, Cloud evidence, or raw logs were inspected. Cloud must compile the translator and determine whether this repair advances the focused P0a/P1 path; later proof and full-matrix obligations remain unchanged. The profile keeps all target rows, including `N-false31`, NOT_RUN and `proof_credit` false.
