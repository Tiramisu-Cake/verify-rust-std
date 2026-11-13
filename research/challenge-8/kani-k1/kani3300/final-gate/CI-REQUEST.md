# GATE-P / C1 — coordinator CI request (NOT_RUN)

Worker15 prepared only Git/Python/static changes. No push, dispatch, local
compiler/Kani/CBMC, Cloud Build, slot/phase registration or budget spending.
All proposed run limits below require coordinator assignment; no automatic retry.
Preparation cap $0. Phase/owner/ledger/slot/deadline for execution remain unassigned.

Frozen export: `Tiramisu-Cake/kani:freeze/kani-3300-part1-c1` must resolve to
`1658f4cadfa83139e41180ce3865e23f79d889aa`, tree
`bfb5eb9db13ffb91ec4585b7c7ef41ddfe0008fb`. Do not move this ref or change
source after gates. Owner-reported qualification43509654772 was Quick only
(kani22/0, expected202/0, ui14/0, script1/0, json3/0), no full/replay proof credit.

## Publication set — after coordinator authorization

Publish only the exact local CI heads listed in CI-OVERLAY.json and
REPLAY-CI-OVERLAY.json to the corresponding `Tiramisu-Cake/kani` branch names.
Both have C1 as direct parent; never merge these overlays into export/upstream.

| Push destination | Exact local commit | Local clone |
| --- | --- | --- |
| Tiramisu-Cake/kani:ci/kani3300-fullgate-c1-w15 | `01ab0503392d7b25ce3732a2768313c6a50c910f` | `/root/kani-fix-3300-fullgate-c1-w15` |
| Tiramisu-Cake/kani:ci/kani3300-replay-c1-w15 | `d58b930924d13854ba1e34c4c5669df38d5d8310` | `/root/kani-fix-3300-replay-c1-w15` |

Research package goes only to the existing research branch when authorized.
Local origins point at read-only clones; do not push to those origins.
No force-push, tags, issue, PR, dependency upgrade or export edits.

The separate SmallSort test-only commit in REPLAY-OVERLAY.json does not need
publication: Gate B embeds its exact two-file patch, applied to an isolated
checkout of selected `Tiramisu-Cake/verify-rust-std` commit
`70ba5befc617627073738e26cb1466bd4fb76e41`. Original library tree
`6ea9d3425f6d0478cfc2517cbdd2fb7d7b32a53f`, patched test-only library tree
`2e7f781b35bc41d1431ea3729b888961f5c96b2f`. Coordinator must confirm this selected
library pin before dispatch; no claim about current PR#752 head.

## Gate A — full Linux regression

One dispatch of `kani3300-fullgate.yml` on the exact published Gate A head.
Runner ubuntu-24.04, concurrency1, job cap360min, regression subprocess20400s
(340min), per-test2400s; setup/artifact reserve20min. Proposed envelope21600s,
not measured runtime. Keep normal solver/slicing/checks and accepted per-fixture
12-bit flags; no global object-bits option. Empty KEEP_GOING, no filtering;
execute unchanged `scripts/kani-regression.sh` in separate exact C1 checkout.
Only this Linux platform is covered; no macOS/full-platform claim.

Require fmt/build-dev, all eight unit packages, dry configuration/build-cov,
all15 suites, firecracker codegen, smoke+clean and warnings-denied final build.
Receipt needs ordered stage presence/exits/counts, original process exit and
signal/timeout, before/after clean identities, binary/model/toolchain/dependency
hashes, and complete bounded artifact identities. Setup/network/runner failure
leaves later stages NOT_RUN; absent/incomplete trace never implies success.
Full scope and controls: FULL-GATE-REQUEST.md / CI-ONLY-OVERLAY-MAP.md.

## Gate B — SmallSort, uninit ON with matched OFF

Separate dispatch of `kani3300-replay.yml` on exact published Gate B head.
Twelve exact root/profile rows from REPLAY-REQUEST.json: three real PFC ON
roots and matched OFF, ordinary raw legal/negative ON/OFF, sort8 boundary
ON/OFF. All object-bits12; cfg controls ON; source unwind16/34; jobs1;
normal CaDiCaL/slicing/default checks; valid-value experimental flag OFF;
ordinary --no-assert-contracts retained and selected PFC Check body reviewed.

Proposed maximum: twelve serial matrix jobs, max-parallel1, fail-fast=false,
50min/job including setup/reporting; root cap2400s; aggregate maximum36000s
(10h), no retries. These caps are envelopes, not measured completion estimates.
The gcb-e2-standard-4 shape retained in REPLAY-REQUEST.json is an earlier alternative proposal; this prepared fork workflow uses ubuntu-24.04 and grants no GCB allocation or SmallSort phase/budget.
Any Cloud execution separately uses existing authorized coordinator lane and
its exact phase/owner/ledger/slot/deadline. No bypass through a new runner.

Require source/export/library/test-patch identities, effective argv/cfg/unwind,
fresh target/export per row, actual binary/runtime/model/solver/toolchain
hashes, regular/JSON root inventory, useful checks/ensures/covers, selected
Check body, original exit/signal/timeout, and exact intended failure locations.
Gate B rebuilds C1 independently; compare its runtime inventory to accepted
Gate A build before claiming shared binary/model identity. Source SHA alone
is insufficient. Unbound generated-property or Check-body causality remains
UNKNOWN/REVIEW_REQUIRED; CI observer is not a proof-acceptance oracle.

Raw-negative-on must fail at the intended retained source[1] read in actual
sort4/callback. Early requires/reference formation, Unsupported, frame error,
object limit, timeout/OOM or unrelated FAIL do not satisfy it. Keep geometry,
backing alternatives, offsets and contracts unchanged after a limit failure.
OFF is compatibility only; negative-OFF and sort8 observations carry no positive
proof or Replace-transfer credit. Exact criteria: REPLAY-ORACLES.json and maps.

## Reporting and acceptance

Both workflows are fork-guarded workflow_dispatch only, with always artifact
steps. Hard runner loss may leave a GAP; do not infer final success. Coordinator
reviews complete outputs rather than aggregate exit0. Preserve eight strong
oracles, six mode expectations, composition REGRESSION_BOUND inventories,
reviewed T1b allowance, and ORDER_UNCONTROLLED producer-order limitation.
Expected Unsupported/reproducers/source claims/B1 bounded evidence/B2 full proof
are distinct; independent proof credit is NOT_ESTABLISHED in this package.
Cloud evidence uses Evidence Brief v0.11; no raw archive/logging downloads,
historical ledger changes or download_verified updates.
