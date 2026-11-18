# Static validation

Run `python3 validate.py /root/kani-f4-uninit-only-w15` from this directory.
Result: PASS, assurance STATIC_AND_SYNTHETIC_ONLY; details in VALIDATION.json.
The module entry point is exercised only with subprocess.run mocked to synthetic
fixtures. Native compiler, Kani, Cargo, CBMC and full runner are never invoked.

Checks include Python AST and shell syntax; immutable observed-main rejection;
two-mode synthetic oracle and parser rejection cases; poisoned-environment
argument separation; narrow compiler byte invariants; direct parent, exact scope,
clean source; all 16 unchanged workflow hashes; and isolated-index replay of both
patches to the exact candidate tree. regression-main.patch is a test-only replay
on frozen main, independent of the full compiler fix.

Compiler build, rustfmt, native two-mode runtime, new main-vs-fix execution and
performance: NOT_RUN. Review14: PENDING. Old b5 CI is historical only. No proof
credit or local archive verification is established.

Source diff whitespace checks pass. Package prose/code whitespace checks exclude
canonical .patch artifacts: unified-diff blank context lines carry the required
space marker, and their bytes/hashes remain unchanged for exact replay.
