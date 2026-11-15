# Reusable extraction seam audit

Run `python3 check_seams.py --repo REPO --base PARENT --head SOURCE_SHA --reference F_SHA
--contracts CALL-CONTRACTS.json --out REPORT.json` (one actual shell line). Reads Git source only;
no compiler, formatter, build, network or verifier. Use explicit immutable revisions.

Run `python3 test_check_seams.py` for synthetic Python checks. Exit1 from the checker means a
structural/API finding. Missing files, malformed source or unsupported token structure raise an error;
never turn such a run into PASS. The old b0a5 head is an expected failing regression in slice02.

For each later slice, review every changed/removed declaration, every current impl/import and the
same-spelling consumer inventory; then bind affected APIs using contracts with id/path_regex/tokens,
explicit call arity and exact count. Count excludes receiver; path scope disambiguates common method
names. Use both current and ancestor call sites. Do not generate contracts blindly from a potentially
broken candidate. Compare required definitions/reexports/imports to this or an earlier slice and keep
one source-map owner. Extend the checks/tests when new syntax or seams need it. A PASS is bounded
static evidence plus the manual inventory review, never Rust compilation or semantic qualification.

The checker inventories ALL changed .rs paths, checks generic arguments in impl headers across all
compiler source files using changed-file type declarations, checks newly added signature/import
provenance against baseline/F, and checks explicit call contracts. It does not resolve symbols,
expand macros, check borrow/type/trait constraints or discover every dependency automatically.
Same-spelling references are navigation, not an AST binding claim. Import paths are compared as
leaves so approved pre-F7 mixed imports remain legal without importing the future API.

Current examples, reviewed contracts and exact-head reports: `../slice-02/COMPILE-SEAMS.md`,
CALL-CONTRACTS-01/02.json, SEAM-AUDIT-01/02.json. Native CI is still required.
