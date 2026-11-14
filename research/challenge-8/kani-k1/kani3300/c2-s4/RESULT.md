# C2-S4 handoff

READY `3b382c812a1b8541946e6dc732cf04497ebcf995`

Source clone `/root/kani-fix-3300-c2-s4`, branch `fix/kani-3300-c2-s4`.
Sole parent `ad324418cdc66b18e9b71f76a412be6ccea20c7e`; tree `716a2446684bb56e0a03b7fbe5df26593648a1c8`.
Author and committer: Tiramisu-Cake <igkharin@gmail.com>, set with git -c.
Source is clean; no push, local builds or CI dispatch. Research uncommitted.

Implemented the S4 first-write journal and scoped restore for delayed-mutated
entries only, including failed-root Unsupported. Original transformed Body and
modified flag move back after current model consumption; regular prewarm/new
entries, stubs/contracts and loop metadata remain. CPROVER Harnesses/AllFns/
PubFns and the existing LLBC global-pass caller are covered. Async exporter
owns materialized values and does not read restored MIR later.

Comparator requires strict exact full inventories; no acceptance allowance or
T1b classification remains. Explicit --collect-unbound skips stale goldens,
keeps full schema/root/configuration/verdict/process guards, completes all
11 invocations with deltas, and returns 2/UNBOUND_CAPTURE/NOT_CHECKED_CAPTURE.
No fixture/manifest binding, runtime, protocol, masks, SCC/points-to, ordering,
solver/check flag, or std algorithm change. No S5, F8, or SEL1 work.

Baseline: exact ad324418cd + baseline-tests.patch; expected tree
`6bed3373b8c2c62f103c2f3c8ecd99d5a90db95a`. This is a test-only package with the same five
observer/test/document blobs as candidate. Temporary-index apply and expected
production-identical tree verified; build/reproduction NOT_RUN.
CI-REQUEST.md specifies seven isolated and four mixed fresh-process selections
per tool, 18 exact comparisons, full source/tool/env receipts, actual shared
unit/read binding, baseline accumulation criterion, candidate strict equality,
and cross-tool isolated inventories. No new golden inventory is created.

Validation performed: requested rustfmt wrapper exit 0, git diff --check PASS,
54 Python synthetic tests PASS (43 comparator + 11 binding), independent Luna
HIGH static review without actionable findings. Six journal and two guard
native tests added but NOT_RUN. Rust compile/borrow checker, build, clippy,
Kani/CBMC, new baseline accumulation and candidate isolation all NOT_RUN.

Separate status:
- Structural lifecycle: IMPLEMENTED, statically reviewed, execution unverified.
- Observed producer order/unit identity: NOT_ESTABLISHED/NOT_RUN; CLI permutations
  are regression coverage only, not observed AB/BA.
- Fresh inventory isolation: NOT_RUN on both tools. Historical R4 data is not
  the distinguishing baseline and grants no new credit.
- JSON composition debt: retained; ordinary bound suite may FAIL until S5.
  Preserve #5093's two real isolated SUCCESS overflow assertions and all existing
  S2 immutable19/unit9 and S3 negative/reinit controls; no all-PASS Quick claim.

This is preparation readiness only, not S4 CI acceptance, C2 completion, or
SmallSort verification/proof credit. Coordinator execution is the remaining
acceptance work, outside this worker's no-build/no-push/no-CI authorization.
