# S4 distinguishing baseline and candidate

Baseline base: `ad324418cdc66b18e9b71f76a412be6ccea20c7e`, exact original tree
`b7e9e8ffa7212c1c41299c32ebd0b72fd9951a68`.
Apply only baseline-tests.patch; expected tree `6bed3373b8c2c62f103c2f3c8ecd99d5a90db95a`.
BASELINE-PACKAGE.json pins patch hash and every changed blob. Application was
checked through an isolated temporary Git index; no baseline commit or branch
was made. All changes are in tests/json-handler/uninit-part1-composition; zero
compiler/runtime changes. The candidate has identical observer/test blobs.
Unchanged mixed.rs SHA256 is
9aa067f674e9cd27b7b4822795208ff4ca940554e65b6ffe32c316cb0b6e7970.

No synthetic Rust source replaces the real reads. Existing initialized immutable,
ordinary ensures, actual-hole negative, PFC/cycle, and unrelated legal roots
are retained. The narrow observer change skips stale golden binding checks
only for explicit --collect-unbound, while preserving source/hash, root/mode,
configuration, verdict, complete JSON/regular cross-checks, and process guards.
Capture always exits 2 / UNBOUND_CAPTURE, with NOT_CHECKED_CAPTURE.
Ordinary bound regression still validates old bindings and may FAIL.

Predicted distinction, NOT_RUN: baseline shared regular cache accumulates delayed
operations; at least one mixed root has additional checks over its own isolated
inventory. Candidate moves first pre-delayed results into a journal and restores
after model emission, so every root has exact isolated/mixed inventories.
No false UB failure is required on baseline: legal SUCCESS with extra successful
checks is the intended discriminator. Historical R4 counts are not this evidence.

Compare inside each tool, with fresh isolated captures. Then cross-check each
candidate isolated root against the same baseline isolated root to catch lost
checks/status/payload changes. Candidate mixed may lose only the baseline's
independently mapped duplicate delayed instrumentation; it must exactly equal
candidate isolation. Do not compare with or bless old C1b serialized inventories.
If baseline is exact, incomplete, different-unit, unreached, or blocked by an
unrelated guard, report NONDISCRIMINATING/UNREPRODUCED and return a bounded revised
request; current source reasoning does not establish actual accumulation.

Source/CLI permutations are regression coverage only. Actual producer order is
NOT_ESTABLISHED until an actual bounded receipt is supplied. Structural scope
is independent of that order; no empirical AB/BA claim is made.
