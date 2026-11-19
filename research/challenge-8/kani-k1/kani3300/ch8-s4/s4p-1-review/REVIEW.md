# Independent W14 review — REQUEST_CHANGES

READY_WITH_LOCALIZED_FINDINGS, not APPROVE and not GO. Reviewed exact author
`590dd6360f5b4c92eab9fff30aa0d2e7d8d942ce`, task
`c049f3c7f44d111db45baf36a5de24dc19209ee5`, and frozen plan
`a931835b4af8dc8b2ad60e9a115bc0a4903b0b5e`. This is an implementation review,
including source, profile, runtime, readers, prebuild gates and plan premises.
Two P2 findings prevent exact approval. Neither establishes a Rust sorting
counterexample or grants proof credit.

**R14-01 — restore complete cfg projection coverage.**
At control `e941155517a02f67ea9bac1adb81c1d5f6f85638`,
`ch8-s1-control/s4p_contract_stacks.py:109` adds the fifth independent key,
but line 110 still enumerates `range(16)`. Sorted keys are `kani`,
`kani_smallsort_s2_assumed`, `kani_smallsort_s3_leaf`,
`kani_smallsort_s4_partition`, `kani_smallsort_sorting`. Consequently bit 4 is
never set: every generated projection omits sorting, and none enables the
complete ACTIVE S2 guard. The gate returns STATIC_PASS with 16 projections
instead of all 32. The fresh real gate report exactly reproduces the committed
MAP-CONTRACT_STACKS report's omitted contexts (AUDIT.json).

This defeats the declared all-feature-combinations regression audit, including
the active safety-wrapper-to-direct-Kani normalization comparisons. Exact source
hashes, normalization equality and the separate active contract inventory still
hold; this finding is an incomplete validation gate, not evidence that current
production contracts actually changed. Original13 should derive the enumeration
from the key count (for example `range(1 << len(keys))`), add an actual Validate
regression requiring the complete unique power set, all 32 projections and all
four ACTIVE-guard contexts, and refresh the exact map/payload/packet provenance.
Keep old profile gates and their independent coverage intact.

**R14-02 — reject malformed terminal campaign schemas at both readers.**
At the same control, `ch8-s1-control/s4p_campaign.py:340` reads terminal metadata
and validates selected_roots, then enters legacy_collect at line 345. The
subsequent terminal checks at lines 348–354 validate state/profile/selection,
but never require terminal `schema == 'ch8-s4p-1-campaign-v1'`.

Using real current writer/finalizer, public collector and compact packer with
synthetic native data, changing only that field to absent, null, old bridge
schema or integer 123 was accepted through both LOCAL and UPLOAD_ONLY routes.
TERMINAL-SCHEMA-MATRIX.json records all 24 accepted mutations across full eight
completed rows, SELECTED_PARTIAL with zero completions, and STOPPED0. In the full
case all eight observations remained RECORDED. This bypasses the task's explicit
new-schema identity gate; it does not bypass all the other identity/role checks
or create independent proof credit. Original13 should require the exact terminal
schema before observation collection on both routes and add distinguishing
Validate tests for missing/null/wrong-type/old/wrong schemas, preserving genuine
full/partial/STOPPED prefixes and old profiles' own schemas/counts. The standalone
reproducer is reproduce_schema.py; use a disposable copy for future reproduction
so this sealed review output is not rewritten.

The following checks passed, subject to those findings:

- Exact source `985062ebad90cee1e2846b1648cd6a8624d146f6`, tree
  `c937101b3056ab6d2e93f25c152e3d0b92004b27`, sole parent
  `97ac4d39d7f959ea70b1f57785ffd1fd66ecd22a`.
- Exact control `e941155517a02f67ea9bac1adb81c1d5f6f85638`, tree
  `a1ea7697041b043d98d34bdb1d7d703879726a8e`, sole parent
  `9e14e033f9ee31522b571c127609dcdff76d230b`; stock tool
  `0aac16ef62da9e9d5645782d458593e5d78143ba`, tree
  `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b`. All three heads clean before/after.
- Packet 54 files/53 hashes, exact author bytes; 40 source files and all 117
  control payload hashes; request SHA256
  `ff5d370fec4577527a03a84a42fa72db97d30efe34a86adbee02a05f80ac4f47` and workflow
  `a56791ab37df944d65131c0a7a612a5245d3c8a0275ff8810fb44fa6a7af061a`.
  The author read-only checker independently executed with 576 checks PASS.
- Six patches independently applied using disposable indexes, each yielding
  its complete expected Git tree. Independent local shallow fetches at source5,
  control7 and tool2 preserve all stated required commits and exact tip trees.
  Source whole-tree diff against f1 is only new partition module plus appended
  guarded verify wiring; production kernels, contracts, old models/harnesses and
  old verify prefix are byte-identical. All control entries outside the declared
  delta against d675 are unchanged.

All eight request rows and source bodies were checked in order:

| Row | Bound source behavior | Required result / covers |
| --- | --- | --- |
| checker_order_corrupt | Unchanged fixed [1,2] to [2,1] | Exact S2_NEG_CHECKER_ORDER failure |
| checker_count_corrupt | Unchanged fixed32, last value corrupted | Exact S2_NEG_CHECKER_COUNT failure |
| sort13_weak | Unchanged descending [12..0] caller-copy weak seam | Exact S2_NEG_SORT13_WEAK failure; no positive actual13 claim |
| s4p_cell_count_corrupt | Initialized Cell34, [1,3) [0,1] to [0,0], outside unchanged | S4_NEG_CELL_ACTIVE success and exact S4_NEG_CELL_COUNT failure |
| s4p_fallback_b01_n00_02_fullbyte | Actual fallback, Cell/KeyLess, inclusive 0..2 | Four located success roles; 3 per-length SAT covers + 5 witnesses |
| s4p_fallback_b01_n03_04_fullbyte | Same family, inclusive 3..4 | Four located success roles; 2 per-length SAT covers + 5 witnesses |
| s4p_network_b01_n00_02_fullbyte | Actual network, u8/KeyLess, inclusive 0..2 | Four located success roles; 3 per-length SAT covers + 5 witnesses |
| s4p_network_b01_n03_04_fullbyte | Same family, inclusive 3..4 | Four located success roles; 2 per-length SAT covers + 5 witnesses |

All are Original/null. The four candidates retain independently arbitrary whole
logical bytes across all 34 initialized elements, base1, full sorted multiset
postcondition, every-outside frame and arbitrary outside canary. Cell snapshot
owns copied logical bytes via concrete get/Project specialization; the count
control is still sorted but differs in multiplicities. Equal lengths and counts
of every original distinct byte exclude introduced values as well as losses.
No value-domain reduction, assumed invariant, ordinary/verified replacement or
provider edge is enabled for these candidates. The old weak negative alone uses
its unchanged intended ordinary seam.

The actual small-length call paths are fallback -> insertion -> insert_tail and
network n<9/no_merge -> insertion -> insert_tail. Cell is not passed to a
Freeze-bound network. The 34-element initialization/frame loops and <=4 active
snapshot/count loops justify the proposed source unwind envelope36; this is
not compiled-loop exhaustion evidence. Each unsorted/duplicate/nonconstant
witness is guarded by n>=2; descending at hi and all length witnesses are
source-feasible. Literal source totals are 21 assertion sites and 30 cover sites;
native property/instance counts and exhaustion remain UNKNOWN.

Fresh ordinary, cfg/PFC, contract-stack and lexical gates ran against the exact
source, including Cell/import/provider anchors and every required new function.
They return STATIC_PASS, with R14-01 limiting the projection portion. Missing
required static paths, Cell get anchors, module declarations and contracted
ordinary targets reject in targeted tests. The lexical gate explicitly leaves
typing, generic/method dispatch, expansion and MIR unproved. Request, exact
singleton argv/selector/unwind/cfg, fresh namespace, Original export target-null,
native-start observation, metadata inventory, roles, statuses, locations and
covers remain checked by the actual writer and local/upload reader paths.
Strict U/unsupported/guard/extra-failure rejection remains; prior location
exceptions/admissions do not transfer.

The new campaign was compared directly with the reviewed bridge implementation:
the runtime algorithm is preserved, with new profile/policy/schema routing and
four negatives. Shared snapshot, evidence, lifecycle, bounded diagnostic,
packing and legacy runtime modules are unchanged. Canonical tool resolution
precedes E0; source/control/request/bin captures, all-state observed drift and
read errors, absent-inner-AFTER interruption recovery only after verified
cleanup and matching controller post, original exits/errors/errno/epochs,
ownership initialization/finally, PID/starttime census and escaped-child reap
remain guarded. Atomic portable seals exclude raw captures as replay
requirements. Recorded drift cannot be excused by controller recovery.

selected_roots is a genuine int8 derived from validated request inventory.
Missing/null/bool/string/float/wrong values reject on both routes, including
STOPPED0 and partial prefixes. Existing exact Validate records include every
valid prefix0..8, legacy7/8/9, caps, lifecycle/error paths, escaped children and
B01/B02 diagnostic tests. Fresh targeted tests checked roles, Cell/count,
required source paths, Original/PFC mismatch, timeout/signal/missing/null/partial/
NOT_RUN/wrong-type/error exports, real relative-path writer/portable replay,
STOPPED0 and partial count validation, and all-state drift rejection.

Reviewer targeted execution: 12 tests initially passed; one path test errored
because a stdin harness left sys.path[0] relative while its fixture changed cwd.
The initial log/JSON are preserved. With an explicit absolute import path, that
test and three additional distinguishing path tests passed (4/4). This was a
review harness correction; source/control were untouched. Total 16 distinct
targeted tests passed. The two reproductions expose gaps not asserted by those
tests. See TARGETED-TESTS.*, TARGETED-PATHS.*, AUDIT.json and SHALLOW.json.

Actual author final Validate evidence is bound to the exact control/request/
workflow/script and retained stdout/stderr hashes: 302 tests, exit0, 554.090277s,
1.94914086x at the unchanged18min limit, >=1.5. All five original suite lists
remain wired to s4p_validate; failure/precursor objects and records are retained.
This review checked the retained local execution record and did not repeat full
Validate. Pure-lexer caching occurs only within Validate, keyed by full text,
returning fresh lists of immutable token pairs. Independent tests across all
five patched lexers confirmed full-text/line-coordinate equivalence, fresh-list
mutation isolation, uncached lexer errors and restoration on normal/exceptional
exit. There is no source-read, identity, gate-result or test-result caching.

Resource limits remain exact: child600 including compile180, slot720,
controller180, cleanup240, campaign6900, outer7500, step7560, phase8100,
setup1800, job180min; sampled local PGID6GiB, owned outer census12GiB and available
reserve2GiB, Ceff=min(6,12,A-2); output16MiB/1MiB/8MiB/artifact256MiB. The 6180s
eight-slot envelope is arithmetic, not native fit or a kernel/cgroup peak claim.
Artifact remains ch8-s3-2-${{ github.run_id }}-${{ github.run_attempt }} with sole
group-evidence.json.gz. No stock-tool patch, uninit-ON or model experiment entered.

Route findings through root to the original fresh13 CURRENT26d. Reviewer has
edited only this new review directory. Original13 owns a new immutable repair
candidate/packet, distinguishing tests and refreshed final exact provenance;
SAME14 reviews the delta into a new immutable review output. Preserve this
candidate and its failed/precursor history. Exact approval and a later root GO
are still required; publication, nonskip same-tree sibling sole9e14 trigger,
future source/head/ref/run and ledger belong to the separate user coordinator.

Native compile/proof/exhaustion/cost/fit, compiler/MIR binding and B1/B2 were not
run or established. No CI, full runner, raw/GCS access, push, publication,
admission, accounting, subagent or model change occurred. Even after a later
completed/reviewed/admitted union, scope is only lengths0..4 per exact finite
family; fallback5..16/network5..32/general/type/caller/init/ownership/panic and
provider obligations stay OPEN. Existing two bounded SOURCE_REPORTED admission
cases and strict historical0/7 are unchanged. New proof credit NONE.
