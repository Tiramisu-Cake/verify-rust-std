# R9 candidate 6 independent review — GO for checked owner-list replacement

Reviewed the source-only candidate-6 delta. The prior current-owner constructor
is split into three checked lemmas. `r9_drop_u64_owners` opens the old
`foreach`, then opens each generic `own::<u64>` and concrete `u64_own` before
recursing; `r9_make_u64_owners` constructs the new list through the existing
concrete-u64 close sequence; `r9_current_u64_owners` requires an old owner list
and returns the list for the newly observed current values by composing those
two lemmas. The pinned model defines `u64_own` as `true` and
`<u64>.own = u64_own`, so this explicitly consumes only the logical, resource-
free u64 ownership interpretation. The source does not discard a heap chunk or
claim a generic ownership transformation. The array/current values still come
from the checked physical rejoin.

No translator, profile, kernel, model, physical-array, F, or unwind change is
in this candidate. The exact source block remains ordinary checked ghost code;
the actual verifier must reject it if the expected old foreach resource is not
present or any close/rejoin obligation fails.

Validation: `r9-marker-service-test.py` passed, all 10
`r9-guard-return-controls-service-test.py` tests passed, and `git diff --check`
passed for the changed source/test files. This review did not run a compiler,
preparation, proof, or Cloud Build. **GO for the bounded source candidate
only.** No proof credit is granted; hosted verification remains required.
