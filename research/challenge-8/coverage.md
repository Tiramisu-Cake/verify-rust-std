# Challenge 8 coverage ledger

This tracks requirements, not inferred coverage from an Actions badge.
Current stop/phase: [STATUS.md](STATUS.md). Evidence and exact source/tool
identifiers: [experiment log](EXPERIMENT-LOG.md). Distinguish actual-source
proofs, bounded adapters, synthetic fixtures and prefixes of failing proofs.
No complete Challenge 8 solution is established.

Current S7b: **auxiliary generic body NOT ACCEPTED; actual linkage NOT ACCEPTED;
no S7 actual advancement.** [Report](SORT4-SELECT-FORGET-RESULTS.md),
[design/trust](SORT4-SELECT-FORGET-DESIGN.md), [current checkpoint](STATUS.md).
Standalone run37675513854/source `c9c59a85807da0135a8192b1912b15d510c68028`
checks the whole minimal generic unit without focus/select/macros/guard. All seven
predeclared functions execute, return and leak-check; full verifier exits1 with
sole adapter-span dead-code diagnostic. NORMAL/readonly/decode/refinement exit0;
source hashes PASS. Existing ManuallyDrop correspondence remains TRUSTED.
Separate immutable replay37676357686/processor
`dd4b0493b8411d92f61f525a3c7ef6ec0429d021` preserves all nine original classes;
new separate map has two INCONCLUSIVE positives and seven intended negatives.
Dead-code exit1 never becomes PASS. Full S7 thread/cell/frame/borrow/admission/
mutation controls and new-profile regressions remain NOT RUN; no actual redirect.
S6v4 remains accepted. Last actual run37656621026 still stops at forget63,
std/lib.rsspec420 requiring absent nominal guard-own; assume_init is not reached.
Full helper/sort4 NOT PROVEN. Latest [AST diagnostic37678089113](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37678089113),
source `a6f077a5aa89ad25df94295320cdbe18ebe4b9d9`, confirms an orphan translated
cleanup return; full VF remains exit1, with source/MIR/tool identity retained.
STOP at frozen translation/dead-code acceptance; no pruning/exemptions/model change.
Physical loc-key attribution remains an explicit diagnostic limit in the report.
Budget **4752/5400 summed hosted job seconds used; 648 remain**, no reset/no active
run. Historical budgets and instructions below do not reopen phases.

Historical S6 closeout: **COMPONENT_ACCEPTED (v4); actual integration STOPPED at forget guard-own.**
[Fresh run37656621026](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37656621026), proof source
`75681fbc57bda633f59096cdc28f0c1aa61daef8`, profile
`experimental-source-linked-select-pointer-drop-v4`, patch
`c7cc08a995bac5879901f4fe08030f09d23bdfefb1a3ab5893be12a8dd1f8fc1`.
Constructor/as_mut_ptr/typed intrinsics/narrow pointer drop matrices and14baselines
PASS freshly; S6 has2positive+11proofnegative+22source/MIR/pin negatives, all on
intended obligations. All19 independent NORMAL controls reject exactly beforeproof,
including oldreceiver26→23. Full source/typed method+actual MIR/runtime/normal-unwind
CFG correspondence preserved; diagnostic37649244205 is not a proof. Five extra
stock ghost locals/blocks and every annotation coordinate are in the design table.

Actual baseline still lacks initialized payloadcell. Stock-projected actual enters
proof after full36/19 admission and checkedmethod redirect. Both stock opens, proof
condition split, retained runtime drop at verified/lib.rs60 and both closes61/62
pass in the recorded prefix. Next blocker: verified/lib.rs63 `mem::forget(guard)`,
frozen std/lib.rsspec420:41–42 requires nominal
`<DropOnPanic<*const Element>>.own(t, guard)`, absent. No guard/forget extension;
STOP at this exact obligation. Current classifier stays INCONCLUSIVE with heuristic
kind intrinsic_select; rawlog establishes the forget guard-own failure separately.
Finalreturn/leak/fullnormal-unwind posts not reached; wholehelper/sort4 NOT PROVEN.

Checked method and ghost resource identity lemma are separate from TRUSTED compiler
raw-pointer drop glue correspondence and frozen stock frontend ghost substitution.
Existing initializedcell/fullpointervalue/thread/independentframes required, no
Element rights. Recursive free stub is not a runtime-body theorem. Runtime std,
signatures/targetcontract unchanged; broader04d67f4b/Drop/guard/forget/assume_init/
union/refiner/kernel/memory/alias/provenance stay frozen. Further semantic work
requires a separate owner decision; no additional dispatch authorized at this stop.
Budget **3954/5400 summed hosted jobseconds used;1446remain**, same budget/noreset,
noactive. Last two proof orchestration jobs:37654585346=184s,37656621026=202s.


Historical accepted pointer-select baseline: S4b source-linked SAFE as_mut_ptr accepted;
S5k/37624082376/source128dd5673c7796c5916017ab4afafaeea8d836b8, profile
experimental-source-linked-select-pointer-intrinsics-v2/7bb39a84 accepts two
exact intrinsic specializations (*mut *const Element and MaybeUninit<*const Element>).
6positive/10proofnegative/40admission and classifier/regressions PASS. This is a
trusted compiler intrinsic value rule plus verified SAFE adapters, not Rust intrinsic
body proof. Complete modeled value/inner/state and caller frame/thread preserved.
Actual source-linked helper full31local14BB gate/refinement/3translations PASS;
body first stops at drop_in_place57, final return/leak/normal-unwind posts NOT PROVEN.
Drop/guard/forget/assume_init unaccepted; source-linked assume read-resource hypothesis
NOT RUN (S5j readonly refiner1 RawPtr1:4 plus normal tail-annotation failure;
S5k RawPtr refiner/union frontend failure). No semantic boundary declared;
kernel/refiner unchanged. Owner resumes ONLY S6 pointer drop with mandatory
initialized-cell pre/full-value preservation; other extensions FROZEN; S5r2/37626031885 sameprofile S5j replay accepted with exactly8
message corrections, original classifications retained. No new proof execution.
[Results and compact evidence inclO4](SORT4-SELECT-POINTER-RESULTS.md),
[design/dependency map](SORT4-SELECT-POINTER-DESIGN.md). Fullhelper/sort4 NOT PROVEN;
RAPx CLOSED/NO-GO, B/C NOT RUN.

[Night phase](SORT4-NIGHT-PHASE.md) N2/37547890530/source3f5c9e3 now accepts the
exact experimental fieldless layout profile d4a12525 after full matrix/artifact
audit: original profile comparisons,18extra cases,7metadata controls,10native
paired controls and31classifier/span checks PASS. All Rust source-integrity,
export/decode/refinement gates retained. Historical wrong-source-span mutation
rejected, but new owner review found its hi coordinate invalid on a blank line;
C3/37586921301/source3844c5f now recalibrates it with valid distinct
lo(7,0)..hi(7,12), unchangeddefSpan(7,13), both source-bounded and solebinding
mismatch. Full6+6/18/7/10 matrix and41 classifier/span checks PASS. C++ empty complete-object nonzero assertion
now verifies both profiles. N1/37547307118's remaining C++ annotation error is
historical, not replaced evidence. Acceptance concerns only pinned original-fieldless
nongeneric Sized reprRust/C structs with optional alignment and geometry. It adds
no field/generic-ADT/packed/transparent/enum/union/DST/ownership/copy semantics,
full-model soundness, automatic operation UB, callback or whole-sort4 theorem.
Independent stock [index theorem](SORT4-INDEX-LEMMA.md) now PASS at N4/37548475221,
sourcefa74d92: checked header/application,VF0,8statements/leak checks; all5 independent
Booleans give intermediate/final bounded distinct IDs,each0..3 exactly once.
Duplicate-index negative fails intended assertion on manual audit; raw processing
INCONCLUSIVE retained and corrected saved replay in N5. This adds a universal pure
index component, no actual Rust-callee/pointer/memory/refinement bridge.
Stock [abstract rank order/stability](SORT4-ORDER-LEMMA.md) N5/37548811698,
source6a12b4e,39statements PASS and intended all-equal instability negative rejected.
Fixed/preserved integer ranks are functional premises only; pure finite-SWO
[finite-SWO transfer](SORT4-SWO-BRIDGE.md) accepted at N11/37553933186,
source3c3f0f3,104statements: arbitrary relation16/all4diagonal+64triple laws,
predecessor count0..3,less iff rank< and equivalence iff rank=. Intended tied-rank
negative rejected at19. N9/N10 timeouts are historical; checked isolated arithmetic
helpers resolve both without changing laws/posts/profile. Pure network composition
accepted at C1/37585795831/source0383012,194statements with all
components and full original posts; C2/37586573468/source4e7ee10 hosted saved
audit accepts intended stability assertion failure and3 classifier mutants, no
verifier repetition. Raw C1 negative INCONCLUSIVE preserved. Historical N12 remains pre-verifier failure. This is pure mathematics;
actual callback/T/pointer/resource simulation remains open.
Stock [scalar range composition](SORT4-MEMORY-OPERATIONS.md) N8/37549955948,
source9b25c41,24statements PASS: exact selected IDs to dst0..3, containment and
separation for arbitrary stride>=0 (includingZST0). Endpoint negative rejected.
No pointer/provenance/overflow/permission/initialization/reference/copy theorem.
[Pointer ownership closeout](SORT4-POINTER-OWNERSHIP-RESULTS.md) O4/37601511894,
proofSHA182ddf29dc73961723bf32be6b65643c524ca927, artifact11473086721,
experimental-source-linked-maybeuninit-pointer-own-v2/patch325af428:
**defined MaybeUninit<*const Element> value ownership and SAFE constructor ACCEPTED**.
Full exact source/HIR/typed MIR admission, checked introduction/imported body,
inner equality/token/frame/no-unwind/return/leak,5proof/8source/9MIR controls,
nonpointer opaque ownership preservation,5classifier groups and14 separate
stock/experimental Rust/C/C++ baselines PASS. Empty value-own resources grant no
pointee or storage permission; no Copy/Freeze/pointee premise. Exported path-string
identity/local-copy equivalence is an explicit trust limitation, not native DefId
identity or organizer acceptance. Existing ManuallyDrop identity remains a trusted
frozen dependency. This does not extend general union/alias/borrow/copy/Drop semantics.

[Actual pointer select](SORT4-SELECT-CALLEE.md) O4 on that same source/profile/artifact
passes integrity/export/decode/refinement and SAFE prototype, then both verified
constructor calls at22/23. First remaining error at38,20–41: unsupported
MaybeUninit::as_mut_ptr(&mut self). Storage-address/borrow permission bridge is
outside the accepted value rule; extension STOPPED. Full callee normal pointer/
provenance/frame and no-unwind posts NOT PROVEN, later operation proofs NOT RUN.
Historical N6/37549040942/sourceaed1d97 first blocked at runtime new;
C8/37592506846/source53b64a7 translator-only profile failed SAFE opaque ownership
before body. Their raw failures remain historical; they are not O4 acceptance.
Full sort4/callback/unwind/raw-scratch/copy composition remains open. RAPx CLOSED /
NO-GO; B/C NOT RUN.518/5400jobseconds,4runs,noactive,unused budget retired.

The [sort4 phase](SORT4-PHASE.md) completed on 2026-10-06 under the
[revised roadmap](PLAN.md). [Hosted closeout](SORT4-RESULTS.md) establishes
the actual-body functional domain: four arbitrary full-range i32 keys in
fixed/disjoint initialized buffers, plus separate tagged-item stability.
Generic safety and complete four-category UB coverage remain open.

The subsequent [contract-diagnostics phase](SORT4-CONTRACT-PHASE.md) completed;
[run37466906281](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37466906281),
source7f96aa2, validates unchanged values0/267failed/12covers, coincident actual
copy overlap negative, shifted original-multiset negative with all other default
checks passing/unreachable, and independent zero-output witness0/130failed/1cover.
The44-case classifier rejection gate passes. Coincident first copy violates
non-overlap; shifted individually disjoint copies lose original values, NOT an
UB finding. Prior memcmp-unwind and formatted-panic-label fixture failures are
preserved in [closeout](SORT4-CONTRACT-RESULTS.md). No generic safety/UB coverage
or new VeriFast result follows; [adopted research contract](SORT4-CONTRACT.md) and
[one selected architecture/gate](SORT4-SAFETY-DECISION.md) remain unproved research
specifications. That phase stopped at the owner decision; its proposed verifier
capability remains NOT AUTHORIZED.

The bounded [no-patch review](SORT4-NO-PATCH-ASSESSMENT.md) completed with no
new experiment and **no generic coverage gain**. Static comparison of official
VeriFast26.09/26.10 preserves relevant tuple/HRTB/direct-unwind/typed-scratch gaps;
Kani remains a concrete monomorphized evidence route. Target-source compilation/
refinement on26.10 NOT RUN. These are feasibility observations, not new target
failures or proofs. The historical patched proposal remains unauthorized;
the later explicit-domain decision below changes no tool finding or proof count.

The [remaining-tools screening](ALTERNATIVE-TOOLS-ASSESSMENT.md) selected the
[RAPx applicability phase](RAPX-APPLICABILITY-PHASE.md). Its preceding session
closed [INCONCLUSIVE](RAPX-APPLICABILITY-RESULTS.md). Hosted runs
[37492790456](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37492790456)
and [37493697524](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37493697524)
failed in runner setup (direct-driver version argument channel, then absent
Cargo checksum metadata). Exact package installation/version/binary identities
were recorded, but installed-source audit, layout, MIR, target preparation and
all six alignment controls were NOT RUN. Zero fixture paths/obligations and
**no generic or detector coverage gain**. B/C NOT RUN because A did not pass.
The suspected ZST alignment gap and callback/panic concerns remain source-review
concerns, not executed counterexamples in that historical session.
The subsequent owner-authorized A-only continuation used2/4 NEW runs and closes
**NO-GO**: run37508888778 at929ea803 completed identity audit and all six actual
controls (48 primitive records, six checkpoint paths). Both deliberate
alignment-eight ZST source/destination byte-offset1 copies are SOUND with the
violated Align ProvedByRule; optimized MIR retains the defect. Valid ZST/u64
controls prove; u64 negatives fail intended Align with separate ValidPtr Unknowns.
Manual contracts/DefId/checkpoint/property/MIR audit establishes these observations;
all automatic JSONs remain fail-closed/unmapped, not successful checks. This adds
concrete detector-limit evidence, **no generic or actual-sort4 proof coverage**.
B/C NOT RUN, no further dispatch/patch authorized. All safety/sorting tables below
retain earlier established proofs.

The separately authorized automatic replay37513897141, processor1c0b517,
uses only original artifact11434810024/source929ea803. All six real pairs parse;
9/9 hosted replay/mutation test groups pass. It reproduces two PROVED_VALID,
two ZST SOUND_MISS and two intended Align detections with separate Failed/Unknown.
commands_succeeded/evidence_parsed=true, gate_outcome=NO-GO. Original unmapped
JSONs/manual result preserved. This adds reproducible processing, **no new
verifier run or semantic coverage**. Replay scope CLOSED at1/2 allowed runs.

## Safety targets and sorting contracts

The documentation-only [joint-route assessment](SORT4-COMPOSITION-ASSESSMENT.md)
adds **no proof or detector coverage**. Multiple tools may prove independent
obligations, but current evidence supplies no generic composition or checked
model bridge. RAPx presently remains diagnostic; other properties are not
automatically reliable after the scoped Align finding. ZST is retained with
independent geometry/operation/resource obligations, A NO-GO and B/C NOT RUN.
The unchanged-VF alignment gate was NOT RUN / NOT AUTHORIZED at that review;
its separately authorized initial [scope](SORT4-ALIGNMENT-PHASE.md) closed INCONCLUSIVE at1/1.
[Run37529855468](SORT4-ALIGNMENT-RESULTS.md), source17ad1f4, passes all six
exports/decodes/refinements but every VeriFast case fails annotation parsing.
Zero helper/caller proof bodies or intended negatives were reached; this adds
**no geometry, layout, detector or generic-sort4 coverage**. Proposed formatting
correction was separately authorized and applied at9474453; the ONE additional
[run37532204465](SORT4-ALIGNMENT-RESULTS.md#syntax-only-continuation--one-new-run)
now closes INCONCLUSIVE. All six exports/decodes/refinements pass. Generic helpers
reach bodies but fail 0<=address before callers; ZST layout fails size==0, ZST add
fails pointer limits. Both byte-offset controls reach and reject intended line25
alignment assertion on manual audit. This adds limited false-post control evidence,
**no geometry/layout/automatic-copy UB or actual-sort4 coverage**. Raw all-six
INCONCLUSIVE/header counts0 retained; actual source-prefixed named headers exist
but the classifier frozen for that historical scope misses them. That scope closed
at additional budget1/1; its raw outputs are never replaced by later replay.
The subsequent bounded no-patch continuation [run37535499783/sourceea635ea](SORT4-ALIGNMENT-RESULTS.md)
closes at a concrete ZST model boundary,1/3 NEW runs,38s total jobs/setup.
It adds checked const/mut helper-body proofs under explicit local nonnegative req,
caller derivations from existing array/provenance/layout/size_align facts, successful
.add and full post/leak checks on i=1,2,3 paths. The residual no-helper path still
fails alignment post; **no complete generic geometry theorem**. Both negatives
now automatically reject exactly the marked line25 assertions after byte add/cast.
Hosted replay leaves original parse errors INCONCLUSIVE, separately recognizes
syntax-run negatives, and passes3 test groups/30 fail-closed mutants with unchanged
historical tree/source hashes. Original raw JSONs/logs/outcomes remain preserved.

The concrete ZST size0/align8 and unchanged-address add posts remain unproved.
[Source-to-model trace](SORT4-ALIGNMENT-MODEL-BOUNDARY.md) establishes lost repr
alignment and a positive concrete-struct size assumption incompatible with Rust ZST;
a faithful calibration needs reviewed model correction or an independent component.
Generic prefix/branch proofs do not repair that correspondence. ZST is retained;
**no automatic-copy UB, ownership/callback/unwind or actual-sort4 coverage gained**.
STOP at model boundary, unused run slots retired; no verifier extension implemented.

The separately authorized [generic completion/layout review](SORT4-ALIGNMENT-RESULTS.md#generic-completion-and-layout-review--two-new-runs)
uses runs37537448952/source16aaf1b and37537868053/source519a370,2/2 NEW,85s summed
jobs/setup. First explicit residual i==0 assertion fails. Second checked integer
order splits derive0, pointer identity/alignment and original residual resource /
return/leak posts. Three impossible guard-body assertions trigger dead-code gate:
**whole-unit generic const/mut remain INCONCLUSIVE, no accepted full-profile theorem**.
No classifier/check suppression, runtime/outer-contract change or third run.
All exports/decodes/refinements/stage hashes pass; ZST layout/add retain earlier
blocks; negatives2/2 and unchanged replay3 groups/30 mutants pass in each run.

The [layout review](SORT4-ALIGNMENT-MODEL-BOUNDARY.md#follow-up-layout-model-review-documentation-only-2026-10-07)
checks26.09 and26.10/master exact sources and plans a bounded compiler-backed Rust
struct layout correction, Rust-scoped nonnegative lower bound, shared typeid/target
consistency and other-language preservation. Changing>0 to>=0 alone supplies no
exact0/8 facts. Kani0.67.0 concrete Z candidate has no existing Z/full-domain bridge;
contradictory concrete VF Z facts cannot be used in a composition. Regression
matrix DESIGN ONLY / NOT RUN, no tool patch/new axiom or new target coverage from
review. Accepted generic geometry, faithful concrete Z layout, automatic copy UB,
ownership/callback/unwind and actual-sort4 coverage remain open independently.

Arithmetic evidence alone would not count as automatic UB coverage. Required VF
callback/unwind/raw-copy capabilities are separated from optional historical
insertion patches. Existing Kani results retain their exact concrete domains.

The documentation-only [admissibility review](SORT4-ADMISSIBILITY-REVIEW.md)
adds **no proof or detector coverage**. Full range separation is sufficient and
caller-established, not shown necessary for every safe overlap or accepted as
the complete standalone target domain. Our full ownership/Shadow/no-debt protocol
is a resource-accounting choice, not the language's minimum no-UB condition.
Legal callback effects/all five panic exits stay in safety scope; order/key
preservation belongs to conditional functionality. The owner subsequently
adopted this explicitly delimited [research domain](SORT4-CONTRACT.md#adopted-domain-and-caller-obligations)
after the [authority check](C-VERIFICATION-ARTIFACTS.md#authority-and-separation-precedents).
Caller-precondition proofs are required for composition; no such new proof was
produced by the decision. Organizer clarification is deferred, not a planning
gate; committee acceptance is unconfirmed. **No coverage counts change.**
The old RAPx runner's evidence-dir/processor-scope mismatch is only a static
preparation limitation; it changes none of the historical measured claims.

| Actual target | Established evidence / tool | Remaining obligations |
| --- | --- | --- |
| `StableSmallSortTypeImpl::small_sort` | None | Default / Freeze specialization; arbitrary valid lengths and scratch; sorting contract; generic ownership and comparator behavior |
| `UnstableSmallSortTypeImpl::small_sort` | None | Default / Freeze dispatch; arbitrary valid lengths; sorting contract; generic ownership and comparator behavior |
| `UnstableSmallSortFreezeTypeImpl::small_sort` | None | General / Copy network / fallback choices and stack-size thresholds; arbitrary valid lengths; sorting contract |
| `swap_if_less` | Kani: two bounded i32 harnesses, positions 1/2 in a four-cell initialized allocation; 5/5 covers (37383583285) | Generic values, arbitrary valid indices/allocations, ZST, comparator mutation/panic, all required UB checks |
| `insertion_sort_shift_left` | Kani: direct bounded i32 functional proof, lengths/offsets 1..4, sorted prefix, 7/7 covers (37389298278) | Arbitrary valid lengths, actual outer-loop contracts, independent safety domain, generic types, ZST, ownership and panic restoration |
| `sort4_stable` | Pinned Kani actual body: sorted exact multiset for four arbitrary i32; separate symbolic-key/fixed-ID item stability and complete-item permutation; source unchanged;18/18 covers (37459631500) | Fixed disjoint initialized buffers/pure nonpanicking `<`/Copy layouts only. Generic validity, aliasing/provenance/ZST, ONE ownership, comparator effects and all five panic exits remain open; see refined contract and selected architecture. Concrete overlap diagnostics37466906281 expose the short-comment safety/functionality gap; they add no generic coverage |
| `has_efficient_in_place_swap` | Unchanged VeriFast 26.09: actual unrestricted generic const body, req true, exact size_of(T)<=8 on LP64; VF/refinement pass (37401540878) | Dispatch callers and full-core integration; no other target follows from this pure helper proof |

Only the size helper has an isolated generic proof among these seven targets.
The other six and all three sorting contracts remain incomplete.

## Internal callees and fixtures — separate from public target completion

| Artifact / run | Source and tool boundary | Established / still open |
| --- | --- | --- |
| Bounded `insert_tail` adapter, 37389298278 | Actual std callee via proof-only i32 adapter; pinned Kani | Contract has sorted-prefix precondition, 6/6 covers. Three-call summary harness proves that research caller only; not std's modular pointer loop or unsorted-prefix safety. |
| Generic insertion diagnostic, 37417173472 | Exact-source unrestricted T/F; experimental patched VeriFast | Prefix reaches first FnMut/partial synthetic unwind, lifetime cut/recovery, tail.read, guard and first copy/dst update; fails at compiler Drop. Not a proved callee or completed exit contract. |
| Actual `CopyOnDrop<T>::drop`, 37419989766 | Exact extracted std body; experimental patched VeriFast | Generic T/arbitrary valid len with fractional initialized src, full initialized dst and ONE ownership sequence; exact copied values, VF/refinement pass. Conditional internal body proof only. |
| Local Drop callers, 37435525052 | Actual Drop plus two synthetic one-element callers; experimental `tuple_local_drop` profile | Whole normal caller and FnMut() normal/unwind caller pass with exact destination/ONE ownership/leak checks. All 25 controls and 7 intended negatives pass. Not actual insertion, held &T release or arbitrary FnMut(&T,&T) provenance. |
| Two-cell normal recovery, 37437514808 | Synthetic i32/unrestricted T callers and actual recovery helper; UNCHANGED release 26.09 | Genuine share/init, natural block exit, full initialized current cells/T.own; two positives and three intended negatives pass, refinement passes. No callback/panic/ManuallyDrop or std integration. |
| ManuallyDrop recovery, 37441463201 | Synthetic control; `manually_drop_only`, existing single translator patch on 26.09 | FAILURE: new common recover_single helper blocks all seven callers before intended tests. ManuallyDrop positive also fails RawPtr refinement. No new lifecycle or intended-negative result; earlier unchanged-release baseline remains established. |
| Isolated recover_single, 37448257248 | Synthetic helper, same minimal single-patch profile | Actual conditional full current tmp-cell/T.own recovery body passes,16records and leak-check. Neither MD caller reaches reference or helper call: immutable tmp half storage fails full-borrow precondition. Positive RawPtr refinement still fails; missing-init negative NOT established. |
| Rechecked release recovery, 37448682524 | Same source f0f417c, UNCHANGED26.09 | Both original full-cell positives,3 intended negatives, all5 export/decode/refinement checks pass; optional helpers absent. No new std target completed. |

The old local-cleanup failure37423762729 was superseded by the complete
caller gate37435525052; callers are no longer "unexecuted". Negative refinement
was intentionally not run in that caller gate, so no such result is claimed.
The 25 controls include matcher rejection tests, not 25 proved comparator bodies.

Still open: source-exact first false return/direct panic recovery; genuine
held-reference release/provenance; second comparison; generic gap invariant;
full normal/late-unwind range restoration and actual outer loop.
`COMPARISON_DEBT_POST` is diagnostic, not the final full storage post.
Patched-tool success does not establish verifier soundness or admissibility.
See [resource ledger](INSERTION-RESOURCE-LEDGER.md) and
[borrow applicability gate](BORROW-RECOVERY-DESIGN.md).

## Required UB categories

| Category | Current measured evidence / pinned Kani | Remaining work |
| --- | --- | --- |
| Dangling / misaligned loads and stores | Default bootstrap checks; sort4 actual comparison reference-alignment/invalid-pointer checks and copy source/destination alignment, readable/writeable regions, overlap/null/dead/bounds checks pass in both concrete domains (37459631500) | Arbitrary allocations/types, generic provenance/permissions, ZST and relevant stronger pointer profile |
| Uninitialized reads | Explicit uninitialized i32 read detected in37394356873; positive read2/2covers. Sort4 uses initialized fields by construction; explicit target uninit profile NOT RUN | Apply measured instrumentation to actual targets; generic ownership/raw scratch remains separate |
| Mutating immutable bytes | Write-only passes37394356873; observed write9/volatile-read/assert9 and1/1cover pass37397720683 | Concrete detector gap in this measured profile; cannot claim this required category |
| Invalid values | Invalid bool detected in37394356873; valid bool read2/2covers. Sort4's i32/u8 scalar fields admit every bit pattern; explicit target validity profile NOT RUN | Broader target/type coverage; actual copy_nonoverlapping validity instrumentation is unsupported in37396688760 |

These claims concern Kani pin `152c6a8c875d9886a67e229247b4826d6105ccfd`,
not all versions/tools. API flags in `kani-driver/src/call_single_file.rs:143-152`
and `kani_metadata/src/unstable.rs` describe capabilities, not proof results.

Actual insertion's explicit uninit/valid-value/pointer profile first hit an
instrumentation ICE37395779522 (unsupported Formatter function pointer in the
delayed-uninit pass). The harness-only raw-slice construction resolved that ICE
in37396688760; validity instrumentation then rejected copy_nonoverlapping as
unsupported (pinned check_values.rs:387-393 TODO). All7covers/unwind assertions
passed, but no completed UB safety proof exists. Keep the checks enabled.
The immutable-write control is an independent measured limitation.

## Cross-cutting completion gates

- Lengths: insertion remains bounded to four cells; sort4's four cells are its
  complete arity, but buffers/types/comparator remain restricted. Arbitrary valid
  lengths at the three small_sort entrypoints remain unproved. Bounds16/32 only
  measure performance.
- Types: internal Drop and recovery fixtures have conditional generic results,
  not generic safety of public entrypoints. Interior mutability/non-Freeze,
  invalid bit patterns, large types and ZST model adequacy remain explicit gates.
  The pure size helper accepts unrestricted T without allocation/comparator.
- Comparators: bounded swap allows arbitrary single decisions; insertion
  and sort4 functionality use pure nonpanicking key `<`. Safety must separately cover
  stateful/mutating comparators and panic, without borrowing ordering premises.
- Loops: bounded insertion uses unwind6 with unwinding assertions. An outer
  invariant alone does not remove the inner bound.
- Summaries: actual callee proof at the same source/profile must precede reuse.
  Pinned Kani `stub_verified` still asserts requires under the repository's
  `--no-assert-contracts`; that flag affects ordinary contracted calls, not
  replacement mode (contracts.rs and kani_macros contracts module).
- Submission: approved integrated tools and documented trust boundaries; no
  runtime/signature changes. Tool-semantic expansion, external publication and
  bounty submission each require the owner's separate decision.

## Historical fieldless-layout closeout before night N2

Run37540829027/source968c073983e0fa27112c5d8a4e10a36b05828323 establishes BOTH
generic const/mut H_align with whole-unit VF0 on unchanged official26.09: all
four checked index cases, exact old byte resources/aligned-base/i<=3 domain,
full normal/no-unwind geometry posts, leak/dead-code/refinement/integrity PASS.
Earlier generic INCONCLUSIVE results remain historical. This adds independent
abstract geometry coverage only; stock original Z layout/add still unproved,
copy UB/ownership/callback/five-unwind/full-sort4 remain open. Experimental layout
prototype and matrix were implemented separately and close at6/6 NEW runs,653s.

[Final run37544574703/sourcee472aa2](SORT4-ALIGNMENT-RESULTS.md#fieldless-layout-prototype-closeout)
provides narrow experimental evidence: original Z size0/ABIalign8, const/mutadd
for arbitrary i<=3, exact generic helper/body verification and checked calls Z/u64,
reprRust/C fieldless default/aligned layout, four intended false assertions under
ordinary premises, five unsupported original-shape absence cases. Prior Rust/C/C++
regressions pass both profiles. Metadata5/7 gates pass; absent/span raw intended
failures remain classifier INCONCLUSIVE; two new C/C++ fixtures parse-fail on both
profiles. Overall prototype acceptance INCONCLUSIVE, not accepted tool profile or
complete model-soundness. No proof transfer from stock assumed: instantiated units
verify callee and caller together in experimental model. Full ownership/copy UB/
callback/five-unwind/universal sort4/caller composition remain open. Next harness/
annotation repair plus unchanged-patch matrix check was NOT AUTHORIZED / NOT RUN
at this historical checkpoint. Later night N1/N2 completed full acceptance
(updates above); earlier raw failures and closed historical budgets remain.
RAPx0.7.50 CLOSED/NO-GO; B/C NOT RUN; original ZST remains in adopted domain.
