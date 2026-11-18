# W14 scope B — CHANGES_REQUIRED

Reviewed W11 package `ac956bdf4db98a95e2da988ccd2c527582d3d32f` against
task `90b7e5bd7f7dcecc00e7009196a466a7422f179d`, scope B only.
Control `b678fb6cdd5edf69a4e952167422f36a45a3d6cb`, tree
`beb2346615ffbb7027b2f1ea8ea33a149952aa0b`, parent
`9e14e033f9ee31522b571c127609dcdff76d230b` are exact and clean.
All 26 committed package files match. The three patches independently replay
to that tree, and their bytes match the corresponding Git diffs.

Two reproducible correctness findings block approval. Both belong to original
owner **11**, via the coordinator. No author implementation was edited.

## B-01 — P1: missing main-execution receipts disappear from artifact completeness

Location: `b678fb6cdd5edf69a4e952167422f36a45a3d6cb:ch8-s1-control/pack_evidence.py:43`
and `:99`; related fallback materialization in `check_package.py:184`.

`diagnostics` enumerates only directories already containing at least one
`rustc-*-receipt.json`. The final `diagnostic_retention.complete` aggregates only
that enumeration. It does not account for expected execution directories whose
diagnostics are absent.

The bounded reproduction finishes empty stdout/stderr captures for `setup`,
then invokes the existing fallback for the exact `s2-batch3probes-u34` group,
simulating interruption before the group's execute call. The group receipt is
`NOT_RUN_OR_INTERRUPTED`, its diagnostics are explicitly incomplete with both
stream receipts unavailable, and its outcome remains UNKNOWN. Packing nevertheless
emits only `setup` in `rustc_diagnostics`, and global
`diagnostic_retention.complete=true`, with no incomplete reasons. This hides the
group-level missing-data state behind successful setup captures. No proof outcome
is falsely approved by this probe; the false claim is diagnostic retention.

Required repair, **NOT_APPLIED**: determine diagnostic coverage from expected
execution/group receipt inventory as well as existing stream files. Preserve
missing/interrupted/NOT_RUN distinctions in the packed summary; an unrelated
complete setup must not certify the main group. Add a regression for this exact
case and for removal of both main diagnostic receipts at an artifact boundary.
Keep source receipts, exits and UNKNOWN/proof outcomes intact.

Evidence: `REPRODUCTIONS.json`, check `B-01`; `python reproduce.py`.

## B-02 — P2: suggestion diff context is silently cut off as complete

Location: `b678fb6cdd5edf69a4e952167422f36a45a3d6cb:ch8-s1-control/rustc_diagnostics.py:15`
and `:87` (completeness fields at `:125`).

The context predicate accepts numbered `N |` source lines, but not numbered
suggestion diff lines `N -` / `N +`. The first such line closes the active
error block as complete. The suggestion and its following gutter/context are
discarded without dropped-byte accounting or an incomplete reason.

A 165-byte rustc-style error/source/help/suggestion fixture, delivered one byte
at a time, retains only the first 126 bytes. In both stdout and stderr the missing
39 bytes include the proposed old/new source lines. Block, stream and compact
artifact all claim `complete=true`; `dropped_bytes=0` and incomplete reasons are
empty. This is below every cap, at natural EOF. The fixture is constructed text,
not recovered historical output or an observed diagnostic from the pinned compiler.

Required repair, **NOT_APPLIED**: retain suggestion diff lines and following
source/note/help context as part of the error block, or explicitly report any
context the parser cannot retain as incomplete with correct accounting. Add both
stream regressions with exact original-byte coordinates and packed text, including
split/ANSI input. Do not solve this by raising resource caps or exporting raw logs.

Evidence: `REPRODUCTIONS.json`, check `B-02`; `python reproduce.py`.

## Verified behavior and limits

| Area | Independent result |
| --- | --- |
| Exact package/control/delta | 26 package files, seven delta paths, all changed-file hashes and payload bindings MATCH; required parent/tree and three patch replays MATCH |
| Frozen semantics and limits | Request changes only `ci_changed_paths` and `ci_payload_sha256`; source/tool/cfg/argv/selection, 11 roots, 20 covers, six negative oracles and hard budgets unchanged |
| Original long-middle loss | Actual baseline `2ecf5e839f898f6bb1cd96edd6cc6bf677acb4c8` reader and candidate produce equal bounded previews for 168090 bytes; both previews lose the error, new receipt retains the exact block at `[84005,84085)` |
| Author's final targeted selection | Independently executed: **29/29 PASS**, including affected execution/compile/finalization/fallback/build-wrapper error controls |
| Chunk/ANSI/UTF-8/EOF and caps | Existing targeted controls pass; stdout/stderr capture, producer count gap, suppression, timeout, signals, output/retention cap, invalid/missing receipts and compact projection covered |
| Normal/failure/fallback propagation | Static execution/compile/group/row propagation and existing tests pass; B-01 blocks the global packing completeness claim |
| Full error context | Ordinary multiline source/note/help regression passes; B-02 blocks approval for suggestion diffs |

The seven-file delta adds diagnostics and offline preflight tests; it does not
alter proof/selection gates, source/tool inputs, native exit recording or numeric
resource caps. Existing native failure/snapshot controls pass. These statements
are bounded static/synthetic findings, not an exhaustive production guarantee.
Earlier author 69-test results remain author-reported, stage-qualified evidence;
they were not rerun or promoted to final-code validation.

No compiler, verifier, full runner, CI, push, PR, cancellation, ledger,
reservation, budget or author implementation changes were performed. No subagents
were used; model/effort settings were not changed. Production diagnostics retention
is **NOT_RUN**; historical run44284869572 compile cause remains **UNKNOWN**;
no B1/B2 or other proof credit is established.

Scope A approval `fc8eeb66342d588a513e22c1e2bf8552007fb690` was not rerun.
Source13's combined-r2 preparation is independent work, not a prerequisite for
this verdict. A later combined review can inherit a runner approval only after
these findings are repaired and the exact immutable replacement is approved,
with byte binding to that approved runner. This candidate is **not approved**.
