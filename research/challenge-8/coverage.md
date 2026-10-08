# Challenge 8 coverage ledger

This tracks requirements, not inferred coverage from an Actions badge.
Current stop/phase: [STATUS.md](STATUS.md). Evidence and exact source/tool
identifiers: [experiment log](EXPERIMENT-LOG.md). Distinguish actual-source
proofs, bounded adapters, synthetic fixtures and prefixes of failing proofs.
No complete Challenge 8 solution is established.

OVERNIGHT-MERGE-26.10 latest full matrix: run
[37752503002](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37752503002),
proof/Actions SHA `77f50f75c4b62f30fe2b477ba64f5f01e6cf0ccb`, job113228913710,
266 seconds. Same actual source commit `cd371e035c7e573760c43bf934d53e8118ee3e7d`
and full-source SHA `85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1`;
profile official-stock-VeriFast-26.10 plus W1/M2a/copy/strict-cleanup patches.
The Actions job succeeded and all group commands/classifier controls completed;
diagnostic `INCONCLUSIVE` rows below remain open and job success is not whole-proof
acceptance. Profile includes W1+M2a+copy+strict cleanup+zero-safe usize summary+
hidden stack-address translator and explicit pinned strict kernel patch; exporter,
refiner and schema are stock. Cache use was disabled for this pending stack
admission. The source console was cold-built; VeriFast binary SHA is
`18b914ef6420d329097607c6e102fde6d3c733016ae95b9478717045513b1be9`, profile ID
`vf26.10-w1-m2-c1-cleanup-usize-stack-ubuntu22.04-v1`. No cache-hit/admission
claim is made.

Unchanged actual `merge_up`/`merge_down` again passed full source/export/decode,
refinement, body, normal/unwind, return/leak/dead-code gates (116/120 body records;
3 return and 3 leak records each). This remains conditional on positive stride,
distinct source cells and explicit C1 pointer/separate writable-option destination,
with arbitrary lawful FnMut effects/answers. Current source/F owners are preserved,
the selected current value is copied and cursors advance; callback unwind preserves
the destination option and recovers current owners. No entry snapshot, SWO, duplicate
T owner, SAFE shared-slice caller realization or general Challenge proof follows.

Every row with a predeclared classification and every fail-closed classifier
control matched its stated gate; exploratory rows below remain explicitly
INCONCLUSIVE. In the **prior run377468** artifact, completed groups included: profile smoke; ordinary normal/unwind and dead-body
baselines; native C/C++; G2 geometry (1 positive + 3 negatives), A occurrence IDs
(2), B order/stability (4); nine Rust regressions (including two intended false
assertions); 22 wrapping positives + 5 rejection/assertion controls; 9 pointer-bridge
cases; pointer-domain positive + 2 exact precondition rejections; owned-array
3 positive + 2 resource negatives; scratch-option 3 positive + 3 resource negatives;
cleanup 2 positive/frame + 6 proof rejections + 4 frontend admission rejections;
M2 tuple shape 6 admission rejections, tuple resources 1 positive + 4 negatives;
and copy model 6 positive + 6 proof negatives. HRTB 11/11 source/AST admission
certificates and fail-closed controls PASS, but all 11 proof statuses remain
INCONCLUSIVE. The callback-borrow case is INCONCLUSIVE. Concrete ZST has two terminal
reentry positives and four INCONCLUSIVE layout/access cases; the copy ZST mapping
control is INCONCLUSIVE. These rows do not broaden the positive-stride domains.

The prior run377468 cache restore was an exact hit on console `3a08722c…d68b70f1a`, profile
`aeca556c…1906e6`, producer `b04b1b6063e53d3bb543c117f5ea84d493ed01da`; the full
matrix ran on that payload, and all nine cache self-tests passed.

In run377501 the cache was a miss (no profile entry); the hosted job cold-built the
same exact console SHA `3a08722cedc2f07daf26dfde2f46b8710662028ca5924212c4d1d92d68b70f1a`
under profile `0661e3063ff6a572419f54d9fa330c54a75b2ea06b49ac41f0a61c7a67c7c33e`
and published it with producer SHA `0c6699b7700b7f2b4d474f23da8fe8ad153fd553`;
all nine cache self-tests passed. Source is pinned to commit
`cd371e035c7e573760c43bf934d53e8118ee3e7d` / SHA
`85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1`, VF26.10
`f76012fb518703b1d98e243ac4f487f16877cfcb`, nightly-2026-09-25. Profile adds the
trusted zero-safe `usize::is_multiple_of` specification plus explicit pinned strict
kernel extension; stock exporter/refiner/schema remain unchanged. The source adapter
certificate and six fail-closed controls passed, but certificate does not prove the
stdlib method body. Only `usize_multiple_adapter_formula` was PASS in that run: frame fixture failed
at exporter syntax (`frame: *u32`, missing `mut`/`const`); boundary/zero-divisor cases
ended in VeriFast `Division_by_zero`; odd-divisor false target reached
`verified/lib.rs(30,30-32)` but has no exact calibrated negative oracle and remains
INCONCLUSIVE. Keep all four outcomes INCONCLUSIVE; no concrete boundary claim.

In run377501, trace generic and `u32` entry controls passed; `trace_generic_entry_domain_negative`
reached its exact assertion and is EXPECTED_FALSE_ASSERTION. The unsafe nested tuple
constructor under the original 12-coordinate domain remains INCONCLUSIVE: 0 body
executions and dead code at the constructor, so it does not resolve return
representation. Actual bidirectional len2 remains INCONCLUSIVE at line387 after 47
body statements, leaking 14 existing tuple3/Range field and padding chunks associated
with four compiler-generated locals; the exact same-source `merge_up/down` bodies
still pass their full normal/unwind gates. Full pointer trace remains INCONCLUSIVE:
13 helper bodies pass, main has zero executions and is dead code. No whole-trace or
bidirectional proof follows from workflow success.

In run377501, other nonaccepted exploratory rows were: HRTB had 11 passing admission
certificates but all 11 proof rows INCONCLUSIVE; callback borrow is INCONCLUSIVE at
`points_to<T>(left_src, _)`; concrete ZST has four INCONCLUSIVE layout/access rows;
copy overlap/misaligned/ZST calibration rows and wrapping unsupported-count/signed-offset
rows are INCONCLUSIVE after source-line drift. These are not upgraded by successful
aggregate controls; historical run classifications remain attached to their SHAs.

Run377525 completed every selected group and aggregate classifier-control gate.
Actual `merge_up/down` again pass all source, export/decode/refinement, normal/unwind,
body, return/leak and dead-code gates (116/120 execution records, three returns and
three leak checks each). Baseline/profile smoke, G2/A/B compatibility, native C/C++,
and nine Rust regressions pass, including two exact false assertions. Cleanup is
12/12; M2 tuple-shape has the valid control plus six admission rejections, M2 tuple
resources one positive plus four exact proof rejections; owned-array is 3+2,
scratch options 3+3, pointer bridge 9/9, pointer domain 1+2. HRTB source/AST
admission certificate is 11/11 with controls, while all underlying proof rows are
INCONCLUSIVE; the four prepared HRTB rows and callback-borrow remain INCONCLUSIVE.
These component and certificate rows do not imply composed admission or proof.

The tuple return-shape ladder has 11 rows: flat pointer pair, nested pointer pairs,
and nested scalar pair each PASS with full return/leak checks (4, 10 and 6 body
records respectively). Eight rows remain INCONCLUSIVE: baseline and three matched
false-entry assertions reach uncalibrated `Cannot prove false` assertions; both
pointer-half shapes stop at `Invalid dereference` before body entry; both full G2
tuple shapes have zero body entry, failing while VeriFast verifies prelude helper
`u32_sync` (other stage exits are zero; VeriFast exits1). The ladder does not prove
the full generic nested tuple return representation.

The usize source certificate and six fail-closed controls pass, as do its adapter
formula and boundary examples (13 case-body executions, one return and one leak).
The odd-divisor false target is EXPECTED_FALSE_ASSERTION at
`verified/lib.rs(35,30-32)`. The zero-divisor false target remains INCONCLUSIVE at
its assertion (`34,30-32`); no calibrated oracle declares the reached error. The
frame case reaches VeriFast but fails before case-body entry on missing
`points_to<u32>(frame, _)` at `verified/lib.rs(30,5-6)`, so remains INCONCLUSIVE.
The trusted specification and source certificate do not prove the std method body.

All six stack-address syntax cases are INCONCLUSIVE with zero body executions.
Five report `mir_stack_addr requires exactly one unsuffixed decimal literal, no
type arguments or indices`; the high-ID probe reports its raw local ID absent.
Their classifier-control mutations pass but no syntax/admission oracle is calibrated.
The fresh normal-MIR roles certificate is complete for 14 markers and four hidden
local roles: `_53` and `_65` are tuple3 call results; `_34` and `_35` are Range
result/input. It binds source SHA `95b919b4e30ecc8ffc320fe28d7d6b1891bf13c20f42ee5579f1aba1f02230b3`,
normal MIR SHA `a8716d978e206c4bf1030a2bbe6fe305df6fb81b506578cd135b4012ce1b6211` and
decoded SHA `ee5d431dfa7908fb951eab158441b67d10dc7d4f1de5c6a448df44b38fb0c15c`;
nine role/provenance mutants are listed. However, same-input rewritten proof-AST
declaration/call/destructure/address linkage remains OPEN, exit 125, AST SHA
`b18fe7deea62068d59ab7814e3a0f476e6f0caabec78e9b8843700f4aa2ed251`. Therefore
the actual bidirectional experiment/profile is not admitted.

`bidirectional_merge_len2` remains INCONCLUSIVE. It reached 56 body executions,
including one return/leak record, and first failed at
`verified/lib.rs(330,71-73)` on `bidirectional_unwind_options(...) <==> true`.
The open proof-AST gate is an independent blocker: do not claim actual bidirectional
profile acceptance or transfer the normal-role certificate into it. G2 trace main
remains dead/zero execution with 13 helper bodies passing. Concrete ZST retains two
terminal-reentry positives and four INCONCLUSIVE layout/access rows. Copy overlap
and both misalignment controls now classify EXPECTED_REJECTION at exact primitive
preconditions; ZST mapping remains INCONCLUSIVE and its earlier source-alignment
observation is not an accepted ZST model result. Both unsupported wrapping controls
now classify EXPECTED_REJECTION after exact +5-line recalibration. Historical
run377501 INCONCLUSIVE statuses remain attached to that SHA.

In run377468, trace diagnostics were separate. Generic and concrete-u32 trace-entry probes
passed; the false-assertion target was reached at line35 but remains INCONCLUSIVE
because no exact EXPECT_ERROR oracle was declared. The nested-tuple representation
probe failed before entering its body on the implicit tuple ownership requirement.
The main G2 trace remains INCONCLUSIVE: all 13 helper bodies passed, while the main
body had zero executions and dead-code throughout. Actual `bidirectional_merge`
executed 47 body statements and stopped at line387 because its loop invariant omits
compiler-generated Range and nested tuple stack chunks; the log reports 11 return
and 14 leak records across checked bodies, not a full main-body return. Iterator,
odd branch, terminal wrapping and panic-frame composition remain open. Neither
diagnostic is promoted by the successful workflow status.

Current pointer-select phase: S4b source-linked SAFE as_mut_ptr accepted;
S5k/37624082376/source128dd5673c7796c5916017ab4afafaeea8d836b8, profile
experimental-source-linked-select-pointer-intrinsics-v2/7bb39a84 accepts two
exact intrinsic specializations (*mut *const Element and MaybeUninit<*const Element>).
6positive/10proofnegative/40admission and classifier/regressions PASS. This is a
trusted compiler intrinsic value rule plus verified SAFE adapters, not Rust intrinsic
body proof. Complete modeled value/inner/state and caller frame/thread preserved.
Actual source-linked helper full31local14BB gate/refinement/3translations PASS;
body first stops at drop_in_place57, final return/leak/normal-unwind posts NOT PROVEN.
Drop/guard/forget/assume_init unaccepted; source-linked assume read-resource hypothesis
NOT RUN (tail annotation failure S5j, RawPtr refiner/union frontend failure S5k).
No semantic boundary declared; kernel/refiner unchanged. Extension temporarily
FROZEN; S5r2/37626031885 sameprofile S5j replay accepted with exactly8
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

M3k/35574949/run37756317511: actualup/downfullPASS116/120exec preserved;
G2quartetconstructorfullPASS23exec, main134exec reachesreturnpackingthen
30stimeout—nofulltraceproof. Usize3positive/2exactnegativePASS underexplicit
trustedprimitive. Stackexpectedcommentprepfailure, ASTOPEN125; actuallen2
annotationparse andlen23matchpatternparse remainsetupfailures. Stagebase
lemmafatalnestedSwitchExprNot_found isunsupported, notcounterexample.
Continuation1348/7200,5852left. See M3l preparedcard; noadmissiontransfer.

M3l/b691c406/run37757727697: sameinputMIR→ASTlinkagePASSforboth
actualprofiles14addresses+12ASTmutants (9normalMIRmutants separately),
6exactsyntax/missingIDfrontendcontrolsPASS. Wholeaddress/permission
admission remainsseparate. Stageframe+3purecheckedlemmasfullPASS;
suffixfalseintendedreacheduncalibrated. Actual len2119exec30stimeout
afterreturn/panic;len23dst2scopeSETUP. G2quartet360exec120stimeout;
constructor/fullnegativePASS; actualup/downfullPASS. Continuation1729/7200.

M3m/de87fd91/run37759998061: stageframe+3checkedbodies+suffixnegative
fullPASS. Actual len2 mandatoryodd/guarddead-code rejection retained
(119exec); actual2/3setupfixed,151exec reachesodd-copy/normalreturn then
120stimeout onfreeinglocals. Stack7frontendcontrolsPASS andsameinput
MIR/ASTgatesPASS. Scalar/namedcontrolprepSETUPfailed beforeexport.
Z3all8controls+traceSETUPunsupported(pointer_ctorSortMismatch), no
body/targetentry, allINC—notproofnegatives. Fullup/downPASS.
Continuation2127/7200,5073left. MacrooriginclassifiercandidateNOTadmitted.
