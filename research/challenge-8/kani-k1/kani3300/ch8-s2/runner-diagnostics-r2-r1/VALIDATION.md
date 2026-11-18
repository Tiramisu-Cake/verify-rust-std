# Localized offline repair validation

Exact control `472be8c3794d7a4530760ab7d5eae4ce950aa01c` / tree `4835c615d20e6606ddcdc64bbb8314973cec141b` / parent `9e14e033f9ee31522b571c127609dcdff76d230b`.
Final localized selection: **32/32 PASS** (FINAL-32-TESTS.txt), exact unittest
recipe in FINAL-TEST-COMMAND.py, executed from the candidate ch8-s1-control cwd.
The original preview snapshot test also passed **1/1 in isolation**
(PREVIEW-ISOLATED-RECHECK.txt). This is author static/synthetic evidence only.

The full 33-test attempt had one failure in the existing preview snapshot test
(EXPANDED-ATTEMPT.txt): the compile receipt's stderr head was empty at the marker
snapshot. The same test passed separately, and an earlier combined selection
passed 33/33 before a final test-assertion clarification with identical runtime
repair code (INITIAL-33-TESTS.txt). `runner.py` and this existing test are byte
identical to b678. Its asynchronous marker/pipe timing is a separate observation
returned to the coordinator, not repaired or hidden here. No workflow/test gate
was weakened; the workflow still runs its original complete preflight selection.

B-01: exact s2-batch3probes-u34 fallback with successful setup/main absent;
removal of BOTH main stream receipts; selected terminal inventory with a wholly
absent group; explicit NOT_RUN/IN_PROGRESS/INTERRUPTED states. Tests assert global
incompleteness, expected directories and reasons, preserving source receipts,
native exit42, UNKNOWN and proof NONE.

B-02: review's exact 165-byte suggestion fixture retains all165 bytes on stdout
and stderr, including N-minus/N-plus and following context. ANSI/one-byte split
variants preserve raw byte coordinates, UTF-8, note/help context and exact packed
text. No cap increase. Original long-middle/error/cap/fallback/native exit tests
also pass in the final32 selection.

The four new tests give **10 expected assertion failures, zero errors**, against
the frozen b678 implementation (BASELINE-NEGATIVE-REGRESSIONS.json). Original
review counterexamples were rerun unchanged (BEFORE-REPRODUCTIONS.json).
`python reproduce_repairs.py` demonstrates repaired outcomes plus unchanged old
baseline/new-reader long-middle behavior (AFTER-REPRODUCTIONS.json). This author
adaptation does not close independent findings.

`python validate_package.py` passes exact clean identities, old-to-new hashes,
request invariants, source/PFC checks, offline control preflight, and three exact
patch-tree replays (PACKAGE-CHECK.json). It submits no work. Only the payload hash
map changes in the request; source/tool/cfg/argv/caps/11roots/20covers/6negative
oracles/proof outcomes remain fixed. Production retention NOT_RUN; historical
compile cause UNKNOWN; no proof/accounting change.
