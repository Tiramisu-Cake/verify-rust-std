# Exact timing scopes and unchanged limits

This document proposes allocation and measurement gates. It changes no cap, flag,
runner, workflow, ledger or execution authorization.

## What 600 seconds means

The current experimental profile has **two distinct 600 s limits**:

* The supervisor's whole-child wall limit is600 s for one exact fresh-namespace
  invocation, including driver startup, compilation/codegen/instrumentation/export
  and verification. Its compile subcap180 s is **inside** that600, not added to it.
* `--harness-timeout 600s` is the native backend ceiling. It does not grant an
  additional600 s after compilation. The outer child deadline can terminate the
  invocation before that inner ceiling is reached.

The external clock is monotonic from child execution start through the supervised
child interval; shutdown is observed and reported separately as well. A measured
elapsed such as600.205 s includes observation/termination overhead and is a censored
whole-child result, not completed verification taking600.205 s. Compile180 cannot
be added to600 to obtain780. `verification_time_s` is a native exported metric,
not exclusive solver CPU, not a wall budget and not a substitute for the child clock.

Neither limit means full SmallSort CI must total600 s; campaign and job limits are
different scopes. Each claim must name the invocation set, timing scope, outcome,
platform and pins. A600 s child termination without a complete native export is
TIMEOUT/censored verification UNKNOWN, not backend TIMEOUT600 or a proof failure
with a known solver duration. Compile/RSS/slot/global stops keep their own causes.

Implementation anchors, read only: control tree `628a9aa91c86a2e5f72efee626b58f1715ec3dbf`
(reviewed control `3d3fb715271e3b195c6e0eee3557d5b0a6aad00d`, same-tree trigger
`d88fac48cf50a742f9f00026ba66e5e4353e1019`),
`ch8-s1-control/runner.py:616,685,690,1093,1159`,
`s4p2r2_campaign.py:239,283,306,347`, and `check_package.py:171`.

## Hard envelopes preserved

Source of truth: [network-r2 RESOURCE.json](../../ch8-s4/network-r2-impl/RESOURCE.json)
and its frozen request/workflow. These are nested/scoped limits, not summands to
add indiscriminately.

| Scope | Unchanged limit | Accounting rule |
|---|---:|---|
| Whole setup from setup epoch | 1800 s | Includes validation/checkouts/setup/tool build; stop if aggregate exhausted |
| Stock-tool build once | min(900 s, remaining setup) | Inside setup1800, not per-root compilation |
| Synthetic Validate step | 1080 s | Separate step ceiling; successful prior policy requires margin>=1.5 (elapsed<=720 s); within aggregate setup, not proof |
| Per-invocation compile marker subcap | 180 s | Inside child600; initial-export marker is an upper bound, not exclusive compile CPU |
| Whole child | 600 s | Compilation and verification share one deadline |
| Inner backend | 600 s | Simultaneously constrained by the outer child |
| Complete serial slot | 720 s | Worker supervision710 + durable publication reserve10; includes pre/post/containment/receipt overhead |
| Shared controller / campaign cleanup | 180 / 240 s | Reserves inside campaign, not per-row allowances |
| Campaign | 6900 s | At most9 full slots by arithmetic: 9*720+180+240=6900; actual selected set still frozen at8 |
| Outer process / phase / actual-leaf step | 7500 / 8100 / 7560 s | Different watchdog/deadline scopes; retain all |
| Job | 180 min =10800 s | Aggregate setup, campaign, fallback and upload must fit; individual step maxima sum to more than the job ceiling |
| Local / outer RSS / reserve | 6291456 /12582912 /2097152 KiB | Effective local=min(local6GiB, outer12GiB, available−2GiB); sampled PGID/owned census, no kernel full-tree maximum claim |
| stdout / stderr / export / artifact | 16777216 /1048576 /8388608 /268435456 bytes | Preserve caps and completeness checks; truncation/loss is not proof |

Flags remain exact=true, jobs1, default unwind50 with current root34/36 overrides,
object-bits12, no-assert-contracts and the current unstable/check/cfg set in RESOURCE.json.
No checks, useful covers or model roles may be removed to obtain fit. No warm-cache or
compile-sharing assumption is allowed to evade the per-child clock or fresh namespaces.

## Proposed planning allocations (not new enforced caps)

For one future invocation, use **60 s compilation +300 s native verification +30 s
other child work =390 s** as an initial soft target, leaving210 s under child600.
Then budget120 s for slot overhead, for a510 s planning target under slot720.
Only the600/180/720 hard limits are enforced today; soft allocations do not guarantee
fit. Native verification and compile marker metrics can overlap in scope, so acceptance
uses actual child wall and complete native results, not an unverified sum of metrics.
If compile actually uses180 s, the remainder under600 is at most420 s for **all** later
work, not an entitlement to420 s of solver time. Flag a soft overrun for decomposition;
keep existing caps and honest terminal outcomes.

For one future9-row campaign, reserve controller180 +cleanup240:
soft target `9*510+420=5010 s`; hard planned envelope `9*720+420=6900 s`.
For the current8-row request: `8*720+420=6180 s`, campaign reserve720 s.
The prelaunch gate must reserve **every remaining full slot** and cleanup; it must
not shorten a root because little campaign time remains. Serial execution stays jobs1.

For one job, allocate setup1800 including tool build900, campaign6900, and fallback120
+upload360: **9180 s =153 min**, leaving1620 s inside the180-minute job for outer
overhead. This is a conservative allocation, not a promise that checkout/network/platform
delays fit; the aggregate and step deadlines still apply. Example soft subdivision of
setup: validation/checkouts/tool setup/pins900 and build900, both subject to setup1800.
Do not independently spend each step maximum and then claim the setup budget was met.

For the hypothetical five-campaign core in PLAN.md,43 children imply a whole-child
envelope25800 s, including at most7740 s of compile subcaps. Complete slots plus
shared controller/cleanup reserve total43*720+5*(180+240)=33060 s, below five
campaign ceilings totaling34500 s. Repeated setup allows9000 s, including at most
4500 s of stock-tool builds. Five conservative job allocations total45900 s
(12 h45 min). These are summed serial envelopes, not measured runtime or an
available ledger allowance. The initial verification allocation43*300=12900 s
is a soft planning target, not a bound on unseen large-N proofs. Legacy/provider
lanes are additional; their costs and attempt availability remain UNKNOWN.

The proposed five core campaigns in PLAN.md have9/9/9/9/7 rows. Worst planned native
campaign envelopes are6900/6900/6900/6900/5460, sum33060 s. Adding five setup1800 and
five fallback/upload480 gives **44460 s =741 min** of serial job allocation (up to five
separate180-minute jobs), excluding retained-legacy and provider/calibration lanes.
This deliberately exposes the cost of a23-positive core with20 repeated controls.
It does not establish that these jobs or attempts are available. Fewer campaigns require
fewer proved-equivalent rows or a separately approved design, not hidden cap changes.

## What run44548842328 actually measured

Use [COST-INTERPRETATION.json](../../ch8-s4/run-44548842328/COST-INTERPRETATION.json)
and the admission/intake records; no new evidence was acquired for this plan.

| Scope / roots | Observed seconds | Meaning |
|---|---:|---|
| Four positives, native exported verification | 3.061223584 /3.846284711 /4.692468986 /33.427759135 | N2/N3/N4/N01, complete source-reported results at frozen caps |
| Same positives, whole child | 41.716 /43.751 /44.183 /72.998 | Includes roughly37 s initial-export compile markers |
| Four negative whole children | 37.816 /36.931 /36.581 /39.480 | Intended failures, not positive proof coverage |
| Selected8-row campaign | 359.3813398520001 | Excludes prior setup and tool build; not full S5 |
| Setup receipt / stock-tool build child | 531.1854872703552 /269.343 | Build is inside setup, not an additional setup interval |
| Connected job elapsed | 898 | Includes workflow overhead; not campaign or native verification |
| Earlier four network child cutoffs | 600 s limit, censored | Incomplete exports; old native verification durations UNKNOWN_CENSORED |

The reduction from old whole-child cutoffs to current completed network cases is
observed. An exact speedup ratio or compiler/MIR causal attribution is not established.
The campaign's strict producer outcome remained0/8 matches, SELECTED_PARTIAL and workflow
FAILURE; separate exact-case admission did not rewrite it. **359 s campaign != S5 PASS**.
It excludes larger network lengths, general, full fallback/entry domains, retained old
types/comparators and any newly required providers/consumers. No linear extrapolation
from N0..4 estimates the cost of merge32, sort13 or all six full entry contracts.

## Final measurement gates

For each final root record setup/build scope, compile marker, child start/end/exit/signal,
native exported verification duration, slot/control/cleanup/campaign/job times, effective
RSS cap and sampled peak, native inventory completeness, every check/cover/guard/U,
and exact std/tool/control/cfg/selector/target/stub identities. Missing exclusive solver
timing remains UNKNOWN. Report intended negative failures separately from positive PASS.

Measure the **full final inventory**, not only the new core. Compare baseline and proposed
inventory on the same platform, tool/pins, flags, runner and sharding; otherwise identify
the incomparable dimensions. Historical #752 summaries7802 s Ubuntu and10534 s macOS
are source-reported references, not matched measurements for the present stock tool.
Proposed integration gate: total SmallSort native VT must not increase versus a matched
baseline on either platform; target a decrease. Record setup/build/compile/whole-job wall
separately so repeated compilation is visible. A lower VT alone cannot establish lower CI wall.

Measure the longest actual shard and simultaneous aggregate RSS under organizer scheduling
(historical four count-based shards, KANI_JOBS=2), not just average VT or a serial opt-in job.
Preserve the6GiB local/12GiB outer/headroom policy for current experiments; a serial sampled
peak does not establish two concurrent children fit the organizer host. Normal PR inclusion
requires platform/shard fit and accepted coverage; opt-in feasibility can remain partial.
No900-second build success,600-second individual fit, or359-second selected campaign
can substitute for these aggregate and semantic gates.
