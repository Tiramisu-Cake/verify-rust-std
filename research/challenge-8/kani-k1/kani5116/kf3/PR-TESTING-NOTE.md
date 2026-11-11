# Proposed PR Testing section

### Testing

- Final revision: fork CI pending — `<run, SHA>`. This run should execute the updated specialization tests and the existing free-function, trait, generic, and contract regressions.
- Static checks passed: rustfmt with the repository configuration, whitespace checks, and copyright/SPDX headers. The production changes match the reviewed auditor patch exactly.
- Historical validation: targeted native compiletest on Linux at `f046b70644`, with the previous revision of the patch, matched the expected outcomes for 19 selectors (nine new fixtures and ten existing regressions). For negative tests, PASS means the expected diagnostic matched. These results precede the final AST refactor, `--no-assert-contracts` flag, and additional stub harness.

# Corrections to the auditor's draft

- Its fork CI run 42922309733 and macOS observations describe the previous `2a3e2ae` revision. Replace the Testing section with the final run and SHA after coordinator CI; do not attribute that older run to the final revision.
- Replace “A targeted local run” with “targeted native compiletest on Linux”, pin `f046b70644`, and identify the previous patch revision and negative PASS meaning as above.
- The final clauses fixture contains both `stub_requires_first` and `stub_modifies_first`. Both-order stub harnesses have been added; execution is pending. Any statement that both passed must wait for final CI.
- The opening production explanation remains accurate with direct `syn::ImplItemFn`. The body/test overview can remain, subject to the pending execution qualification above.
- Keep the shortened description, disclosure, and license statement from the auditor draft. Keep the verify-rust-std paragraph omitted; the early patch/N2 results do not validate this candidate.
