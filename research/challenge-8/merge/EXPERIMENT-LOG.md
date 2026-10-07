# Independent merge geometry experiment journal

## G1 card — before proof implementation/dispatch

Actual obligation: exact pinned merge_up/down and bidirectional_merge geometry
for arbitrary n>=2 and arbitrary comparator results, including access BEFORE
advancement, reverse wrapping intermediate, even/odd/minimum/final residual.
Hypothesis: count-based invariant and induction on arbitrary decision list prove
all access/advance bounds and terminal/residual geometry without sorting laws.
Domain: n=2m+e,m>=1,e0/1;0<=a,d<=k<=m; decision list lengthm-k, arbitrary
forward-left/backward-right choices. Both possible odd residual source choices
included. No enumeration/upper bound/SWO/pointer-ownership assumption.
Full mathematical normal post: all ordered modeled accesses in[0,n); forward
cursors admissible through n after access, backward source intermediary LR>=-1
with -1 never read; destination ordinary advancement stays in[0,n]; terminal
ends in[0,n], residual source and dst valid, write count2m+e=n, scalar guard
balance characterized separately. Comparator unwind: no further events after
panic; actual Rust unwind/resources not covered by pure lemma, remains OPEN.

Tool profile official unchanged VF26.09 with PLAN pins; source full SHA32574f...
Three Rust bodies admit exact token order + full-file hash in hosted runner.
Every abstract helper/recursive body checked; reusable frozen pure classifier
checks expected==visited bodies,normal/return/leak,0error and source integrity.
Positive: full invariant/induction/event/fullpost body acceptance, arbitrary n.
Negative controls: isolated off-by-one source READ at n and incorrect cursor
advance violating invariant. Each must fail ONLY its marked false assertion,
proof stage, exact predicate/location/column after setup and antecedents.
Fail-closed altered-location/predicate/body/target/column/timeout/source controls.
Concrete minimal witnesses calibrate negatives, never replace universal proof.
Outcome: positives+intended negatives accepted -> report geometry certificate
and exact Rust transfer OPEN; parse/annotation/solver failure -> new evidence
before within-profile fix; insufficient trust/budget -> precise checkpoint.
Selection dedicated workflow_dispatch hosted merge_geometry job/branch guard,
percase180s, job<=6min, new1800total inclprep; one own hosted run. No local execution.
Source/run/cost pending. Prior networks budgets/proofSHAs preserved in STATUS.

G1 implementation review: full universal mg_entry + recursive mg_trace_safe
normal posts,8named lemma bodies; no own bodyless lemmas. Standard unchanged
stock div_rem_nonneg(n,2) provides built-in integer division/remainder laws.
Negative case names merge_geometry_negative_read/advance/wrap_read, marked
TARGET_NEGATIVE_READ/ADVANCE/WRAP_READ. Expected VC strings in initial metadata
2<2,3=2,0<=-1; exact marked lines computed in retained hosted sources. A VC
format mismatch is INCONCLUSIVE, never accepted by relaxing the frozen gate.
Wrapped -1 witness added explicitly.21independent classifiercontrols expected
(7each). Source/signature/activeoperation SHA+line admission all3functions;
fullfile/static source map reviewed, actual tools/scripts NOT executed locally.
Hosted cap6min/inner300/percase180, first experiment0/1800spent.
