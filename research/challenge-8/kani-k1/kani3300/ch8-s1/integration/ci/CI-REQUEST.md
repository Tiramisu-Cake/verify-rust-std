# S1 bounded CI request — preparation only

No push, remote branch, CI invocation, publication or Cloud spend in worker13.
Coordinator exclusively creates the eventual non-skip push trigger under
`uninit-ci/ch8-s1-*` in `Tiramisu-Cake/verify-rust-std`, after independent review.
Suggested ledger S1-01 is NOT_RESERVED/NOT_RUN. S1-02 is conditional only after
first-run review, for one corrective fixture/integration/CI change or minimal
blocker repro. Infra/rerun counts toward S1 cap2 and unified total32; no worker11
second allocation. Ledger remains untouched by this preparation.

## Exact source and control

Production/model export: `75a4d1ea6eb60c63c27c1b18e662740d93bafb08`, tree
`6d1b90bc11440762c9b65889fc538ba3071b0d9d`, based on published#752 std872d.
Accepted model source `3f469d3ba2e94d7129e66e53ea76df883ff9c946`, cherry-picked
as1313f7c329. Interface hash in JSON binds worker11. Tool stock upstream
`0aac16ef62da9e9d5645782d458593e5d78143ba`, tree
`9d8bc9312bf955ef126d32b819b3cd0ed105ed2b`, nightly-2026-10-23,
CBMC6.11.0/Kissat4.0.1 from exact tool config; no C2/SEL1/tool patch.

CI-only patch/identity receipt is separate from this production export. It deletes
ordinary workflows ONLY in the CI control overlay, adds one S1 workflow plus
scripts/ch8-s1 payload. It must be applied on the exact production SHA. Coordinator
makes the trigger commit with production SHA as its sole parent; checks compare
control HEAD to GITHUB_SHA, HEAD^ to production, and exact added payload hashes.
Source export and clean upstream tool never lose ordinary workflows. No local
non-skip trigger commit is created by worker13.

Checkout layout is sibling control/export/tool; outer workspace has no Cargo.toml.
Each source owns its normal build outputs on runner only. No nested workspace,
no compiletest/full Gate A/S2 probes. Dependencies installed from exact stock tool
setup; one tool build, one actual list, fixed rows serial jobs1/max-parallel1.

## Inventory, oracles and flags

Frozen prospective inventory is JSON rows: six symbolic N0..3 real-body PFC,
12 model controls (six legal/six named negatives), two legal attachment PFC
companions, two isolated false-ensures variants, one unchanged ordinary smoke
bridge. All23 rows NOT_RUN. Source selectors must match actual tool list exactly
(including crate prefix); mismatch is STOP, never fallback substring matching.
Generated property IDs/counts remain unbound until CI. Positive exports require
PFC metadata for PFC rows, complete checks, all covers satisfied, and normal useful
return. Intended negatives require precisely named failure, not a generic exit.
Setup/codegen errors, signal, caps, Unsupported or missing posts are UNKNOWN.

Actual CLI ordering is recorded per row: verify-std -Z unstable-options,
-Z function-contracts -Z mem-predicates -Z float-lib -Z c-ffi -Z loop-contracts
-Z quantifiers -Z stubbing, --no-assert-contracts --jobs=1 --harness SELECTOR
--exact --default-unwind ROW -Z export-json --export-json OUT
--output-format=terse STD/library, then --cbmc-args --object-bits 12.
Cfg sorting+controls is pinned; experimental uninit/valid-value OFF. Solver,
slicing and checks remain defaults, unwinding assertions ON. N0..3 smoke unwind34
covers CAP32 checker loops conservatively; model controls retain unwind4/5/34
as specified. No summary stubs or panic/comparator stubs. --no-assert-contracts
is preserved even for both false-ensures PFC diagnostics.

## Caps and costs

One ubuntu-24.04 job, workflow120min; setup<=30min (including tool build),
verifier/list phase<=75min, receipt/upload reserve15min. Each invocation hard600s
from driver through codegen/backend. Fixed rows planned2760s + actual-list estimate
300s =3060s (51min), leaving1440s inside verifier phase. These are UNMEASURED
planning estimates, not performance evidence. At all600s worst case23 rows cannot
fit75min: the phase watchdog stops, writes remaining NOT_RUN and yields UNKNOWN;
no successful-fit claim, silent skips, cap increase or automatic rerun. A new
row starts only if its full600s plus cleanup fits the remaining phase; a short
remaining phase never silently reduces the invocation cap. Coordinator
and worker14 review estimate/inventory before dispatch; reduce only redundant
diagnostics with review if revised estimates exceed envelope, preserving required
controls and six bodies. Setup failure still consumes the eventual dispatch.

RSS concurrent process-group aggregate cap6291456KiB (=6GiB); raw sampled peak
KiB and GiB=KiB/1048576 captured, not sum of lifetime process peaks. Sampling is
an observation with50ms granularity, not exact kernel high-water proof. Timeout,
RSS or output cap terminates process group TERM then KILL. Each row stdout/stderr
bounded, export<=8MiB; whole retained artifact<=256MiB, retention7days. Truncation
explicitly marks UNKNOWN. Always fallback yields per-row NOT_RUN when setup or
an interrupted wrapper leaves no receipt. Preserve original exit/signal and
execution evidence before postprocessing; never relabel named negative exit as
workflow success without a complete export and review.

S1 establishes mechanism on selected N0..3 geometry only. No threshold theorem,
extra-UB assurance, arbitrary T/F/frame, Replace credit or organizer acceptance.
