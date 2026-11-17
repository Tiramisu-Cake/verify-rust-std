# Bounded repair and preserved base7c delta

New control e27ec119eeac798d43d6bc056a449fa7576a5e94 is a sibling of old da8 over
9208, not an amendment or descendant. Old da8/9f/review ec48 and source99e/base7c
remain immutable. The exact reviewed OPEN finding is W14-CELL-RETRY-01 (P2).

REPAIR-DELTA.patch / REPAIR-DIFF.json describe only the three-file da8→new repair:

- `test_package.py`: adapt exactly two original methods, retaining their names.
  `test_fallback_terminal_after_setup_failure_and_mid_run_interruption` checks
  exact cell-only setup fallback, preserved terminal context and original
  exit/signal/exception through interruption; only IN_PROGRESS row/group/compile
  receipts become INTERRUPTED/UNKNOWN. It checks byte-exact preservation of a
  bound terminal and its interrupted predecessor, and null/array/partial terminal
  inputs. Collector remains observation-only and gives no credit.
  `test_fallback_preserves_receipt_materializes_tail_and_bounds` checks captured
  exit42 before fallback, byte-exact completed row/group/compile receipts, absent
  cell-tail materialization, interrupted row logs/outcomes, and artifact bounding
  with exact dropped bytes/hash. Bounds use a small in-memory cap only after
  canonical request/selection validation, with a fixed exact pair selection;
  production artifact cap/pins/validators remain unchanged.
- `test_cell_retry.py`: include both adapted methods in the already executed
  service-preflight suite. Add an explicit mutation control: compile the existing
  fallback function in memory with its sole `if not receipt.exists():` changed
  to `if True:`; run both controls against it and require both assertion failures
  on None versus42, with no errors/skips/hash-gate failure. A direct synthetic
  probe records exit42→null. No on-disk runtime modification is made.
- `CI-REQUEST.json`: update only SHA256 for these two test files. No other
  request field, hash, declared inventory, resource or proof setting changes.

The workflow is byte-identical to da8: its exact test_cell_retry/test_s108/
test_s108r1 preflight now reaches both adapted controls and the mutation test.
No runtime/preflight/fallback implementation, decoder/native capture, cfg,
source/tool identity, source assumptions/types/geometry, flags/checks/solver,
unwind/covers/labels/oracles/variants, ROLE-MAP, snapshots/location exceptions
or admission change relative to da8. REPAIR-DIFF.json records byte hashes of all
unchanged files and precise test-method/JSON changes.

REVIEW-DELTA.patch / SEMANTIC-DIFF.json preserve the whole new candidate delta
from reviewed7c for audit navigation. Its original runtime delta remains only
cell-only scheduling, two root timeouts600→1200 and necessary derived expectations
and receipts; compile900/RSS12GiB/headroom2GiB/phase8100/job180min are unchanged.
The reference35-row/14-group manifest and ROLE-MAP remain intact; other roots
stay600s and cannot execute. See the immutable original package and exact W14
review for prior confirmed properties; this repair does not claim to replace or
repeat the original proof audit. Static equality and actual shallow5/2/2 checks
were rerun for the new sibling; no compiler/solver/U/PFC runtime audit was run.

CONTROL-CANDIDATE.patch is relative to9208. All three patches reconstruct the
same exact new tree. parse_export, raw/native capture and missing-RESULTS handling
remain unchanged; TIMEOUT is NOT_COMPLETED/UNKNOWN, never accepted SUCCESS.
Author status FIX_PREPARED_PENDING_W14 is not a CLOSED/APPROVE verdict or GO.
