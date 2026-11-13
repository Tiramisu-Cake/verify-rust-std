# X1 review and local checks

Candidate `c9d3b2c17afe02ceabce73692279a797c54ddd69`, tree `b9d991ff795f35924272e448d819fb424fcda254`, base `94c00a8859bc9e4f0f1b7db73a95dbee88f6213a`.

Python-only checks passed:

- `python3 tests/json-handler/uninit-contract-oracles/test_checker.py`: 21 tests, OK.
- `python3 tests/json-handler/uninit-contract-mode-boundaries/test_observe.py`: 18 tests, OK.
- `git diff --check`: PASS.
- `ast.parse` for all Python modules in both suites: PASS.
- Structural JSON comparison against the base after removing only the named
  historical/redundant metadata fields: all eight cases and six roots otherwise identical.
- AST comparison: `validate` is identical after deleting only the old historical
  evidence-presence statement; every actual invocation/property predicate remains.
- CC5 `observe.py`: byte-identical to base.
- Write-scope check: only assigned suites and deletion of the two internal docs;
  no Rust body, compiler/runtime/schema/shared test infrastructure changed.
- Historical handoff copies: exact byte equality to the base; hashes in INPUTS.

Runner tests mock subprocess boundaries only; no verifier/driver/compiler is
invoked. They exercise success/error/timeout/partial/missing/null/wrong-type,
wrong source/root, original exits, downstream NOT_RUN, cleanup on success/failure/
exception, exact consequence handling and generated/original CC5 cover grouping.
`test.sh`, actual Kani, Quick/full gate and SmallSort replay are NOT_RUN.

Independent review: bounded Luna HIGH reviewer `x1_review` examined committed
candidate `c9d3b2c17afe02ceabce73692279a797c54ddd69` and the separate research
handoff. No remaining concrete X1 regression or oracle weakening was found.
The initial finding that historical copies were absent from the Kani export
was closed after the reviewer inspected the intended separate research tree:
all six handoff docs exist, both historical files are exact base copies, and
the provenance manifest source hash matches the base manifest. The reviewer
also confirmed that CI-only capture is a future coordinator responsibility,
not a missing source-tree X1 overlay. Python tests independently rerun: 21+18
PASS; diff check PASS. Review is static/synthetic only, not actual Kani evidence.
No semantic/model qualification or independent B1/B2 proof credit is claimed.
