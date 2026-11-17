# READY_FOR_W14_REVIEW — W14-CELL-RETRY-01 repair

Control: `e27ec119eeac798d43d6bc056a449fa7576a5e94`.
Tree: `2c4475bf17bb0354e9b204e19c652549c263f90f`.
Parent: `9208b373c0a08a265fa0d7493a6529e331065271`.
Old control: `da8c766f957c576eafa44bccfba2c45490cef6d1`, immutable.
Old package: `9f4c37c894e7fecee0f59321ba66b65309a87606`, immutable.
Exact review: `ec48e6d59b552da2a9aa8d985478bf259c950073`, CHANGES_REQUIRED.
Base: `7c41333f9bfcfd7eb4e0ede7bd316443090c9025`.
Source: `99e8456d200fff1299ee5756279cddb23921dc65`, already published, unchanged.
Stock tool: `0aac16ef62da9e9d5645782d458593e5d78143ba`, unchanged.

Prepared the localized fix for W14-CELL-RETRY-01. Exactly two previous fallback
controls are adapted for the cell pair and included in the existing mandatory
workflow preflight. Captured/completed receipts, original exit/signal/exception,
IN_PROGRESS-only interruption, terminal context, tail materialization and
artifact bounds are checked. Workflow/runtime/fallback implementation unchanged.

PASS:18 top-level exact workflow tests, including the adapted controls inside
the service suite; the in-memory overwrite mutation is rejected by both controls
at original_exit null versus42. MUTATION.json records the two concrete assertion
failures and actual42→null observation below payload hash gates, with no skips
or errors and no on-disk mutation. Actual shallow5/2/2 preflight passes; depth2
reproduces the missing tool endpoint error128. All three patches reconstruct the
exact candidate tree. Source/tool/payload/YAML/whitelist/reference inventory pass.
Reproduce offline: `PYTHONDONTWRITEBYTECODE=1 python3 verify_package.py --tests`.
No local cargo/rustc/Kani/CBMC/rustfmt/solver/full runner or new proof audit.

Review maps: REPAIR-DIFF.json/REPAIR-DELTA.patch are bounded da8→new;
SEMANTIC-DIFF.json/REVIEW-DELTA.patch retain base7c→new; CONTROL-CANDIDATE.patch
retains parent9208→new. IDENTITIES.json/PAYLOADS.json/MANIFEST.sha256 pin all bytes.
OLD-TO-NEW.json maps the immutable previous package/control to this repair.
Author does not mark the finding CLOSED: reviewer14 decides CLOSED/APPROVE
against these exact committed identities. Review is not GO.

Scope/resources remain only cell-u34/2 previous roots,1200s each, compile900s,
child3300+cleanup10, phase8100, job180min, RSS12GiB/headroom2GiB. Other groups
cannot execute; missing RESULTS/TIMEOUT remain UNKNOWN. Old incomplete cell group
is unaccepted. No CI/rerun/cancel/push/reservation/ledger/publication occurred.
Current item2 charge stays8/14; future9/14 is not authorized. Intake11 was not
waited for or modified. Retry decision remains coordinator-only after terminal
S1-08 and committed intake. No auto-rerun.

1200s does not establish fit600s or ordinary cost qualification, nor label
causality. Preserve run/profile origin, no same-run combination across runs;
future composition/admission requires a separate explicit coordinator decision.
