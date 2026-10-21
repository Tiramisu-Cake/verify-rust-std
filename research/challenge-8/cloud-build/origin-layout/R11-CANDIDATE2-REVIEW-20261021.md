# R11 candidate2 independent review

Independent existing GPT-6 Luna HIGH reviewer r10_review, no nested delegation, reviewed candidate2 tool diff relative a3a22f98 plus current-native provenance controls, parent receipts and fullbody wiring on 2026-10-21. Verdict GO: no admission bypass or call/CFG/storage-check change found; exact source/native/AST binding, retained markers/edges, hidden unit local and no-use checks fail closed. Static OCaml APIs/types appeared consistent; actual compilation was not run. Interior checked cut preserves loop consume/produce checking; no synthetic true head is added.

Reviewer earlier NO-GO stale MIR route was corrected by parent exporter/decode receipt creation with current tuple/output digest/size and unchanged decode-input digest. Re-review found no remaining false-match route. Missing native receipts refuse; original validation tuple is supplied only transiently to exact R11 fullbody and restored on error. Recipe includes six native receipt service tests and nine controls tests.

Main found integration details after localized review: replay needs scoped R11 execution/R9 recovery flags; Cut uses inv_at field; wrong-dead mutation must choose canonical declared _0 among many locals. Worker corrected these and tested. Final small tool tightening also scans switch-clause pattern expressions for hidden local references. Reviewer notified before submit.

Limits: source-named ordinary-local and address-taking executable negatives remain OPEN/NOT_RUN, never credited in all_matched. Synthetic/static GO is not verifier acceptance. All controls remain diagnostic accepted=false/proof_credit=false; B2/generic/qualification OPEN.

Final localized parser re-review: LunaHIGH GO after exclusive inv_at precedence plus wrong-inv_at/matching-line negative test. Current service tests: trace9, placement10, native receipt6 PASS; registration5 and full static closure PASS. Tool commit ab4f72b86d8c427381cfc7e2b9190cfb4ffd35e8.
