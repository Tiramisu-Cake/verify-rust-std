# N0..1: observed wall cap, symbolic exploration, source-only diagnosis

Run 44505531344/attempt 1 is completed FAILURE. All four positive partitions, including N0..1, stopped at the unchanged **600-second whole-child wall limit including compilation**. This is neither a successful degenerate proof nor evidence that uncensored cost is independent of N. Exact observations and authenticated member coordinates are in PHASE-OBSERVATIONS.json, COST.json and artifact-integrity.json. Source contexts below are pinned in SOURCE-COST-PATH.json.

## Actual N0..1 observations

The actual invocation is `8dcef366d8654f9cbd1715c87c925326`, with its own fresh cargo namespace and the single exact selector ending `sorting_s4_network_partition::s4p2_network_b01_n00_01_fullbyte`. Native registration reports core/Proof, Original/null target, no stubs, no verified stubs or contracted provider. Source SHA `c12867b1e651a3927cbd9f169fe2c3d3728a44c3`, stock tool `0aac16ef62da9e9d5645782d458593e5d78143ba`, request `c6abee25796842b0a1af44009921045c3da82b36e0fead42a342e7c5d8e74969` and actual cfg/argv agree across frozen readers and protected snapshots. The declaration of the domain is source-bound; emitted AST/MIR/assumption-to-property binding is not exported.

The compile receipt reports `COMPLETE`, boundary `STOCK_INITIAL_EXPORT_OBSERVED`, initial-export upper bound **30.284 s**, compile limit180 s, marker SHA `f4f3cd9047feb415199e9387f81c8a1188bc7e58e353506bb403ebb6631c70ff`. The bounded compiler stderr preview reports a dev-profile finish in29.83 s. These are different observations; neither supplies exclusive compilation CPU time or a separate Kani/MIR translation breakdown.

The stock export began at `2026-11-19T11:12:29Z` and remains `INCOMPLETE`, without `harnesses`, `wall_time_s`, completed native properties or `resources.verification_time_s`. The stock harness-start header was observed at monotonic3332.8327449. It is a harness marker, not instrumentation of helper entry or return.

Child elapsed is **601.592 s**, original exit **-15**, signal **15**, `termination_reason=timeout`, `timed_out=true`, shutdown verified. The extra elapsed above600 includes polling/termination overhead; it does not raise the allowed cap. Worker elapsed601.839331382 s is below slot720, worker exit0, supervisor cutoff null, no supervisor limit initiation/error or orphan survivors. Controller containment is verified, with adopted PID12777/start_ticks333283 reaped (raw wait status3840); the terminal seals after this last row. Per-row diagnostics retain original RunnerError, errno and process identities. There are64 retained lifecycle events and **80 omitted events** for this row: omitted details remain UNKNOWN. Cleanup observations do not establish an exhaustive syscall transcript.

Available memory was14996504 KiB. `min(6291456,12582912,14996504-2097152)` gives the observed **6291456 KiB effective local cap**. Sampled owned-PGID peak3911140 KiB and outer owned census peak3935208 KiB are below their respective6/12 GiB caps. Component maxima are backend3902112/compiler2539488/driver9028/other175268 KiB. Components are classified by process `comm`; backend includes CBMC and goto tools. Their nonsimultaneous peaks are neither additive nor exact per-phase/per-harness memory attribution. These samples support the recorded wall cutoff, not a kernel/cgroup/whole-tree true-peak claim.

The already-authorized compact receipt contains a bounded stdout tail with actual progress text:

```text
... smallsort.rs line 728 ... insertion_sort_shift_left::<u8, ... KeyLess<u8>> thread 0
aborting path on assume(false) ... function kani::mem::cbmc::same_allocation thread 0
Unwinding loop ... insert_tail ... iteration 1 ... smallsort.rs line 684 ...
...
Unwinding loop ... insert_tail ... iteration 2 ...
...
Unwinding loop ... insert_tail ... iteration 3 ...
```

PHASE-OBSERVATIONS.json retains the exact unabridged selected lines, their `/stdout/tail` coordinates and the member SHA. Stdout had1549777 observed bytes,65536 captured bytes,1484241 capture-omitted bytes, and61440 further preview-omitted bytes. No omitted text was recovered. This establishes that symbolic loop exploration emitted insertion-path messages. It does **not** prove that insertion executes on a semantically feasible N0/1 input, identify the exact phase at SIGTERM, prove an unwind check failed, or establish a causal hotspot. There are no per-line timestamps. N2/N3/N4 tails likewise show insert-tail unwinding; N4 includes “Not unwinding ... iteration36”, which is progress text, not a native exhaustion verdict.

## Frozen source path and remaining work at N0..1

All source citations refer to source commit `c12867b1e651a3927cbd9f169fe2c3d3728a44c3`.

- `sorting_s4_network_partition.rs:98–115`: source asserts the concrete model, constructs all34 independent full-byte values with `kani::any<[u8;34]>`, copies all34 into `bytes`, chooses symbolic usize n, assumes0<=n<=1, snapshots `[1..1+n]`, calls the actual `small_sort_network`, checks full sorted/multiset post, checks every outside-frame index with a34-iteration loop, selects an arbitrary outside canary, and declares exactly N00/N01/useful-return covers. None of these four assertion roles or three covers has a completed native verdict here. No UNSORTED/DUPLICATE/NONCONSTANT/MAX_DESCENDING site exists for this exact partition; their omission is structural source design, not acceptance of an exported non-SAT site.
- `sorting_model.rs:35–62,80–158`: exact u8/KeyLess specialization is active. Comparison reads the complete byte and uses `<`; active snapshot initializes a32-byte Snapshot then copies the selected prefix. Active post checks validity/length, adjacent order, and nested full-value occurrence counts. For semantically feasible N0/1, the order loop has no iteration and count loops have at most one-by-one iteration. The snapshot and frame/index checks still exist. This source reasoning is not an emitted-property or initialization proof.
- `smallsort.rs:332–377`: the real network helper returns immediately for len<2, before scratch, network9/13, insertion, or merge. Therefore a semantically feasible N0/1 source execution makes no comparator call in this helper. N2/N3/N4 instead choose presorted prefix1 and actual `insertion_sort_shift_left`; they do not execute sort9/13/swap/sort4. No assumed summary replaces these calls.
- `smallsort.rs:665–735`: the insertion path calls real `insert_tail`, uses pointer movement/copy/CopyOnDrop, and has active source contract attributes under the actual sorting/S2 cfg. Source contract helpers include span capture/post/order and memory predicates. The actual configuration exports `assert_contracts=false`, with `--no-assert-contracts`, all safety/unwind checks enabled and no verified stubs. It does not export effective expanded contract clauses or MIR edges; no stronger claim about actual instrumentation is made.
- `sorting_s2_span.rs:20–52` and `sorting_s2_swap.rs:38–56`: exact u8 predicates activate the first source assertion. Activation is not qualification of their provider contracts. Actual n/canary assumptions, symbolic construction and slicing are preserved by the exact source hashes; no native assumption trace is available.

## Candidate explanations, not measured causes

The meaningful discrepancy is source-early-return for n<=1 versus retained symbolic insertion-loop progress. One candidate is exploration of source-infeasible branches before constraints from symbolic usize n, dynamic slices and assumes prune them. Slice lowering, contract/builtin handling, or another transformation could also affect exploration. The compact does not distinguish these mechanisms or establish an actual MIR/compiler/model defect.

All34-byte symbolic construction/copy,32-slot snapshots, dynamic indexing, full frame/canary checks and oracle loops are additional source-reachable work. Some are common to the four harnesses, but shared source work and four censored observations do not establish common dominant cost, N independence, or a future fit guarantee. `same_allocation` assume(false) messages are observations about explored symbolic paths; they are not new U/guard inventories, proof of a common emitter, or an accepted proof premise.

Stock `kani-driver/src/call_cbmc.rs:172–238,267–278` at tool commit `0aac16ef62da9e9d5645782d458593e5d78143ba` describes CBMC invocation, unwind flags, and timeout/output handling. This source context cannot allocate actual run time between symbolic execution and SAT. Runner `runner.py:469–483,525–572,1093` at control `4059c900e50ba179d824a1e6f6bd7798cf343e36` explains the coarse component RSS and initial-export marker; the per-root body/model/checker/summary timings are explicitly UNKNOWN_NOT_EXPORTED_BY_STOCK.

## Missing evidence and root handoff

The compact has no internal symex/solver wall durations, solver-start timestamp, VCC/SSA/symex counts, measured initialization/oracle time, helper entry/return markers, timestamped phase at signal, completed native unwind outcomes, full positive property/U/guard/location inventories, or AST/MIR origin links. Exact signal time and omitted lifecycle event details also remain UNKNOWN. Child wall minus compile marker is arithmetic only; it is not exclusive solver/backend time. No raw/full/GCS fallback or experiment was performed.

This intake qualifies zero network leaves. It supports a separately issued offline simplification-or-defer plan bound to this committed packet. Candidate design questions include representing the same finite n-domain more concretely while keeping the real helper call, all34 independent bytes, type/comparator, four assertions, all feasible covers and complete frame/canary checks; diagnostic isolation would need its own limited claim. Removing the real call or assuming its summary would change the theorem. No implementation, resource escalation, unchanged rerun, new CI or admission follows from this intake.
