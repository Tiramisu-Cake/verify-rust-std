# M2-B/R resource evidence and phase map

PREPARED/AWAITING_CI. No new execution, proof credit or established resource root cause. Inputs P1/P2, exact pin/tree/parent and source hashes are in INPUTS.json. The following measurements are coordinator-reported facts from TASK-KANI3300-M2B.md, not independently reconstructed process telemetry.

| Source / fork run | P1/P2 reported observation | What it establishes |
| --- | --- | --- |
| M1+M2 5f7f2b7364 / 43243491671 | cutoff, >6.4/8.0GiB in 10–12s | RESOURCE_INCOMPLETE; intended property verdict UNKNOWN |
| B1I-A6134e42dd1 / 43244391200 | same resource cutoff | M1 not necessary for reported cutoff; first source boundary/phase UNKNOWN |
| upstreambf9c58e662 / 43244395728 | 46s/1.4GB; frame in store_argument, unreachable load_argument, Unsupported | Non-equivalent executable obligations; no baseline semantic PASS or speedup |

P1/P2 attribution of each quoted number, raw RSS unit interpretation (GB vs GiB), exact sample times, process-tree vs per-process measurement, actual kill threshold/signal/exit and overshoot are not supplied. The reported watchdog triggers above6GiB with sampling overshoot; 6GiB is not a proven hardware cap. Existing timeout300s is the requested policy, not a measured elapsed value. C03 4s/238MB refers to the different ordinary Assert selector, not scalar PFC. Earlier combined legal-pair 15GB evidence likewise is not a matched singleton baseline.

Connected GitHub metadata in CI-METADATA.json confirms all three job/step summaries completed success, including Build Kani and singleton configurations. The connector's first-page artifact arrays are empty. Job success does not establish subprocess exits or verification PASS. No curated process/phase/property receipt is available in these supplied inputs or returned metadata. No raw logs/archives were read; run IDs are GitHub numbers, not Cloud Build UUIDs for smallsort-brief. The source-only M2 qualification map explicitly leaves generated numeric signatures/property IDs UNKNOWN.

## Pipeline boundaries to measure, not inferred outcomes

| Phase | Source route at the pinned history | Required curated measurement | Current evidence |
| --- | --- | --- | --- |
| rustc / transforms / GOTO codegen and link | contract pass → generated Check/modifies/ensures wrappers; UninitPass/visitor → lowering → monomorphized mem_init models | actual selected root, instance kinds/types/counts; injected Begin/store/load/set/check counts; emitted symbol/object/function/instruction totals, file bytes, type/layout extents; rustc/codegen/link process argv/time/RSS | UNKNOWN for all matched P1/P2 models |
| GOTO specialization / instrumentation / DFCC | call_goto_instrument.rs:19–73 specializes root, optional restrictions, instrument_contracts, library/drop-unused and back-edge rewrite; :172–216 emits --dfcc/--enforce-contract | pre/post DFCC object hashes/sizes, symbol/function/instruction/check deltas; assigns lambda and private writes; exact goto-cc/goto-instrument process peaks and exits | UNKNOWN; only source order established |
| inlining / symbolic execution / VC generation | CBMC consumes instrumented GOTO via call_cbmc.rs:172–191,263–310; internal phase order is an installed-CBMC receipt obligation | actual milestones separating lowering/inlining/symex/equation creation/slicing; VCC/SSA counts and process RSS/elapsed at each milestone | UNKNOWN; a process named cbmc does not locate the phase |
| Boolean conversion / CNF | backend internal stage, not identified by Kani process name | entered/completed conversion, bitvector/equation size, variables/clauses and matching process sample timestamps | UNKNOWN; no inference from an absent count |
| SAT solving | chosen solver at actual installed pin | actual solver, start/end milestones, variables/clauses when available, process PID/RSS/elapsed/exit | UNKNOWN; no solver verdict from watchdog cutoff |

`--only-codegen` returns before `verify_project`, hence before the driver's DFCC instrumentation. Its successful exit is not a post-DFCC inventory or proof. Existing non-solving backend inventories must identify which artifact/stage they inspect; unavailable instrumentation inventories stay UNKNOWN, without a new runner or an invented CLI.

## Ranked, falsifiable hypotheses

1. **H-A3:** A3 current-call protocol, private scalar state expansion, mandatory return0 and new assertions increase DFCC write/check or VC work on actually reached wrappers. Discriminator: unchanged P1 b207 vs a0, compare pre-codegen/pre-DFCC/post-DFCC/VC sizes and per-process milestones. Falsified as a necessary source interval if both sides already show comparable cutoff at the same phase with complete retained paths. A difference only locates an interval including repairs.
2. **H-early:** Part1/A1 MU relevance/masks/private buffer migration already enlarge model or retain paths unavailable upstream. H-A3 may be additional rather than initial. If both first pins are heavy, next handoff should narrow earlier (A1/Part1), not blame A3. Upstream early Unsupported/frame/absent return protocol makes its lower resource number unqualified.
3. **H-B1I:** preserving call instrumentation across unresolved/shim paths changes actual stores/loads/wrappers/monomorphizations. If both first pins are cheap and complete but6134 is heavy, locate A3R→B1I with an independently measured matched model. Current reports do not distinguish this from environment/model mismatch.
4. **H-layout/DFCC:** actual generated wrapper layouts, specialization count or instrumented assigns expansion dominate, even though private state source fields are only scalars (6usize/2bool before A3;11usize/4bool after). Require actual array extents/instances and emitted counts. Source line counts or struct field counts cannot estimate memory use or exclude an expanded backend object.
5. **H-M1 additional:** immutable origin/extent/seeds can add work at M1, but do not explain necessity of the already-reported6134 cutoff. No M1/worker14 source edits or repeated M1 run are requested now.

Each inventory must retain actual PFC, useful ensures, false source-following transfer and checks. Missing store/load/early Unsupported/changed selected root classifies the pair NON_COMPARABLE, not improvement. No-match/partial receipt is UNKNOWN, not NOT_RUN. The next distinguishing experiment and four-configuration maximum are in CI-REQUEST.md. No ablation or release fix was created; diagnostic removal has no semantic/proof credit.
