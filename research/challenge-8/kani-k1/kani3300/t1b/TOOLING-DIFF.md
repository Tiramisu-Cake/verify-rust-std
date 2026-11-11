# KANI3300 T1b — bounded tooling extension
KT2 `3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c` + tooling `c3468b3bd84f4a91a2ea99fa0fcea317bd98e681`, tree `6446f4d16bf0dad3a7e38a00347835b986694e66`.
Extension patch SHA256 `55aeeefe592b87f46059db08c5abfb5578a58be0b3c644dda764dfecf7361de0`; exact files/recipe hashes in TOOLING-BINDING.json and TOOLING-FILES.json.
Changed kani_k1.py/gcb-k1.sh/k1g.sh; new diagnostic_trace.py/test_diagnostic_trace.py; recipe and protected pins unchanged.
Request diagnostic_trace requires literal filters, library_tree, base_pin, expected_applied_tree; diagnostic/standard4/patched only.
Filters: <=20 items, <=300B/item, <=900B total; strict character/type/uniqueness checks; no arbitrary shell/eval.
trace-env writes only validated KANI3300_TRACE_* assignments; ambient diagnostic env is removed when request opts out.
Runner records structured invocation after exports, including actual cwd/argv and relevant inherited RUSTFLAGS; capture errors nonfatal.
Low-level compiler/rustc/CBMC argv UNKNOWN, never reconstructed as observed facts.
Sidecars attach only summary.json.diagnostic_trace, independently of original Kani status/exit/checks/gate.
Identity binds outer summary/build/head/request, actual library tree/base/applied tree, filter/stage/schema, tooling and argv/env digests.
Collector checks 512 records/256KiB per sidecar, 2048B records,1MiB aggregate before accumulation; bad/missing/partial/overflow explicit.
Root/stage/unit context is validated and preserved; bounded sidecar filename/bytes/SHA256 identities bind exact captured content.
Header/footer sequence/counts/byte bounds and COMPLETE coverage validated; emitted events and payload omissions remain distinct.
k1g.sh trace-field BUILD records 0 20 uses only cached/fetched summaries, never native tests or raw artifacts.
Dotted object paths: identity, state, coverage, errors, omitted, sidecars; arrays page by start/count. Follow only returned next_start.
Pages <=20 records/12000B; trace_complete, page complete/omitted, next_start and identity always explicit; inconsistent bindings rejected.
Existing summary/native/native-field and original verdict/exits/checks remain unchanged.
Independent review: REVIEW-TOOLING.md; all blocking findings repaired, final PASS.
Tests: python3 -I test_kani_k1.py equivalent unittest discovery:96 PASS; test_gcb_native.py:9 PASS.
Tests: python3 -I test_diagnostic_trace.py:11 PASS (main rerun after fixes); shell syntax and git diff --check PASS.
Service tests exercise actual mocked gcb verify/summarize and cached k1g; invalid env, inherited env, opt-out, missing/oversized/partial/timeout/null/type/identity/cap/coverage errors.
No real compiler, verifier, Cloud or credential access; all subprocess proof/Cloud service commands are mocks.
