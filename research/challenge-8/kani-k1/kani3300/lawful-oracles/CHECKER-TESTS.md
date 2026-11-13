# Python/static checks

Source: `/root/kani-fix-3300-lawful-oracles`, commit
`0beeb6b79efb72b88035e2b747aa889e9b1cb4d4`.
Executed: `python3 tests/json-handler/uninit-contract-oracles/test_checker.py`.
Result: 15 unittest methods PASS (including parameterized adversarial subcases).
Fixtures are explicitly synthetic documents/regular records, never Kani results.
All subprocess boundaries in the scenario tests were mocked: no compiler ran.

| Tested boundary | Required result |
| --- | --- |
| Eight synthetic completed bound selections | All accepted by the structural checker |
| The same eight with shipped pending bindings | UNKNOWN, never qualified |
| Extra FAIL / one of two checks missing, with counters and regular inventory consistently updated | Rejected by exact inventory, including independent postcondition-hole |
| Duplicate/missing root, zero/wrong selection, same root in wrong input, wrong harness line | Rejected |
| Swapped frame *outside/var_7 → shadow/var_8 in both outputs | Rejected; no wildcard normalization |
| Changed failure class/type/source line/file or required success function | Rejected |
| Extra reached Unsupported, duplicate property IDs, overlapping buckets | Rejected |
| n_properties/checks/success/summary mismatch, null count, UNKNOWN status | Rejected |
| Useful positive assertion UNREACHABLE | Rejected |
| Unrelated UNREACHABLE service/Unsupported branch | Accepted with consistent inventory |
| Missing/truncated/duplicate-key JSON, stale timestamp, PARTIAL/INCOMPLETE, null/wrong-type export | Rejected; original process receipt retained |
| Signal -15, exits2/124/137, false success0, missing exit, timeout, codegen/process errors | Rejected, no negative PASS from nonzero alone |
| Tampered retained export hash | Rejected on offline recheck |
| Lawful root reached versus unreachable Unsupported | STOP distinction preserved |
| Command construction | Existing exact source/root, jobs1, required four -Z features, all flags before final b12 backend args |

Also PASS: Python AST parsing; eight-case input hashes/root lines;
comment-stripped lawful body equality to fe36afc4; Bash `-n`; staged diff whitespace
and allowed path/process-boundary checks. The unchanged schema validator was used.
Rustfmt is absent in this environment: scratchpad fmt NOT_RUN, no installation.
Compiler/fmt/build/Kani/CBMC/Miri/semantic CI remain NOT_RUN. These tests validate
the consumer and error handling; they do not replace any actual semantic gate.
