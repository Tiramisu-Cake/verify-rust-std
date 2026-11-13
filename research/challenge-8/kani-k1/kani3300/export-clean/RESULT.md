# KANI3300 X1 result — prepared

Source `c9d3b2c17afe02ceabce73692279a797c54ddd69`; tree `b9d991ff795f35924272e448d819fb424fcda254`;
base `94c00a8859bc9e4f0f1b7db73a95dbee88f6213a`; branch `fix/kani-3300-x1`.

Export cleanup complete in the assigned suites/docs. Historical documents and
attestations are preserved with provenance in research. Before/after map and
retained invariants are in EXPORT-FILE-MAP and ORACLE-INVARIANTS. Local Python
checks: 21 oracle tests + 18 mode tests PASS; static/source-scope checks PASS.
Independent Luna HIGH review found no remaining concrete X1 regression; the
provenance finding was closed by inspecting the separate research copies.
Source checkout is clean after the source commit.

Actual Kani/CBMC/compiler, both JSON suites against Kani, Quick/full regression,
M3/mixed composition and SmallSort replay: NOT_RUN. Cloud $0, push/CI/publication0.
No new proof credit; marker diagnostics remain DEFERRED. No work from later
unissued stages or W14's files was performed. Coordinator owns integration,
publication and future CI as described in CI-REQUEST.

Research pull limitation: configured remote branch was not fetched; original
local research HEAD still matches issued df5501c9f0. No alternative ref was used.
