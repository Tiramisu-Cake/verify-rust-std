# Network N≤4 after S4P1 — offline plan

Disposition: **CONDITIONAL_PENDING_REVIEW**. This is a source/cost plan for root,
not an executable package or GO. Actual independent14 full SHA, verdict and
constraints have not been supplied. INPUTS.json binds task
`0f39a22f0148755e7ba881736e77b54f74b01cb5`, root inputs/decision
`27cdf2a7e7895344aa3be9c47b2867a9298c3e0f`, and verified intake
`842984040e87b8b8594653634b72df7d800ca198` including exact HANDOFF/COST hashes.
Source `985062ebad90cee1e2846b1648cd6a8624d146f6` and stock tool
`0aac16ef62da9e9d5645782d458593e5d78143ba` are frozen. All references below are
static pinned-source observations or supplied intake facts, not new native proof.

Recommend one separately authorized campaign of four new Original-mode,
full-byte network roots: `{0,1}`, `{2}`, `{3}`, `{4}`, retaining initialized
V34/base1, all34 independent bytes, full multiplicities, every outside-frame
assertion and arbitrary outside canary. Keep all existing negative controls and
caps. Front-load exact n2 after controls, then n3/n4 and the degenerate block;
this exposes the smallest nontrivial actual path first. Fixed lengths are explicit
coverage partitions with new IDs, not a universal theorem. Do not rerun the two
old heavy selectors. Completion and speedup of the new roots are UNKNOWN.

## Actual selected path and its obligations

S01–S12 refer to SOURCE-CITATIONS.json (commit/file/blob/hash/line ranges).
The two original roots S06 call `small_sort_network<u8,KeyLess<u8>>` directly on
`v[1..1+n]`. They do not call a trait body. The supplied request keeps sorting,
controls, s2_assumed, s3_leaf and s4_partition cfgs; exact native roots are Original,
with no enabled summary edge. The name `s2_assumed` enables predicates/contracts;
it is not a qualified provider. Preserve the frozen flag/check configuration;
module registration and ACTIVE source expressions do not establish native binding.

In S02, n0/1 return at `len<2`, before scratch construction. For n2..4, the
32-element MaybeUninit scratch is constructed but unused. `no_merge=true`,
`initial_region_len=n`, `region.len()<9`, `presorted_len=1`; the region loop runs
once, calls `insertion_sort_shift_left(region,1)` and returns. Neither sort9,
sort13, swap_if_less, sort4, sort8, bidirectional_merge nor scratch copyback is
executed on this path. Replacing n4 with sort4 or n2 with swap would verify a
different algorithm. The abort at n>32 and second-region/final-merge branches
are source-unreachable under this bounded domain; native path/exhaustion evidence
is still required, rather than an assumed mask or new panic stub.

S03's insertion pointer loop visits tails relative to begin at p=1..n−1:

| n | Actual insert_tail calls, absolute V34 begin/tail | Other work |
| --- | --- | --- |
| 0,1 | none | early return |
| 2 | (1,2) | prefix1 → ordered2 |
| 3 | (1,2), (1,3) | prefix1 → ordered2 → ordered3 |
| 4 | (1,2), (1,3), (1,4) | prefix1 → ordered2 → ordered3 → ordered4 |

At each call, prove one allocation/provenance, valid nonwrapping begin/tail,
initialized readable/writable `[1,p+2)`, and an ordered prefix of p full bytes.
Its modifies footprint must preserve the later active suffix and all outside
storage. Compose equal full counts across steps against the entry snapshot;
prove the final sorted prefix covers n. These are real caller obligations,
not assumptions inferred from a fixture name. S03's early-return/sift/CopyOnDrop
paths also require validity and initialization checks before every typed/spec
read and restoration on normal return. KeyLess<u8> is stateless byte `<` (S07),
so the bounded normal-return target does not need an arbitrary comparator-panic
premise. General FnMut side effects, unwinding, Drop/ownership and abort posts
remain separate OPEN obligations; do not remove their existing checks or grant
an ownership theorem from count equality.

Keep per-root unwind36, existing default50, and native unwind assertions.
Source envelopes: outside-frame loop34; active snapshot/count loops each≤4
(the nested count loops remain full, not a fewkeys oracle); descending≤3;
region loop1; tail loop≤3; each sift≤3. Snapshot has a fixed32-byte backing.
Compiler-generated/spec/memory-predicate loops are not established by this list:
actual emitted exhaustion/UB/validity checks must succeed. No local compiler,
exporter or verifier was run.

The unstable specialized source route for u8 is Freeze+Copy and uses size1≤8
and 1×32≤4096 (S01), hence chooses network in source. The forwarding and
specialized trait bodies, concrete emitted instantiation and real caller
binding remain OPEN because direct helper roots bypass them. Cell fallback
SUCCESS and stable/general bodies cannot discharge these obligations.

## Decomposition compared with partitions

CALLER-DAG.json enumerates every n0..4 call and p1/p2/p3 summary edge, with
T/F, domain, allocation, offset, init, frame, mode, provider and caller status.
All proposed summary edges remain **OPEN** and disabled.

The p1 bounded PFC report at
`97eaff96cd28267e36af69fe98077dd08737eea6` has superficially matching V34/base1
geometry. It remains SOURCE_REPORTED for that exact fixture: require actual
current-source callee/contract/tool/cfg and native provider/caller binding before
reuse, even for n2. p2/p3 need checked provider coverage and induction from the
preceding real call. One p1 result does not authorize all insertion lengths or
all pointer/allocation states. If summaries were inserted without those checks,
the result would be DIAGNOSTIC_ASSUMED, never a qualified network result. The
recommended campaign executes actual bodies and has no such dependency.

Bounded swap and sort4/merge8 PFC cases from the prior applicability report
are not universal contracts or automatic stub_verified summaries. Swap feeds
sort9 at n≥9; sort4 writes to a disjoint destination and feeds sort8/general,
not selected network n4. Original sort9 SOURCE_REPORTED is neither a semantic
contract nor a PFC provider. Allinit merge8 fixtures do not prove partially
initialized scratch; DIAG_INIT_OPEN partial merge is never a provider. They
are excluded source edges here, rather than shortcuts to n≤4. A future genuine
source-faithful decomposition for this task is insertion p1/p2/p3 plus the
checked caller loop, not swap/sort4 substitution.

PARTITIONS.json compares four choices. Splitting both old blocks into
`{0,1}|{2}|{3}|{4}` isolates every nontrivial length while sharing only the
source early-return pair. Five one-length roots are a useful alternative if
that pair itself censors, with extra compile/slot overhead and a separately
reviewed envelope. Leaving `{3,4}` intact repeats a censored selector and is
not recommended. V6/base1 roots could reduce frame work but prove only that
smaller backing; they lose the V34 geometry and cannot recover it from canary
equality without a checked locality/frame lifting proof. Thus retain V34 first.
Reduced byte domains are not selected; any future proposal needs distinct IDs,
explicit coverage loss, exhaustive full-byte union and SAT obligations.

## Coverage and admission boundary

New IDs in PARTITIONS.json are design labels, not registered selectors.
Disjoint union `{0,1}∪{2}∪{3}∪{4}={0,1,2,3,4}` retains exactly the old length
coverage, V34/base1 and all34 independent logical byte values. Preserve the
S07 owned snapshot, order, equal full multiplicities, all outside storage and
arbitrary outside canary. No claim extends to n5..32, another backing/base,
init masks, generic T/F or fullN16/N32/B1/B2. Each completed leaf would still
need its own native inventory/roles/SAT/U/guards/location/status review.

Retain exact per-length witnesses, ACTIVE and useful return. All nontrivial
roots retain unsorted, duplicate, nonconstant and descending witnesses; old
hi2/hi4 descending witnesses belong to n2/n4. In the `{0,1}` block, pair-based
unsorted/duplicate/nonconstant and old hi2/hi4 descending predicates are
infeasible. Future implementation must explicitly map those roles to union
witnesses at n2/n4 and review any explicit N/A/UNSAT handling; it must neither
expect impossible covers nor silently weaken the shared gates. This role/SAT
mapping is an implementation prerequisite, not an applied exception.

The four existing negative controls remain required: checker_order_corrupt,
checker_count_corrupt, sort13_weak, s4p_cell_count_corrupt, with their original
expected failure assertions/identities. Retain all other required matrices and
controls on compatible identities. No old evidence or qualified historical
case is rewritten. Two fallback missing-location proposals remain NOT_APPLIED
pending a separate root/coordinator decision and prove no network property.

## Actual cost, scenarios and the next decision

RESOURCE.json preserves the actual two wholechild costs601.428/601.401s,
compile-marker upper bounds48.195/45.976s and sampled RSS3515064/3516320KiB
against effective6291456KiB. Both cutoffs are CHILD600_WALL_INCLUDING_COMPILE,
after initial export/native start. No compile180/RSS/outer/slot/global cutoff
was observed. Native inventory and exact symex/backend subphase, uncensored
verification time/peak and signal timestamp are UNKNOWN. Sampling is nominal
50ms non-atomic owned-PGID VmRSS, not a strict kernel/cgroup/tree peak. Arithmetic
600−compile-marker551.805/554.024s is not measured solver time. More memory
has no demonstrated causal benefit.

Defaults remain child600 including compile180, slot720, local6GiB sampled PGID,
outer12GiB owned, reserve2GiB available, Ceff=min(6,12,A−2), campaign6900,
setup1800, job180min. RESOURCE.json gives scenario arithmetic, not predictions:
four positive roots + four existing negatives =8 slots, 5760s; adding conservative
controller180+cleanup240 gives6180s, leaving720s of campaign arithmetic margin.
Five exact-length positives + four negatives consume6900s under that screen,
with no spare margin. Neither calculation proves the nested actual runtime,
setup/outer/phase/job/deadline envelope fits. Future root/coordinator must
check that exact package; owner budget is TRACKING_ONLY and nothing is reserved.

Hypothetical120/300/600s per-positive-child cases give480/1200/2400s for four
positives before controls/setup/cleanup. They assign no probability or speedup;
a600s censored result remains UNKNOWN with possible overshoot. Repeated old
compile markers illustrate ~184–193s for four roots versus ~230–241s for five,
not a future bound. Do not infer fit from linear length or memory extrapolation.

If separately authorized exact partitions also censor, first retain their
actual phase/cost evidence. A narrowly scoped later wall proposal could be one
nontrivial exact root at child900/compile180 with slot1020, unchanged6/12/2GiB.
That is unselected and NOT_APPLIED, requires a distinct resource decision,
compatible nested limits/deadline/reserve, runner error-path tests/preflight,
exact-package independent review and root/coordinator GO+ledger. It offers no
completion guarantee. This plan proposes no memory-cap increase.

Root's next action is to bind actual14 fullSHA/verdict/constraints. If pending,
retain this disposition; do not turn elapsed time or review files in progress
into approval. Once this plan is sealed, preserve it and, if needed, make one
immutable evidence-update sibling for actual14 rather than rewriting history.
Plan acceptance permits no implementation or execution by itself. Future work
must separately authorize new harness IDs/role map and any source/control
registration, preserve production bodies/contracts/oracles/flags/caps, review
the exact immutable package, and obtain explicit root/coordinator execution GO
with its ledger. This task ends at the committed root HANDOFF.
